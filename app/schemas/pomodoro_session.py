from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.pomodoro_session import SessionType


class SessionCreate(BaseModel):
    session_type: SessionType = SessionType.FOCUS
    started_at: datetime
    planned_duration: int = Field(gt=0, le=180)


class SessionUpdate(BaseModel):
    ended_at: datetime | None = None
    actual_duration: int | None = Field(None, gt=0, le=180)
    completed: bool | None = None


class SessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    started_at: datetime
    session_type: SessionType
    ended_at: datetime | None
    planned_duration: int
    actual_duration: int | None
    completed: bool

class ActiveSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    started_at: datetime
    session_type: SessionType
    planned_duration: int