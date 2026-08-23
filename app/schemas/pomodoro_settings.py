from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PomodoroSettingsBase(BaseModel):
    focus_duration: int = Field(default=1500, gt=0, le=10800)
    short_break_duration: int = Field(default=300, gt=0, le=3600)
    long_break_duration: int = Field(default=900, gt=0, le=7200)
    sessions_before_long_break: int = Field(default=4, gt=0, le=20)
    auto_start_focus: bool = False
    auto_start_break: bool = False


class PomodoroSettingsCreate(PomodoroSettingsBase):
    pass


class PomodoroSettingsUpdate(BaseModel):
    focus_duration: int | None = Field(None, gt=0, le=10800)
    short_break_duration: int | None = Field(None, gt=0, le=3600)
    long_break_duration: int | None = Field(None, gt=0, le=7200)
    sessions_before_long_break: int | None = Field(None, gt=0, le=20)
    auto_start_focus: bool | None = None
    auto_start_break: bool | None = None


class PomodoroSettingsResponse(PomodoroSettingsBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
