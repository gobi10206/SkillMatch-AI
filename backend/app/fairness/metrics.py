"""
Fairness dashboard metrics (Phase 22). Computes aggregated,
group-level statistics only — reads FairnessSurvey (isolated table)
joined against Match outcomes purely for measurement, never for
ranking. A minimum group size is enforced before a metric is stored
so small groups can't be re-identified from aggregate stats.
"""
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models.fairness import FairnessSurvey, FairnessMetric
from app.models.jobs import Match

MIN_GROUP_SIZE = 10  # groups smaller than this are excluded from published metrics


@dataclass
class SelectionRateResult:
    group_label: str
    selection_rate: float
    sample_size: int


def compute_selection_rate_parity(db: Session, period_label: str) -> list[SelectionRateResult]:
    """
    Selection-rate parity: for each self-reported group with consent,
    what fraction of their job matches scored above an interview-worthy
    threshold, compared across groups. This is a MEASUREMENT ONLY
    query — its output never feeds back into app.matching.job_matching.
    """
    threshold = 70.0
    consented = db.query(FairnessSurvey).filter(FairnessSurvey.consent_given == True).all()  # noqa: E712
    if not consented:
        return []

    # NOTE: demographic_data is an encrypted/opaque blob at rest in
    # this MVP; production would decrypt+group here. For the demo we
    # only demonstrate the isolation boundary and the metric shape.
    results: list[SelectionRateResult] = []
    total_matches = db.query(Match).count()
    if total_matches == 0:
        return []

    high_scoring = db.query(Match).filter(Match.match_score >= threshold).count()
    overall_rate = round(high_scoring / total_matches, 3)

    results.append(SelectionRateResult(
        group_label="platform_overall", selection_rate=overall_rate, sample_size=total_matches
    ))

    for r in results:
        if r.sample_size < MIN_GROUP_SIZE:
            continue
        db.add(FairnessMetric(
            metric_name="selection_rate_parity", group_label=r.group_label,
            value=r.selection_rate, sample_size=r.sample_size, computed_for_period=period_label,
        ))
    db.commit()
    return results
