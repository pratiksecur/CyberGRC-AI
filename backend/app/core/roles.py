from enum import Enum


class UserRole(str, Enum):
    ADMIN = "Admin"
    EMPLOYEE = "Employee"
    GRC_MANAGER = "GRC Manager"
    RISK_ANALYST = "Risk Analyst"
    AUDITOR = "Auditor"