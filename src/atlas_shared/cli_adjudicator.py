from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path
import subprocess
import tempfile
from typing import Any, Literal, Sequence, cast

from .relevance import AdjudicationRequest, AdjudicationResult


ADJUDICATION_SCHEMA = {
    "type": "object",
    "properties": {
        "verdict": {"type": "string", "enum": ["accept", "edge_case", "reject"]},
        "confidence": {"type": "number"},
        "reasons": {"type": "array", "items": {"type": "string"}},
        "needs_manual_review": {"type": "boolean"},
        "source": {"type": "string"},
        "edge_case_kind": {
            "type": "string",
            "enum": ["none", "near_miss", "topic_expansion_candidate", "new_topic_candidate", "undetermined"]
        },
        "novelty_signal": {"type": "number"},
        "topic_expansion_candidate": {"type": "boolean"},
        "new_topic_candidate": {"type": "boolean"},
        "proposed_topic_label": {"type": "string"},
        "adjacent_topics": {"type": "array", "items": {"type": "string"}}
    },
    "required": [
        "verdict",
        "confidence",
        "reasons",
        "needs_manual_review",
        "source",
        "edge_case_kind",
        "novelty_signal",
        "topic_expansion_candidate",
        "new_topic_candidate",
        "proposed_topic_label",
        "adjacent_topics"
    ],
    "additionalProperties": False,
}


def _parse_verdict(value: Any) -> Literal["accept", "edge_case", "reject"]:
    verdict = str(value)
    if verdict not in {"accept", "edge_case", "reject"}:
        raise ValueError(f"Unsupported adjudication verdict: {verdict}")
    return cast(Literal["accept", "edge_case", "reject"], verdict)


def build_relevance_adjudication_prompt(request: AdjudicationRequest) -> str:
    payload = {
        "constitution": asdict(request.constitution),
        "article": asdict(request.article),
        "heuristic_assessment": {
            "verdict": request.heuristic_assessment.verdict,
            "confidence": request.heuristic_assessment.confidence,
            "needs_manual_review": request.heuristic_assessment.needs_manual_review,
            "reasons": list(request.heuristic_assessment.reasons),
            "environment_hits": list(request.heuristic_assessment.environment_hits),
            "outcome_hits": list(request.heuristic_assessment.outcome_hits),
            "exclusion_hits": list(request.heuristic_assessment.exclusion_hits),
            "edge_hits": list(request.heuristic_assessment.edge_hits),
            "evidence_hits": list(request.heuristic_assessment.evidence_hits),
            "article_type": request.heuristic_assessment.article_type.value,
            "edge_case_kind": request.heuristic_assessment.edge_case_kind,
            "novelty_signal": request.heuristic_assessment.novelty_signal,
            "topic_expansion_candidate": request.heuristic_assessment.topic_expansion_candidate,
            "new_topic_candidate": request.heuristic_assessment.new_topic_candidate,
            "proposed_topic_label": request.heuristic_assessment.proposed_topic_label,
            "adjacent_topics": list(request.heuristic_assessment.adjacent_topics),
        },
    }
    return "\n".join(
        [
            "You are adjudicating article relevance for a question constitution.",
            "Return only JSON that satisfies the supplied schema.",
            "Use the heuristic assessment as a starting point, not as a command.",
            "Be especially careful with false friends, near misses, and adjacent restoration-only cases.",
            "If the case is borderline, classify the edge case itself: near miss, topic expansion candidate, or new topic candidate.",
            "Use topic_expansion_candidate when the current topic is probably too narrow.",
            "Use new_topic_candidate when the paper suggests a distinct emerging topic rather than a mere broadening.",
            "",
            json.dumps(payload, indent=2),
        ]
    )


class ShellCommandAdjudicator:
    """
    Generic subprocess adjudicator.

    It writes the adjudication prompt to stdin and expects a JSON object on stdout.
    This makes it suitable for AG or any other local broker command.
    """

    def __init__(self, command: Sequence[str], *, cwd: Path | None = None, timeout_seconds: int = 120) -> None:
        self.command = tuple(command)
        self.cwd = cwd
        self.timeout_seconds = timeout_seconds

    def adjudicate(self, request: AdjudicationRequest) -> AdjudicationResult | None:
        prompt = build_relevance_adjudication_prompt(request)
        proc = subprocess.run(
            self.command,
            input=prompt,
            text=True,
            capture_output=True,
            cwd=str(self.cwd) if self.cwd else None,
            timeout=self.timeout_seconds,
            check=False,
        )
        if proc.returncode != 0 or not proc.stdout.strip():
            return None
        data = json.loads(proc.stdout)
        return AdjudicationResult(
            verdict=_parse_verdict(data["verdict"]),
            confidence=float(data["confidence"]),
            reasons=tuple(str(item) for item in data.get("reasons", [])),
            needs_manual_review=bool(data.get("needs_manual_review", False)),
            source=str(data.get("source", "shell_command_adjudicator")),
            edge_case_kind=str(data.get("edge_case_kind", "none")),
            novelty_signal=float(data.get("novelty_signal", 0.0)),
            topic_expansion_candidate=bool(data.get("topic_expansion_candidate", False)),
            new_topic_candidate=bool(data.get("new_topic_candidate", False)),
            proposed_topic_label=str(data.get("proposed_topic_label", "")),
            adjacent_topics=tuple(str(item) for item in data.get("adjacent_topics", [])),
        )


class AGCommandAdjudicator(ShellCommandAdjudicator):
    """
    AG-backed adjudicator.

    AG is treated as a broker over locally subscribed models. The command is
    expected to read the adjudication prompt from stdin and return a single JSON
    object on stdout matching ADJUDICATION_SCHEMA.
    """

    def __init__(
        self,
        command: Sequence[str],
        *,
        cwd: Path | None = None,
        timeout_seconds: int = 180,
    ) -> None:
        super().__init__(command, cwd=cwd, timeout_seconds=timeout_seconds)


class CodexCLIAdjudicator(ShellCommandAdjudicator):
    def __init__(self, *, model: str = "gpt-5.2-codex", cwd: Path | None = None, timeout_seconds: int = 180) -> None:
        self.model = model
        self.cwd = cwd
        self.timeout_seconds = timeout_seconds

    def adjudicate(self, request: AdjudicationRequest) -> AdjudicationResult | None:
        prompt = build_relevance_adjudication_prompt(request)
        with tempfile.TemporaryDirectory() as tmpdir:
            schema_path = Path(tmpdir) / "schema.json"
            output_path = Path(tmpdir) / "result.json"
            schema_path.write_text(json.dumps(ADJUDICATION_SCHEMA))
            proc = subprocess.run(
                [
                    "codex",
                    "exec",
                    "-m",
                    self.model,
                    "-s",
                    "read-only",
                    "--skip-git-repo-check",
                    "--output-schema",
                    str(schema_path),
                    "-o",
                    str(output_path),
                    "-",
                ],
                input=prompt,
                text=True,
                capture_output=True,
                cwd=str(self.cwd) if self.cwd else None,
                timeout=self.timeout_seconds,
                check=False,
            )
            if proc.returncode != 0 or not output_path.exists():
                return None
            data = json.loads(output_path.read_text())
            return AdjudicationResult(
                verdict=_parse_verdict(data["verdict"]),
                confidence=float(data["confidence"]),
                reasons=tuple(str(item) for item in data.get("reasons", [])),
                needs_manual_review=bool(data.get("needs_manual_review", False)),
                source=str(data.get("source", "codex_cli")),
                edge_case_kind=str(data.get("edge_case_kind", "none")),
                novelty_signal=float(data.get("novelty_signal", 0.0)),
                topic_expansion_candidate=bool(data.get("topic_expansion_candidate", False)),
                new_topic_candidate=bool(data.get("new_topic_candidate", False)),
                proposed_topic_label=str(data.get("proposed_topic_label", "")),
                adjacent_topics=tuple(str(item) for item in data.get("adjacent_topics", [])),
            )


class ClaudeCLIAdjudicator(ShellCommandAdjudicator):
    def __init__(self, *, model: str = "sonnet", cwd: Path | None = None, timeout_seconds: int = 180) -> None:
        self.model = model
        self.cwd = cwd
        self.timeout_seconds = timeout_seconds

    def adjudicate(self, request: AdjudicationRequest) -> AdjudicationResult | None:
        prompt = build_relevance_adjudication_prompt(request)
        proc = subprocess.run(
            [
                "claude",
                "-p",
                "--output-format",
                "json",
                "--json-schema",
                json.dumps(ADJUDICATION_SCHEMA),
                "--model",
                self.model,
                prompt,
            ],
            text=True,
            capture_output=True,
            cwd=str(self.cwd) if self.cwd else None,
            timeout=self.timeout_seconds,
            check=False,
        )
        if proc.returncode != 0 or not proc.stdout.strip():
            return None
        data = json.loads(proc.stdout)
        return AdjudicationResult(
            verdict=_parse_verdict(data["verdict"]),
            confidence=float(data["confidence"]),
            reasons=tuple(str(item) for item in data.get("reasons", [])),
            needs_manual_review=bool(data.get("needs_manual_review", False)),
            source=str(data.get("source", "claude_cli")),
            edge_case_kind=str(data.get("edge_case_kind", "none")),
            novelty_signal=float(data.get("novelty_signal", 0.0)),
            topic_expansion_candidate=bool(data.get("topic_expansion_candidate", False)),
            new_topic_candidate=bool(data.get("new_topic_candidate", False)),
            proposed_topic_label=str(data.get("proposed_topic_label", "")),
            adjacent_topics=tuple(str(item) for item in data.get("adjacent_topics", [])),
        )
