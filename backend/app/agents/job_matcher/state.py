from typing import TypedDict


class JobMatcherState(TypedDict, total=False):
    user_id: int
    user_profile: dict
    category_ids: list[str]
    job_details: list[dict]
    match_results: list[dict]
    ranked_results: list[dict]
    report_id: int
