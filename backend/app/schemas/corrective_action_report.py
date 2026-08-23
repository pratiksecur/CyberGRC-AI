from datetime import date, datetime

from pydantic import BaseModel


class CorrectiveActionReportSummary(BaseModel):
    total_actions: int

    open_actions: int

    in_progress_actions: int

    completed_actions: int

    closed_actions: int

    overdue_actions: int

    critical_actions: int

    high_actions: int


class CorrectiveActionReportItem(BaseModel):
    id: int

    finding_id: int
    finding_title: str

    assigned_to: int
    assignee_name: str

    title: str
    description: str

    priority: str
    status: str

    due_date: date
    completed_at: date | None

    comments: str | None

    created_at: datetime
    updated_at: datetime

    overdue: bool


class CorrectiveActionReportResponse(BaseModel):
    summary: CorrectiveActionReportSummary

    actions: list[CorrectiveActionReportItem]