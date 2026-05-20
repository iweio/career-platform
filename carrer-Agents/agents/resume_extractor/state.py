from typing import TypedDict

class CareerPlanningState(TypedDict):
    input_text: str
    file_path: str
    image_path: str
    extracted_text: str
    file_text: str
    ocr_content: str
    merged_text: str
    user_profile: dict
    completeness_flags: dict
    missing_fields: list
    next_question: str
    supplement_text: str
    supplement_count: int
    analysis: dict
