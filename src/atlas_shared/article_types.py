from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Mapping, Sequence


NEGATED_TYPE_SIGNAL_RE = re.compile(
    r"\b(?:no|not|without|lacks?|lacked|lacking|absence of|does not|do not|did not|rather than)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class ArticleTypeDecision:
    value: str
    confidence: float
    source: str
    evidence: tuple[str, ...] = ()


ARTICLE_TYPE_SECTION_HEADINGS: tuple[str, ...] = (
    "abstract",
    "introduction",
    "background",
    "method",
    "methods",
    "methodology",
    "materials and methods",
    "participants",
    "results",
    "findings",
    "discussion",
    "conclusion",
    "conclusions",
    "references",
)


def clean_article_type_text(text: str) -> str:
    """Remove extraction payload noise without destroying section boundaries."""
    cleaned = re.sub(r"!\[[^\]]*\]\(data:image/[^)]*\)", " [embedded image removed] ", text, flags=re.IGNORECASE)
    cleaned = re.sub(r"data:image/[A-Za-z0-9+/=;,:.-]{200,}", " [embedded image removed] ", cleaned)
    cleaned = re.sub(r"[A-Za-z0-9+/=]{500,}", " [long encoded payload removed] ", cleaned)
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def _extract_headings(text: str, *, limit: int = 80) -> tuple[str, ...]:
    headings: list[str] = []
    seen: set[str] = set()
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or len(stripped) > 160:
            continue
        label = re.sub(r"^#+\s*", "", stripped).strip()
        label = re.sub(r"^[0-9.\s]+", "", label).strip()
        normalized = label.lower()
        if not label or "data:image" in normalized:
            continue
        if stripped.startswith("#") or normalized in ARTICLE_TYPE_SECTION_HEADINGS:
            if label not in seen:
                headings.append(label)
                seen.add(label)
        if len(headings) >= limit:
            break
    return tuple(headings)


def extract_article_type_section(text: str, headings: Sequence[str], *, max_chars: int = 6000) -> str:
    """Extract a named section from paper text if the heading is visible."""
    if not text.strip():
        return ""
    heading_alt = "|".join(re.escape(h) for h in headings)
    stop_alt = "|".join(re.escape(h) for h in ARTICLE_TYPE_SECTION_HEADINGS)
    pattern = re.compile(
        rf"(?ims)^[ \t]*(?:#+[ \t]*)?(?:[0-9.]+[ \t]*)?(?:{heading_alt})\b[ \t:.-]*\n"
        rf"(.*?)(?=^[ \t]*(?:#+[ \t]*)?(?:[0-9.]+[ \t]*)?(?:{stop_alt})\b[ \t:.-]*\n|\Z)"
    )
    match = pattern.search(text)
    if not match:
        return ""
    return clean_article_type_text(match.group(1))[:max_chars]


def build_article_type_surface(
    text: str,
    *,
    title: str = "",
    abstract: str = "",
    keywords: Sequence[str] = (),
) -> dict[str, object]:
    """Build the canonical text surface used for heuristic article typing.

    The surface deliberately samples the article's type-bearing parts instead
    of trusting a title/abstract-only or front-slice-only shortcut.
    """
    clean = clean_article_type_text(text)
    sections = {
        "abstract": abstract.strip() or extract_article_type_section(clean, ("abstract",), max_chars=5000),
        "introduction": extract_article_type_section(clean, ("introduction", "background"), max_chars=6000),
        "methods": extract_article_type_section(
            clean,
            ("method", "methods", "methodology", "materials and methods", "participants"),
            max_chars=7000,
        ),
        "results": extract_article_type_section(clean, ("result", "results", "findings"), max_chars=5000),
        "discussion": extract_article_type_section(clean, ("discussion", "conclusion", "conclusions"), max_chars=6000),
    }
    headings = _extract_headings(clean)
    first_text = clean[:6000]
    later_text = clean[6000:30000]
    parts: list[str] = []
    if title.strip():
        parts.append(f"TITLE: {title.strip()}")
    if keywords:
        parts.append("KEYWORDS: " + "; ".join(str(item).strip() for item in keywords if str(item).strip()))
    if headings:
        parts.append("HEADINGS: " + " | ".join(headings[:60]))
    for label, value in (
        ("ABSTRACT", sections["abstract"]),
        ("INTRODUCTION", sections["introduction"]),
        ("METHODS", sections["methods"]),
        ("RESULTS", sections["results"]),
        ("DISCUSSION", sections["discussion"]),
    ):
        if str(value).strip():
            parts.append(f"{label}: {value}")
    if first_text.strip():
        parts.append("FRONT_SAMPLE: " + first_text)
    if later_text.strip():
        parts.append("LATER_SAMPLE: " + later_text)
    classifier_text = "\n\n".join(parts)
    return {
        "classifier_text": classifier_text,
        "headings": headings,
        "sections": sections,
        "clean_chars": len(clean),
        "raw_chars": len(text),
    }


TYPE_SIGNAL_PATTERNS: dict[str, tuple[str, ...]] = {
    "empirical": (
        r"\bparticipants?\b",
        r"\bsubjects?\b",
        r"\bn\s*=\s*\d+\b",
        r"\bexperiment(?:al)?\b",
        r"\brandomi[sz]ed\b",
        r"\banova\b",
        r"\bregression\b",
        r"\bp\s*[<=>]\s*\.?\d+\b",
        r"\bdependent variable\b",
        r"\bmeasured\b",
        r"\bsurvey\b",
        r"\bquestionnaire\b",
    ),
    "review": (
        r"\bsystematic review\b",
        r"\bliterature review\b",
        r"\bnarrative review\b",
        r"\bmeta[- ]analysis\b",
        r"\bscoping review\b",
        r"\bprisma\b",
        r"\binclusion criteria\b",
        r"\bexclusion criteria\b",
        r"\bliterature search\b",
    ),
    "theory": (
        r"\btheoretical\b",
        r"\bconceptual framework\b",
        r"\bframework for\b",
        r"\bwe argue\b",
        r"\bwe propose\b",
        r"\bwe develop\b",
        r"\bmodel of\b",
        r"\btypology\b",
        r"\bconceptual model\b",
    ),
    "methods": (
        r"\bmethod(?:s|ological)? paper\b",
        r"\bprotocol\b",
        r"\bvalidation study\b",
        r"\bscale development\b",
        r"\bpsychometric\b",
        r"\binstrument\b",
        r"\bbenchmark\b",
    ),
}


def article_type_signal_profile(
    text: str,
    *,
    title: str = "",
    abstract: str = "",
    keywords: Sequence[str] = (),
    surface: Mapping[str, object] | None = None,
) -> dict[str, object]:
    """Return positive and negative type evidence for routing review."""
    surface = surface or build_article_type_surface(text, title=title, abstract=abstract, keywords=keywords)
    haystack = str(surface.get("classifier_text") or "").lower()
    raw_lower = text[:50000].lower()
    image_noise = raw_lower.count("data:image") + raw_lower.count("base64")
    sections = surface.get("sections") if isinstance(surface.get("sections"), Mapping) else {}
    headings = surface.get("headings") if isinstance(surface.get("headings"), Sequence) else ()
    profile: dict[str, object] = {
        "text_chars_examined": len(haystack),
        "clean_chars_available": int(surface.get("clean_chars") or 0),
        "section_chars": {str(k): len(str(v or "")) for k, v in dict(sections).items()},
        "heading_count": len(tuple(headings)),
        "title_present": bool(title.strip()),
        "image_noise_markers": image_noise,
        "families": {},
    }
    families: dict[str, dict[str, object]] = {}
    for family, patterns in TYPE_SIGNAL_PATTERNS.items():
        matches = []
        for pattern in patterns:
            for match in re.finditer(pattern, haystack, re.IGNORECASE):
                if NEGATED_TYPE_SIGNAL_RE.search(haystack[max(0, match.start() - 80):match.start()]):
                    continue
                matches.append(pattern)
                break
        families[family] = {
            "hit_count": len(matches),
            "matched_patterns": matches,
            "negative_evidence": len(matches) == 0,
        }
    profile["families"] = families
    empirical_hits = int(families["empirical"]["hit_count"])
    nonempirical_hits = (
        int(families["review"]["hit_count"])
        + int(families["theory"]["hit_count"])
        + int(families["methods"]["hit_count"])
    )
    if empirical_hits >= 2:
        profile["routing_hint"] = "empirical_like_despite_unknown_type"
    elif nonempirical_hits >= 2 and empirical_hits == 0:
        profile["routing_hint"] = "nonempirical_like_despite_unknown_type"
    elif image_noise > 5 or len(text.strip()) < 1500:
        profile["routing_hint"] = "insufficient_clean_text_for_type"
    else:
        profile["routing_hint"] = "ambiguous_type"
    return profile


class HeuristicArticleTypeClassifier:
    """
    Lightweight cross-repo article-type classifier.

    This is intentionally smaller than AE's richer classifier. It is meant to be
    portable and dependency-light, while still being good enough for intake and
    relevance gating.
    """

    TYPE_PATTERNS: tuple[tuple[str, tuple[str, ...]], ...] = (
        (
            "meta_analysis",
            (
                r"\bmeta[- ]analysis\b",
                r"\beffect sizes?\b",
                r"\bforest plot\b",
                r"\bmeta-regress",
            ),
        ),
        (
            "systematic_review",
            (
                r"\bsystematic review\b",
                r"\bprisma\b",
                r"\binclusion criteria\b",
                r"\bexclusion criteria\b",
                r"\bliterature search\b",
            ),
        ),
        (
            "narrative_review",
            (
                r"\bnarrative review\b",
                r"\bliterature review\b",
                r"\bwe reviewed\b",
                r"\boverview of\b",
            ),
        ),
        (
            "protocol",
            (
                r"\bstudy protocol\b",
                r"\bprotocol for\b",
                r"\bregistered protocol\b",
                r"\bpre-registr",
            ),
        ),
        (
            "case_study",
            (
                r"\bcase study\b",
                r"\bsingle case\b",
                r"\bcase report\b",
            ),
        ),
        (
            "mixed_methods",
            (
                r"\bmixed methods?\b",
                r"\bqualitative and quantitative\b",
                r"\bconvergent design\b",
            ),
        ),
        (
            "qualitative_research",
            (
                r"\bqualitative\b",
                r"\binterviews?\b",
                r"\bthematic analysis\b",
                r"\bgrounded theory\b",
                r"\bethnograph",
            ),
        ),
        (
            "theoretical",
            (
                r"\btheoretical\b",
                r"\bconceptual framework\b",
                r"\bframework for\b",
                r"\bwe argue\b",
                r"\bmodel of\b",
            ),
        ),
        (
            "commentary",
            (
                r"\bcommentary\b",
                r"\beditorial\b",
                r"\bperspective\b",
                r"\bletter to the editor\b",
            ),
        ),
        (
            "empirical_research",
            (
                r"\bexperiment(?:al)?\b",
                r"\bparticipants?\b",
                r"\bn\s*=\s*\d+\b",
                r"\bp\s*[<=>]\s*\.?\d+\b",
                r"\banova\b",
                r"\bregression\b",
                r"\brandomi[sz]ed\b",
                r"\bdependent variables?\b",
                r"\bmeasured\b",
            ),
        ),
    )

    def classify(
        self,
        *,
        abstract: str = "",
        title: str = "",
        keywords: Sequence[str] = (),
        body_text: str = "",
    ) -> ArticleTypeDecision:
        source_text = "\n".join(piece for piece in (abstract, body_text) if piece)
        surface = build_article_type_surface(
            source_text,
            title=title,
            abstract=abstract,
            keywords=keywords,
        )
        signal_profile = article_type_signal_profile(
            source_text,
            title=title,
            abstract=abstract,
            keywords=keywords,
            surface=surface,
        )
        text = str(surface.get("classifier_text") or "").lower()

        if not text.strip():
            return ArticleTypeDecision(
                value="unknown",
                confidence=0.0,
                source="heuristic_classifier",
                evidence=("no title, abstract, keywords, or body text available",),
            )

        best_type = "unknown"
        best_score = 0
        evidence: list[str] = []

        for article_type, patterns in self.TYPE_PATTERNS:
            matches: list[str] = []
            for pattern in patterns:
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    if NEGATED_TYPE_SIGNAL_RE.search(text[max(0, match.start() - 80):match.start()]):
                        continue
                    matches.append(pattern)
                    break
            if len(matches) > best_score:
                best_type = article_type
                best_score = len(matches)
                evidence = [f"matched {pattern}" for pattern in matches]

        if best_type == "unknown":
            return ArticleTypeDecision(
                value="unknown",
                confidence=0.15,
                source="heuristic_classifier",
                evidence=(
                    "no article-type patterns matched",
                    f"routing_hint={signal_profile.get('routing_hint')}",
                ),
            )

        confidence = min(0.45 + 0.12 * best_score, 0.92)
        return ArticleTypeDecision(
            value=best_type,
            confidence=confidence,
            source="heuristic_classifier",
            evidence=tuple(
                evidence
                + [
                    f"routing_hint={signal_profile.get('routing_hint')}",
                    f"clean_chars={surface.get('clean_chars')}",
                ]
            ),
        )
