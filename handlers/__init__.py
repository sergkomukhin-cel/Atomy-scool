# Импортируем все обработчики для удобного доступа
from .tracker_handlers import (
    handle_tracker,
    handle_reading, handle_reading_confirmation,
    handle_video, handle_video_confirmation,
    handle_product, handle_product_confirmation,
    handle_meeting, handle_meeting_confirmation,
    handle_call, handle_call_confirmation,
    cancel,
    AWAITING_READING_CONFIRMATION, AWAITING_VIDEO_CONFIRMATION,
    AWAITING_PRODUCT_CONFIRMATION, AWAITING_MEETING_CONFIRMATION,
    AWAITING_CALL_CONFIRMATION
)

from .steps_handlers import handle_steps, handle_step_detail
from .education_handlers import handle_education, handle_webinar_schedule
from .mentor_handlers import handle_mentor, handle_team_progress

__all__ = [
    'handle_tracker',
    'handle_reading', 'handle_reading_confirmation',
    'handle_video', 'handle_video_confirmation',
    'handle_product', 'handle_product_confirmation',
    'handle_meeting', 'handle_meeting_confirmation',
    'handle_call', 'handle_call_confirmation',
    'cancel',
    'AWAITING_READING_CONFIRMATION', 'AWAITING_VIDEO_CONFIRMATION',
    'AWAITING_PRODUCT_CONFIRMATION', 'AWAITING_MEETING_CONFIRMATION',
    'AWAITING_CALL_CONFIRMATION',
    'handle_steps', 'handle_step_detail',
    'handle_education', 'handle_webinar_schedule',
    'handle_mentor', 'handle_team_progress'
]