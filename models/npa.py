from pydantic import BaseModel
from datetime import datetime

# Npa question answer model

class Npa(BaseModel):
    date: datetime
    chart_type: str
    name: str
    overdue_days: int
    outstanding_amount: int
    recovery_amount: int

