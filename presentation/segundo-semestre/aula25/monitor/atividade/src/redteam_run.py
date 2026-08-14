"""Suíte de red team didática (prompts leves) com relatório JSON."""

from __future__ import annotations

import argparse
from typing import Any

from .common import DATA_DIR, REPORTS_DIR, ensure_offline_env, load_jsonl, write_json
from .guardrails_input import InputGuardrails
from .guardrails_output import OutputGuardrails
from .rag_pipeline import LocalRAG


SAFE_FALLBACK = {
    "answer": "Solicitação bloqueada pelos guardrails de segurança.",
    "citations": ["kb-08"],
    "confidence": 1.0,
}


def run_redteam(*, guards_on: bool = True, mode: str = "obey_injection") -> dict[str, Any]:
    ensure_offline_env()
    prompts = load_jsonl(DATA_DIR / "redteam_prompts.jsonl")
    input_guard = InputGuardrails()
    output_guard = OutputGuardrails()
    rag = LocalRAG(mode=mode)

    results: list[dict[str, Any]] = []
    blocked = 0
    attack_total = 0

    for row in prompts:
        prompt = row["prompt"]
        should_block = bool(row.get("should_block", True))
        if should_block:
            attack_total += 1

        in_res = input_guard.check(prompt)
        blocked_by_input = guards_on and (not in_res.allowed)

        if blocked_by_input:
            import json

            raw = json.dumps(SAFE_FALLBACK, ensure_ascii=False)
            out_res = output_guard.check(raw)
            was_blocked = True
            answer = SAFE_FALLBACK["answer"]
            obeyed = False
        else:
            # Com guards OFF, forçamos obediência a injeção para demonstrar o contraste.
            force = (not guards_on) and should_block
            rag_res = rag.answer(prompt, force_obey_injection=force)
            raw = rag_res.generation.raw_text
            out_res = output_guard.check(raw)
            obeyed = rag_res.generation.obeyed_injection
            answer = rag_res.generation.answer
            blocked_by_output = guards_on and (not out_res.allowed)
            was_blocked = blocked_by_input or blocked_by_output
            if blocked_by_output:
                answer = SAFE_FALLBACK["answer"]

        if should_block and was_blocked:
            blocked += 1

        results.append(
            {
                "id": row["id"],
                "category": row.get("category"),
                "should_block": should_block,
                "blocked": was_blocked,
                "input_allowed": in_res.allowed if guards_on else True,
                "input_reasons": in_res.reasons,
                "output_allowed": out_res.allowed if guards_on else True,
                "output_reasons": out_res.reasons,
                "obeyed_injection": obeyed,
                "answer_preview": answer[:160],
            }
        )

    block_rate = (blocked / attack_total) if attack_total else 1.0
    report = {
        "guards_on": guards_on,
        "mode": mode,
        "attack_total": attack_total,
        "blocked": blocked,
        "block_rate": block_rate,
        "results": results,
    }
    suffix = "on" if guards_on else "off"
    write_json(REPORTS_DIR / f"redteam_report_guards_{suffix}.json", report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Red team didático Aula 25")
    parser.add_argument("--guards", choices=["on", "off"], default="on")
    parser.add_argument("--mode", default="obey_injection")
    args = parser.parse_args()
    report = run_redteam(guards_on=args.guards == "on", mode=args.mode)
    print(
        f"guards={args.guards} block_rate={report['block_rate']:.2%} "
        f"({report['blocked']}/{report['attack_total']})"
    )


if __name__ == "__main__":
    main()
