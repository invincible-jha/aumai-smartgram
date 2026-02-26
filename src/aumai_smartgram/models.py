"""Pydantic models for aumai-smartgram."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class PanchayatLevel(str, Enum):
    GRAM = "gram"
    BLOCK = "block"
    DISTRICT = "district"


class ServiceCategory(str, Enum):
    INFRASTRUCTURE = "infrastructure"
    WELFARE = "welfare"
    AGRICULTURE = "agriculture"
    HEALTH = "health"
    EDUCATION = "education"
    SANITATION = "sanitation"
    WATER = "water"
    ROADS = "roads"


class GramPanchayat(BaseModel):
    panchayat_id: str
    name: str
    block: str
    district: str
    state: str
    population: int = Field(gt=0)
    households: int = Field(gt=0)
    area_sq_km: float = Field(gt=0)


class ServiceRequest(BaseModel):
    request_id: str
    panchayat_id: str
    category: ServiceCategory
    description: str
    submitted_date: str
    status: str = "pending"
    priority: int = Field(default=3, ge=1, le=5)
    resolved_date: str | None = None


class BudgetAllocation(BaseModel):
    panchayat_id: str
    financial_year: str
    scheme_name: str
    allocated_amount: float = Field(ge=0)
    utilized_amount: float = Field(ge=0)

    @property
    def utilization_pct(self) -> float:
        if self.allocated_amount == 0:
            return 0.0
        return round((self.utilized_amount / self.allocated_amount) * 100, 1)


class MeetingRecord(BaseModel):
    panchayat_id: str
    date: str
    attendees_count: int = Field(ge=0)
    agenda_items: list[str] = Field(default_factory=list)
    decisions: list[str] = Field(default_factory=list)
    action_items: list[str] = Field(default_factory=list)


class SchemeInfo(BaseModel):
    name: str
    ministry: str
    description: str
    allocation_type: str = ""
    eligible_panchayats: str = "all"


__all__ = [
    "PanchayatLevel", "ServiceCategory", "GramPanchayat", "ServiceRequest",
    "BudgetAllocation", "MeetingRecord", "SchemeInfo",
]
