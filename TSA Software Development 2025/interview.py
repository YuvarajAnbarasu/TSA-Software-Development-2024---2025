from interview_ai import (
    load_interview_model as _load_model,
    get_interview_feedback as _get_feedback,
    analyze_live_interview as _analyze_interview
)

def load_interview_model():
    #Wrap the function from interview_ai.
    _load_model()

def get_interview_feedback_from_live():
    #Trigger the live interview (camera + mic) and return feedback string.
    return _get_feedback()
