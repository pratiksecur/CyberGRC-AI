from typing import Optional

from pydantic import BaseModel


class CriticalRemediationResponse(BaseModel):
    findingTitle: str
    findingSeverity: str

    actionTitle: str
    assigneeName: str

    priority: str
    status: str

    dueDate: str


class DashboardResponse(BaseModel):
    totalRisks: int
    criticalRisks: int

    controls: int
    activeControls: int

    audits: int

    compliance: int
    securityHealth: int

    totalFindings: int
    openFindings: int
    criticalFindings: int

    totalActions: int
    pendingActions: int
    overdueActions: int

    criticalRemediation: Optional[
        CriticalRemediationResponse
    ] = None