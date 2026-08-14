"""Guardrails de saída: PII, blocklist, schema JSON e orçamento."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any

from jsonschema import Draft202012Validator

from .common import POLICIES_DIR, load_json, load_yaml


@dataclass
class OutputGuardResult:
    allowed: bool
    reasons: list[str] = field(default_factory=list)
    parsed: dict[str, Any] | None = None
    estimated_tokens: int = 0
    estimated_cost_usd: float = 0.0


class OutputGuardrails:
    def __init__(
        self,
        policy: dict[str, Any] | None = None,
        schema: dict[str, Any] | None = None,
    ) -> None:
        self.policy = policy or load_yaml(POLICIES_DIR / "safety_policy.yaml")
        self.schema = schema or load_json(POLICIES_DIR / "output_schema.json")
        self.validator = Draft202012Validator(self.schema)
        out = self.policy.get("output", {})
        self.pii_patterns = {
            name: re.compile(pat) for name, pat in out.get("pii_patterns", {}).items()
        }
        self.blocklist = [k.lower() for k in out.get("blocklist_keywords", [])]
        self.max_tokens = int(out.get("max_output_tokens", 256))
        self.max_cost = float(out.get("max_estimated_cost_usd", 0.01))

    def check(self, raw_text: str) -> OutputGuardResult:
        reasons: list[str] = []
        parsed: dict[str, Any] | None = None

        try:
            parsed = json.loads(raw_text)
        except json.JSONDecodeError:
            reasons.append("json_invalido")

        if parsed is not None:
            errors = sorted(self.validator.iter_errors(parsed), key=lambda e: e.path)
            if errors:
                reasons.append("schema_invalido")

        for name, pattern in self.pii_patterns.items():
            if pattern.search(raw_text):
                reasons.append(f"pii:{name}")

        lower = raw_text.lower()
        for word in self.blocklist:
            if word in lower:
                reasons.append(f"blocklist:{word}")

        est_tokens = max(1, len(raw_text) // 4)
        # custo didático fixo por token
        est_cost = est_tokens * 0.00002
        if est_tokens > self.max_tokens:
            reasons.append("orcamento_tokens")
        if est_cost > self.max_cost:
            reasons.append("orcamento_custo")

        return OutputGuardResult(
            allowed=not reasons,
            reasons=sorted(set(reasons)),
            parsed=parsed if "json_invalido" not in reasons else None,
            estimated_tokens=est_tokens,
            estimated_cost_usd=round(est_cost, 6),
        )
