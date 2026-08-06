from pydantic import BaseModel


class RiskTrendResponse(BaseModel):
    month: str
    risks: int