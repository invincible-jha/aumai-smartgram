"""Core logic for aumai-smartgram."""

from __future__ import annotations

from aumai_smartgram.models import (
    BudgetAllocation, GramPanchayat, MeetingRecord, SchemeInfo, ServiceCategory, ServiceRequest,
)

_SCHEMES: list[SchemeInfo] = [
    SchemeInfo(name="MGNREGA", ministry="Ministry of Rural Development",
              description="100 days guaranteed wage employment per rural household per year.",
              allocation_type="demand-driven", eligible_panchayats="all_rural"),
    SchemeInfo(name="PMAY-Gramin", ministry="Ministry of Rural Development",
              description="Pucca house with basic amenities. Rs 1.20 lakh (plains), Rs 1.30 lakh (hilly).",
              allocation_type="unit-based", eligible_panchayats="houseless_kutcha"),
    SchemeInfo(name="Swachh Bharat Mission (Gramin)", ministry="Ministry of Jal Shakti",
              description="ODF villages. Individual household toilets and community sanitary complexes.",
              allocation_type="unit-based", eligible_panchayats="all_rural"),
    SchemeInfo(name="PMGSY", ministry="Ministry of Rural Development",
              description="All-weather road connectivity to unconnected habitations (500+ population, 250+ in hilly).",
              allocation_type="project-based", eligible_panchayats="unconnected_habitations"),
    SchemeInfo(name="National Health Mission", ministry="Ministry of Health",
              description="Health Sub-Centres, PHCs. Free medicines, diagnostics. ASHA workers.",
              allocation_type="population-based", eligible_panchayats="all"),
    SchemeInfo(name="Samagra Shiksha", ministry="Ministry of Education",
              description="Holistic education from pre-school to Class XII. School infrastructure and teacher training.",
              allocation_type="population-based", eligible_panchayats="all"),
    SchemeInfo(name="National Rural Livelihood Mission", ministry="Ministry of Rural Development",
              description="SHG formation, skill development, micro-credit. Targets poorest of poor.",
              allocation_type="demand-driven", eligible_panchayats="all_rural"),
    SchemeInfo(name="DDU-GKY", ministry="Ministry of Rural Development",
              description="Skill development and placement for rural youth aged 15-35.",
              allocation_type="demand-driven", eligible_panchayats="all_rural"),
    SchemeInfo(name="Jal Jeevan Mission", ministry="Ministry of Jal Shakti",
              description="Functional household tap connection (FHTC) to every rural household by 2024.",
              allocation_type="unit-based", eligible_panchayats="all_rural"),
    SchemeInfo(name="PM-KISAN", ministry="Ministry of Agriculture",
              description="Rs 6,000/year income support to farmer families in 3 installments.",
              allocation_type="dbt", eligible_panchayats="farming_households"),
    SchemeInfo(name="RKVY-RAFTAAR", ministry="Ministry of Agriculture",
              description="Infrastructure for agriculture and allied sectors. Agri-business promotion.",
              allocation_type="project-based", eligible_panchayats="all_rural"),
    SchemeInfo(name="ICDS/Poshan Abhiyaan", ministry="Ministry of Women & Child",
              description="Supplementary nutrition, immunization, health checkup for children 0-6 and pregnant women.",
              allocation_type="anganwadi-based", eligible_panchayats="all"),
    SchemeInfo(name="Mid-Day Meal (PM-POSHAN)", ministry="Ministry of Education",
              description="Hot cooked lunch for government school children Class I-VIII.",
              allocation_type="per-child", eligible_panchayats="all"),
    SchemeInfo(name="NSAP (National Social Assistance)", ministry="Ministry of Rural Development",
              description="Pension for elderly (IGNOAPS), widows (IGNWPS), disabled (IGNDPS).",
              allocation_type="dbt", eligible_panchayats="all_bpl"),
    SchemeInfo(name="AMRUT 2.0", ministry="Ministry of Housing",
              description="Water supply, sewerage, drainage for urban areas and census towns.",
              allocation_type="project-based", eligible_panchayats="census_towns"),
]


__all__ = [
    "PanchayatRegistry",
    "ServiceTracker",
    "BudgetAnalyzer",
    "MeetingManager",
    "SchemeMapper",
]


class PanchayatRegistry:
    def __init__(self) -> None:
        self._panchayats: dict[str, GramPanchayat] = {}

    def register(self, panchayat: GramPanchayat) -> None:
        self._panchayats[panchayat.panchayat_id] = panchayat

    def get(self, panchayat_id: str) -> GramPanchayat | None:
        return self._panchayats.get(panchayat_id)

    def search_by_district(self, district: str) -> list[GramPanchayat]:
        d = district.lower()
        return [p for p in self._panchayats.values() if d in p.district.lower()]

    def search_by_state(self, state: str) -> list[GramPanchayat]:
        s = state.lower()
        return [p for p in self._panchayats.values() if s in p.state.lower()]

    def population_density(self, panchayat_id: str) -> float:
        p = self._panchayats.get(panchayat_id)
        if p is None or p.area_sq_km == 0:
            return 0.0
        return round(p.population / p.area_sq_km, 1)

    def all_panchayats(self) -> list[GramPanchayat]:
        return list(self._panchayats.values())


class ServiceTracker:
    def __init__(self) -> None:
        self._requests: dict[str, ServiceRequest] = {}

    def create(self, request: ServiceRequest) -> None:
        self._requests[request.request_id] = request

    def update_status(self, request_id: str, status: str, resolved_date: str | None = None) -> bool:
        req = self._requests.get(request_id)
        if req is None:
            return False
        req.status = status
        if resolved_date:
            req.resolved_date = resolved_date
        return True

    def get_pending(self, panchayat_id: str | None = None) -> list[ServiceRequest]:
        results = [r for r in self._requests.values() if r.status == "pending"]
        if panchayat_id:
            results = [r for r in results if r.panchayat_id == panchayat_id]
        return sorted(results, key=lambda r: r.priority)

    def category_stats(self, panchayat_id: str) -> dict[str, int]:
        stats: dict[str, int] = {}
        for r in self._requests.values():
            if r.panchayat_id == panchayat_id:
                cat = r.category.value
                stats[cat] = stats.get(cat, 0) + 1
        return stats

    def resolution_rate(self, panchayat_id: str) -> float:
        total = sum(1 for r in self._requests.values() if r.panchayat_id == panchayat_id)
        resolved = sum(1 for r in self._requests.values() if r.panchayat_id == panchayat_id and r.status == "resolved")
        return round(resolved / total * 100, 1) if total > 0 else 0.0


class BudgetAnalyzer:
    def __init__(self) -> None:
        self._allocations: list[BudgetAllocation] = []

    def add(self, allocation: BudgetAllocation) -> None:
        self._allocations.append(allocation)

    def utilization_by_scheme(self, panchayat_id: str, year: str) -> dict[str, float]:
        result: dict[str, float] = {}
        for a in self._allocations:
            if a.panchayat_id == panchayat_id and a.financial_year == year:
                result[a.scheme_name] = a.utilization_pct
        return result

    def under_utilized(self, panchayat_id: str, year: str, threshold: float = 50.0) -> list[BudgetAllocation]:
        return [a for a in self._allocations
                if a.panchayat_id == panchayat_id and a.financial_year == year and a.utilization_pct < threshold]

    def over_utilized(self, panchayat_id: str, year: str, threshold: float = 90.0) -> list[BudgetAllocation]:
        return [a for a in self._allocations
                if a.panchayat_id == panchayat_id and a.financial_year == year and a.utilization_pct > threshold]

    def total_allocation(self, panchayat_id: str, year: str) -> float:
        return sum(a.allocated_amount for a in self._allocations if a.panchayat_id == panchayat_id and a.financial_year == year)

    def total_utilized(self, panchayat_id: str, year: str) -> float:
        return sum(a.utilized_amount for a in self._allocations if a.panchayat_id == panchayat_id and a.financial_year == year)

    def recommend_reallocation(self, panchayat_id: str, year: str) -> list[str]:
        under = self.under_utilized(panchayat_id, year)
        recommendations: list[str] = []
        for a in under:
            unused = a.allocated_amount - a.utilized_amount
            recommendations.append(
                f"Reallocate Rs {unused:,.0f} from {a.scheme_name} (only {a.utilization_pct:.0f}% utilized) to higher-need areas"
            )
        return recommendations


class MeetingManager:
    def __init__(self) -> None:
        self._meetings: list[MeetingRecord] = []

    def record(self, meeting: MeetingRecord) -> None:
        self._meetings.append(meeting)

    def get_meetings(self, panchayat_id: str) -> list[MeetingRecord]:
        return [m for m in self._meetings if m.panchayat_id == panchayat_id]

    def all_action_items(self, panchayat_id: str) -> list[str]:
        items: list[str] = []
        for m in self._meetings:
            if m.panchayat_id == panchayat_id:
                items.extend(m.action_items)
        return items

    def meeting_count(self, panchayat_id: str) -> int:
        return sum(1 for m in self._meetings if m.panchayat_id == panchayat_id)


class SchemeMapper:
    def __init__(self) -> None:
        self._schemes = list(_SCHEMES)

    def find_eligible(self, panchayat: GramPanchayat | None = None) -> list[SchemeInfo]:
        if panchayat is None:
            return list(self._schemes)
        eligible: list[SchemeInfo] = []
        for scheme in self._schemes:
            ep = scheme.eligible_panchayats
            if ep in ("all", "all_rural", "all_bpl"):
                eligible.append(scheme)
            elif ep == "farming_households":
                eligible.append(scheme)
            elif ep == "census_towns" and panchayat.population > 5000:
                eligible.append(scheme)
            elif ep == "unconnected_habitations" and panchayat.population >= 250:
                eligible.append(scheme)
            elif ep == "houseless_kutcha":
                eligible.append(scheme)
        return eligible

    def search(self, query: str) -> list[SchemeInfo]:
        q = query.lower()
        return [s for s in self._schemes if q in s.name.lower() or q in s.description.lower()]

    def all_schemes(self) -> list[SchemeInfo]:
        return list(self._schemes)
