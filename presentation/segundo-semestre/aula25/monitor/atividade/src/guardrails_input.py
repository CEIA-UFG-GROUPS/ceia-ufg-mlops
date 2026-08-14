"""Guardrails de entrada: injeção de prompt e allowlist de ferramentas."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from .common import POLICIES_DIR, load_yaml


@dataclass
class InputGuardResult:
    allowed: bool
    reasons: list[str] = field(default_factory=list)
    matched_patterns: list[str] = field(default_factory=list)
    blocked_tools: list[str] = field(default_factory=list)


class InputGuardrails:
    def __init__(self, policy: dict[str, Any] | None = None) -> None:
        self.policy = policy or load_yaml(POLICIES_DIR / "safety_policy.yaml")
        patterns = self.policy.get("input", {}).get("injection_patterns", [])
        self._patterns = [re.compile(p) for p in patterns]
        self.blocked_tools = {
            t.lower() for t in self.policy.get("input", {}).get("blocked_tools", [])
        }
        self.allowed_tools = {
            t.lower() for t in self.policy.get("input", {}).get("allowed_tools", [])
        }

    def check(self, prompt: str) -> InputGuardResult:
        reasons: list[str] = []
        matched: list[str] = []
        blocked_found: list[str] = []

        for pattern in self._patterns:
            if pattern.search(prompt):
                matched.append(pattern.pattern)
                reasons.append("padrao_injecao")

        for tool in self.blocked_tools:
            if re.search(rf"\b{re.escape(tool)}\b", prompt, flags=re.I):
                blocked_found.append(tool)
                reasons.append(f"ferramenta_bloqueada:{tool}")

        # menção a ferramenta fora da allowlist
        tool_mentions = re.findall(r"\b([a-z_]{3,30})\b", prompt.lower())
        for token in tool_mentions:
            if token.startswith(("http_", "send_", "execute_")) and token not in self.allowed_tools:
                if token not in blocked_found:
                    blocked_found.append(token)
                    reasons.append(f"ferramenta_nao_permitida:{token}")

        allowed = not reasons
        return InputGuardResult(
            allowed=allowed,
            reasons=sorted(set(reasons)),
            matched_patterns=matched,
            blocked_tools=blocked_found,
        )
