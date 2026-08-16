from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PomodoroSettingsBase(BaseModel):
    focus_duration: int = Field(default=25, gt=0, le=180)
    short_break_duration: int = Field(default=5, gt=0, le=60)
    long_break_duration: int = Field(default=15, gt=0, le=120)
    sessions_before_long_break: int = Field(default=4, gt=0, le=20)
    auto_start_focus: bool = False
    auto_start_break: bool = False


class PomodoroSettingsCreate(PomodoroSettingsBase):
    pass


class PomodoroSettingsUpdate(BaseModel):
    focus_duration: int | None = Field(default=None, gt=0, le=180)
    short_break_duration: int | None = Field(default=None, gt=0, le=60)
    long_break_duration: int | None = Field(default=None, gt=0, le=120)
    sessions_before_long_break: int | None = Field(default=None, gt=0, le=20)
    auto_start_focus: bool | None = None
    auto_start_break: bool | None = None


class PomodoroSettingsResponse(PomodoroSettingsBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
