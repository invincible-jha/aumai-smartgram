"""Comprehensive tests for aumai-smartgram core module.

Covers:
- PanchayatRegistry
- ServiceTracker
- BudgetAnalyzer
- MeetingManager
- SchemeMapper
- Models: GramPanchayat, ServiceRequest, BudgetAllocation, MeetingRecord, SchemeInfo
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from aumai_smartgram.core import (
    BudgetAnalyzer,
    MeetingManager,
    PanchayatRegistry,
    SchemeMapper,
    ServiceTracker,
)
from aumai_smartgram.models import (
    BudgetAllocation,
    GramPanchayat,
    MeetingRecord,
    PanchayatLevel,
    SchemeInfo,
    ServiceCategory,
    ServiceRequest,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def make_panchayat(
    panchayat_id: str = "GP001",
    name: str = "Rampur",
    block: str = "Block A",
    district: str = "Sitapur",
    state: str = "Uttar Pradesh",
    population: int = 2000,
    households: int = 400,
    area_sq_km: float = 10.0,
) -> GramPanchayat:
    return GramPanchayat(
        panchayat_id=panchayat_id,
        name=name,
        block=block,
        district=district,
        state=state,
        population=population,
        households=households,
        area_sq_km=area_sq_km,
    )


def make_service_request(
    request_id: str = "REQ001",
    panchayat_id: str = "GP001",
    category: ServiceCategory = ServiceCategory.WATER,
    description: str = "Water pipeline repair",
    submitted_date: str = "2025-01-15",
    status: str = "pending",
    priority: int = 2,
) -> ServiceRequest:
    return ServiceRequest(
        request_id=request_id,
        panchayat_id=panchayat_id,
        category=category,
        description=description,
        submitted_date=submitted_date,
        status=status,
        priority=priority,
    )


def make_budget_allocation(
    panchayat_id: str = "GP001",
    financial_year: str = "2024-25",
    scheme_name: str = "MGNREGA",
    allocated_amount: float = 500000.0,
    utilized_amount: float = 300000.0,
) -> BudgetAllocation:
    return BudgetAllocation(
        panchayat_id=panchayat_id,
        financial_year=financial_year,
        scheme_name=scheme_name,
        allocated_amount=allocated_amount,
        utilized_amount=utilized_amount,
    )


def make_meeting(
    panchayat_id: str = "GP001",
    date: str = "2025-01-10",
    attendees_count: int = 20,
    agenda_items: list[str] | None = None,
    decisions: list[str] | None = None,
    action_items: list[str] | None = None,
) -> MeetingRecord:
    return MeetingRecord(
        panchayat_id=panchayat_id,
        date=date,
        attendees_count=attendees_count,
        agenda_items=agenda_items or ["Road repair", "Water supply"],
        decisions=decisions or ["Approved road repair budget"],
        action_items=action_items or ["Contact PWD department", "Survey water sources"],
    )


# ---------------------------------------------------------------------------
# GramPanchayat model tests
# ---------------------------------------------------------------------------


class TestGramPanchayatModel:
    def test_valid_creation(self) -> None:
        gp = make_panchayat()
        assert gp.panchayat_id == "GP001"
        assert gp.name == "Rampur"
        assert gp.population == 2000

    def test_population_must_be_positive(self) -> None:
        with pytest.raises(ValidationError):
            GramPanchayat(
                panchayat_id="GP001",
                name="Test",
                block="B",
                district="D",
                state="S",
                population=0,
                households=100,
                area_sq_km=5.0,
            )

    def test_households_must_be_positive(self) -> None:
        with pytest.raises(ValidationError):
            GramPanchayat(
                panchayat_id="GP001",
                name="Test",
                block="B",
                district="D",
                state="S",
                population=100,
                households=0,
                area_sq_km=5.0,
            )

    def test_area_must_be_positive(self) -> None:
        with pytest.raises(ValidationError):
            GramPanchayat(
                panchayat_id="GP001",
                name="Test",
                block="B",
                district="D",
                state="S",
                population=100,
                households=10,
                area_sq_km=0.0,
            )

    def test_state_is_stored(self) -> None:
        gp = make_panchayat(state="Maharashtra")
        assert gp.state == "Maharashtra"


# ---------------------------------------------------------------------------
# ServiceRequest model tests
# ---------------------------------------------------------------------------


class TestServiceRequestModel:
    def test_default_status_is_pending(self) -> None:
        req = ServiceRequest(
            request_id="R1",
            panchayat_id="GP001",
            category=ServiceCategory.HEALTH,
            description="Health centre repair",
            submitted_date="2025-01-01",
        )
        assert req.status == "pending"

    def test_default_priority_is_3(self) -> None:
        req = ServiceRequest(
            request_id="R1",
            panchayat_id="GP001",
            category=ServiceCategory.HEALTH,
            description="Test",
            submitted_date="2025-01-01",
        )
        assert req.priority == 3

    def test_priority_bounds(self) -> None:
        with pytest.raises(ValidationError):
            ServiceRequest(
                request_id="R1",
                panchayat_id="GP001",
                category=ServiceCategory.HEALTH,
                description="Test",
                submitted_date="2025-01-01",
                priority=0,
            )
        with pytest.raises(ValidationError):
            ServiceRequest(
                request_id="R1",
                panchayat_id="GP001",
                category=ServiceCategory.HEALTH,
                description="Test",
                submitted_date="2025-01-01",
                priority=6,
            )

    def test_resolved_date_defaults_none(self) -> None:
        req = make_service_request()
        assert req.resolved_date is None

    def test_category_enum_values(self) -> None:
        assert ServiceCategory.INFRASTRUCTURE.value == "infrastructure"
        assert ServiceCategory.WELFARE.value == "welfare"
        assert ServiceCategory.AGRICULTURE.value == "agriculture"
        assert ServiceCategory.HEALTH.value == "health"
        assert ServiceCategory.EDUCATION.value == "education"
        assert ServiceCategory.SANITATION.value == "sanitation"
        assert ServiceCategory.WATER.value == "water"
        assert ServiceCategory.ROADS.value == "roads"


# ---------------------------------------------------------------------------
# BudgetAllocation model tests
# ---------------------------------------------------------------------------


class TestBudgetAllocationModel:
    def test_utilization_pct_calculation(self) -> None:
        alloc = make_budget_allocation(allocated_amount=500000.0, utilized_amount=250000.0)
        assert alloc.utilization_pct == 50.0

    def test_utilization_pct_zero_allocated(self) -> None:
        alloc = BudgetAllocation(
            panchayat_id="GP001",
            financial_year="2024-25",
            scheme_name="Test",
            allocated_amount=0.0,
            utilized_amount=0.0,
        )
        assert alloc.utilization_pct == 0.0

    def test_full_utilization(self) -> None:
        alloc = make_budget_allocation(allocated_amount=100000.0, utilized_amount=100000.0)
        assert alloc.utilization_pct == 100.0

    def test_allocated_amount_cannot_be_negative(self) -> None:
        with pytest.raises(ValidationError):
            BudgetAllocation(
                panchayat_id="GP001",
                financial_year="2024-25",
                scheme_name="Test",
                allocated_amount=-1.0,
                utilized_amount=0.0,
            )


# ---------------------------------------------------------------------------
# PanchayatRegistry tests
# ---------------------------------------------------------------------------


class TestPanchayatRegistry:
    def test_register_and_get(self) -> None:
        registry = PanchayatRegistry()
        gp = make_panchayat()
        registry.register(gp)
        retrieved = registry.get("GP001")
        assert retrieved is not None
        assert retrieved.name == "Rampur"

    def test_get_nonexistent_returns_none(self) -> None:
        registry = PanchayatRegistry()
        assert registry.get("NONEXISTENT") is None

    def test_register_multiple(self) -> None:
        registry = PanchayatRegistry()
        gp1 = make_panchayat(panchayat_id="GP001", name="Rampur")
        gp2 = make_panchayat(panchayat_id="GP002", name="Shyampur")
        registry.register(gp1)
        registry.register(gp2)
        assert len(registry.all_panchayats()) == 2

    def test_search_by_district(self) -> None:
        registry = PanchayatRegistry()
        registry.register(make_panchayat(panchayat_id="GP001", district="Sitapur"))
        registry.register(make_panchayat(panchayat_id="GP002", district="Lucknow"))
        results = registry.search_by_district("sitapur")
        assert len(results) == 1
        assert results[0].panchayat_id == "GP001"

    def test_search_by_district_case_insensitive(self) -> None:
        registry = PanchayatRegistry()
        registry.register(make_panchayat(district="Sitapur"))
        results = registry.search_by_district("SITAPUR")
        assert len(results) == 1

    def test_search_by_state(self) -> None:
        registry = PanchayatRegistry()
        registry.register(make_panchayat(panchayat_id="GP001", state="Uttar Pradesh"))
        registry.register(make_panchayat(panchayat_id="GP002", state="Maharashtra"))
        results = registry.search_by_state("Uttar Pradesh")
        assert len(results) == 1

    def test_search_by_state_case_insensitive(self) -> None:
        registry = PanchayatRegistry()
        registry.register(make_panchayat(state="Uttar Pradesh"))
        assert len(registry.search_by_state("uttar pradesh")) == 1

    def test_population_density(self) -> None:
        registry = PanchayatRegistry()
        registry.register(make_panchayat(population=2000, area_sq_km=10.0))
        density = registry.population_density("GP001")
        assert density == 200.0

    def test_population_density_zero_area(self) -> None:
        registry = PanchayatRegistry()
        # We bypass validation by directly injecting
        gp = GramPanchayat(
            panchayat_id="GP001",
            name="Test",
            block="B",
            district="D",
            state="S",
            population=100,
            households=20,
            area_sq_km=0.001,  # near-zero
        )
        registry.register(gp)
        density = registry.population_density("GP001")
        assert density > 0

    def test_population_density_nonexistent_returns_zero(self) -> None:
        registry = PanchayatRegistry()
        assert registry.population_density("MISSING") == 0.0

    def test_all_panchayats_empty(self) -> None:
        registry = PanchayatRegistry()
        assert registry.all_panchayats() == []

    def test_register_overwrites_same_id(self) -> None:
        registry = PanchayatRegistry()
        gp1 = make_panchayat(name="Original")
        gp2 = make_panchayat(name="Updated")
        registry.register(gp1)
        registry.register(gp2)
        assert registry.get("GP001").name == "Updated"  # type: ignore[union-attr]
        assert len(registry.all_panchayats()) == 1


# ---------------------------------------------------------------------------
# ServiceTracker tests
# ---------------------------------------------------------------------------


class TestServiceTracker:
    def test_create_and_retrieve_pending(self) -> None:
        tracker = ServiceTracker()
        req = make_service_request()
        tracker.create(req)
        pending = tracker.get_pending()
        assert len(pending) == 1
        assert pending[0].request_id == "REQ001"

    def test_update_status(self) -> None:
        tracker = ServiceTracker()
        tracker.create(make_service_request())
        result = tracker.update_status("REQ001", "resolved", "2025-02-01")
        assert result is True
        assert tracker.get_pending() == []

    def test_update_status_nonexistent_returns_false(self) -> None:
        tracker = ServiceTracker()
        result = tracker.update_status("NONEXISTENT", "resolved")
        assert result is False

    def test_get_pending_filters_by_panchayat(self) -> None:
        tracker = ServiceTracker()
        tracker.create(make_service_request(request_id="REQ001", panchayat_id="GP001"))
        tracker.create(make_service_request(request_id="REQ002", panchayat_id="GP002"))
        pending_gp1 = tracker.get_pending(panchayat_id="GP001")
        assert len(pending_gp1) == 1
        assert pending_gp1[0].panchayat_id == "GP001"

    def test_get_pending_sorted_by_priority(self) -> None:
        tracker = ServiceTracker()
        tracker.create(make_service_request(request_id="REQ1", priority=3))
        tracker.create(make_service_request(request_id="REQ2", priority=1))
        tracker.create(make_service_request(request_id="REQ3", priority=2))
        pending = tracker.get_pending()
        priorities = [r.priority for r in pending]
        assert priorities == sorted(priorities)

    def test_category_stats(self) -> None:
        tracker = ServiceTracker()
        tracker.create(make_service_request(request_id="R1", category=ServiceCategory.WATER))
        tracker.create(make_service_request(request_id="R2", category=ServiceCategory.WATER))
        tracker.create(make_service_request(request_id="R3", category=ServiceCategory.HEALTH))
        stats = tracker.category_stats("GP001")
        assert stats["water"] == 2
        assert stats["health"] == 1

    def test_resolution_rate_no_requests(self) -> None:
        tracker = ServiceTracker()
        assert tracker.resolution_rate("GP001") == 0.0

    def test_resolution_rate_all_resolved(self) -> None:
        tracker = ServiceTracker()
        req = make_service_request()
        tracker.create(req)
        tracker.update_status("REQ001", "resolved")
        rate = tracker.resolution_rate("GP001")
        assert rate == 100.0

    def test_resolution_rate_partial(self) -> None:
        tracker = ServiceTracker()
        tracker.create(make_service_request(request_id="REQ001"))
        tracker.create(make_service_request(request_id="REQ002"))
        tracker.update_status("REQ001", "resolved")
        rate = tracker.resolution_rate("GP001")
        assert rate == 50.0

    def test_update_status_without_resolved_date(self) -> None:
        tracker = ServiceTracker()
        tracker.create(make_service_request())
        result = tracker.update_status("REQ001", "in_progress")
        assert result is True


# ---------------------------------------------------------------------------
# BudgetAnalyzer tests
# ---------------------------------------------------------------------------


class TestBudgetAnalyzer:
    def test_utilization_by_scheme(self) -> None:
        analyzer = BudgetAnalyzer()
        analyzer.add(make_budget_allocation(scheme_name="MGNREGA", allocated_amount=500000, utilized_amount=300000))
        by_scheme = analyzer.utilization_by_scheme("GP001", "2024-25")
        assert "MGNREGA" in by_scheme
        assert by_scheme["MGNREGA"] == 60.0

    def test_utilization_by_scheme_empty(self) -> None:
        analyzer = BudgetAnalyzer()
        result = analyzer.utilization_by_scheme("GP001", "2024-25")
        assert result == {}

    def test_under_utilized_default_threshold(self) -> None:
        analyzer = BudgetAnalyzer()
        analyzer.add(make_budget_allocation(scheme_name="SchemeA", allocated_amount=100000, utilized_amount=20000))
        analyzer.add(make_budget_allocation(scheme_name="SchemeB", allocated_amount=100000, utilized_amount=80000))
        under = analyzer.under_utilized("GP001", "2024-25")
        assert len(under) == 1
        assert under[0].scheme_name == "SchemeA"

    def test_over_utilized_default_threshold(self) -> None:
        analyzer = BudgetAnalyzer()
        analyzer.add(make_budget_allocation(scheme_name="SchemeA", allocated_amount=100000, utilized_amount=95000))
        analyzer.add(make_budget_allocation(scheme_name="SchemeB", allocated_amount=100000, utilized_amount=50000))
        over = analyzer.over_utilized("GP001", "2024-25")
        assert len(over) == 1
        assert over[0].scheme_name == "SchemeA"

    def test_total_allocation(self) -> None:
        analyzer = BudgetAnalyzer()
        analyzer.add(make_budget_allocation(scheme_name="S1", allocated_amount=200000, utilized_amount=100000))
        analyzer.add(make_budget_allocation(scheme_name="S2", allocated_amount=300000, utilized_amount=200000))
        total = analyzer.total_allocation("GP001", "2024-25")
        assert total == 500000.0

    def test_total_utilized(self) -> None:
        analyzer = BudgetAnalyzer()
        analyzer.add(make_budget_allocation(scheme_name="S1", allocated_amount=200000, utilized_amount=100000))
        analyzer.add(make_budget_allocation(scheme_name="S2", allocated_amount=300000, utilized_amount=200000))
        total = analyzer.total_utilized("GP001", "2024-25")
        assert total == 300000.0

    def test_total_allocation_wrong_year(self) -> None:
        analyzer = BudgetAnalyzer()
        analyzer.add(make_budget_allocation(financial_year="2024-25", allocated_amount=100000, utilized_amount=50000))
        assert analyzer.total_allocation("GP001", "2023-24") == 0.0

    def test_total_allocation_wrong_panchayat(self) -> None:
        analyzer = BudgetAnalyzer()
        analyzer.add(make_budget_allocation(panchayat_id="GP001", allocated_amount=100000, utilized_amount=50000))
        assert analyzer.total_allocation("GP999", "2024-25") == 0.0

    def test_recommend_reallocation(self) -> None:
        analyzer = BudgetAnalyzer()
        analyzer.add(make_budget_allocation(scheme_name="LowUse", allocated_amount=100000, utilized_amount=10000))
        recommendations = analyzer.recommend_reallocation("GP001", "2024-25")
        assert len(recommendations) == 1
        assert "LowUse" in recommendations[0]
        assert "Reallocate" in recommendations[0]

    def test_recommend_reallocation_no_under_utilized(self) -> None:
        analyzer = BudgetAnalyzer()
        analyzer.add(make_budget_allocation(allocated_amount=100000, utilized_amount=90000))
        recommendations = analyzer.recommend_reallocation("GP001", "2024-25")
        assert recommendations == []

    def test_under_utilized_custom_threshold(self) -> None:
        analyzer = BudgetAnalyzer()
        analyzer.add(make_budget_allocation(scheme_name="S1", allocated_amount=100000, utilized_amount=60000))
        # 60% utilization - under 70% threshold
        under = analyzer.under_utilized("GP001", "2024-25", threshold=70.0)
        assert len(under) == 1

    def test_multiple_panchayats_isolation(self) -> None:
        analyzer = BudgetAnalyzer()
        analyzer.add(make_budget_allocation(panchayat_id="GP001", scheme_name="S1", allocated_amount=100000, utilized_amount=50000))
        analyzer.add(BudgetAllocation(panchayat_id="GP002", financial_year="2024-25", scheme_name="S1", allocated_amount=200000, utilized_amount=180000))
        assert analyzer.total_allocation("GP001", "2024-25") == 100000.0
        assert analyzer.total_allocation("GP002", "2024-25") == 200000.0


# ---------------------------------------------------------------------------
# MeetingManager tests
# ---------------------------------------------------------------------------


class TestMeetingManager:
    def test_record_and_retrieve(self) -> None:
        manager = MeetingManager()
        meeting = make_meeting()
        manager.record(meeting)
        meetings = manager.get_meetings("GP001")
        assert len(meetings) == 1

    def test_get_meetings_empty(self) -> None:
        manager = MeetingManager()
        assert manager.get_meetings("GP001") == []

    def test_get_meetings_filters_by_panchayat(self) -> None:
        manager = MeetingManager()
        manager.record(make_meeting(panchayat_id="GP001"))
        manager.record(MeetingRecord(panchayat_id="GP002", date="2025-01-10", attendees_count=15))
        assert len(manager.get_meetings("GP001")) == 1
        assert len(manager.get_meetings("GP002")) == 1

    def test_all_action_items(self) -> None:
        manager = MeetingManager()
        manager.record(make_meeting(action_items=["Task A", "Task B"]))
        manager.record(make_meeting(date="2025-02-01", action_items=["Task C"]))
        items = manager.all_action_items("GP001")
        assert len(items) == 3
        assert "Task A" in items
        assert "Task C" in items

    def test_all_action_items_wrong_panchayat(self) -> None:
        manager = MeetingManager()
        manager.record(make_meeting(action_items=["Task A"]))
        items = manager.all_action_items("GP999")
        assert items == []

    def test_meeting_count(self) -> None:
        manager = MeetingManager()
        manager.record(make_meeting(date="2025-01-01"))
        manager.record(make_meeting(date="2025-02-01"))
        manager.record(make_meeting(date="2025-03-01"))
        assert manager.meeting_count("GP001") == 3

    def test_meeting_count_wrong_panchayat(self) -> None:
        manager = MeetingManager()
        manager.record(make_meeting())
        assert manager.meeting_count("GP999") == 0

    def test_meeting_with_empty_action_items(self) -> None:
        manager = MeetingManager()
        meeting = MeetingRecord(panchayat_id="GP001", date="2025-01-01", attendees_count=10)
        manager.record(meeting)
        items = manager.all_action_items("GP001")
        assert items == []


# ---------------------------------------------------------------------------
# SchemeMapper tests
# ---------------------------------------------------------------------------


class TestSchemeMapper:
    def test_all_schemes_count(self) -> None:
        mapper = SchemeMapper()
        schemes = mapper.all_schemes()
        assert len(schemes) == 15

    def test_find_eligible_no_panchayat(self) -> None:
        mapper = SchemeMapper()
        eligible = mapper.find_eligible(None)
        assert len(eligible) == 15

    def test_find_eligible_for_panchayat(self) -> None:
        mapper = SchemeMapper()
        gp = make_panchayat(population=2000)
        eligible = mapper.find_eligible(gp)
        assert len(eligible) > 0

    def test_find_eligible_large_population_census_towns(self) -> None:
        mapper = SchemeMapper()
        # Population > 5000 should include census_towns scheme (AMRUT 2.0)
        gp = make_panchayat(population=6000)
        eligible = mapper.find_eligible(gp)
        names = [s.name for s in eligible]
        assert "AMRUT 2.0" in names

    def test_find_eligible_small_population_no_census_towns(self) -> None:
        mapper = SchemeMapper()
        gp = make_panchayat(population=2000)
        eligible = mapper.find_eligible(gp)
        names = [s.name for s in eligible]
        assert "AMRUT 2.0" not in names

    def test_find_eligible_population_250_gets_pmgsy(self) -> None:
        mapper = SchemeMapper()
        gp = make_panchayat(population=300)
        eligible = mapper.find_eligible(gp)
        names = [s.name for s in eligible]
        assert "PMGSY" in names

    def test_find_eligible_population_below_250_no_pmgsy(self) -> None:
        mapper = SchemeMapper()
        gp = make_panchayat(population=200)
        eligible = mapper.find_eligible(gp)
        names = [s.name for s in eligible]
        assert "PMGSY" not in names

    def test_search_by_keyword(self) -> None:
        mapper = SchemeMapper()
        results = mapper.search("MGNREGA")
        assert len(results) >= 1
        assert any(s.name == "MGNREGA" for s in results)

    def test_search_by_description_keyword(self) -> None:
        mapper = SchemeMapper()
        results = mapper.search("employment")
        assert len(results) >= 1

    def test_search_case_insensitive(self) -> None:
        mapper = SchemeMapper()
        results = mapper.search("mgnrega")
        assert len(results) >= 1

    def test_search_no_results(self) -> None:
        mapper = SchemeMapper()
        results = mapper.search("xyznonexistentterm12345")
        assert results == []

    def test_all_schemes_have_ministry(self) -> None:
        mapper = SchemeMapper()
        for scheme in mapper.all_schemes():
            assert scheme.ministry != ""

    def test_all_schemes_have_description(self) -> None:
        mapper = SchemeMapper()
        for scheme in mapper.all_schemes():
            assert scheme.description != ""

    def test_jal_jeevan_mission_in_schemes(self) -> None:
        mapper = SchemeMapper()
        names = [s.name for s in mapper.all_schemes()]
        assert "Jal Jeevan Mission" in names

    def test_pm_kisan_in_schemes(self) -> None:
        mapper = SchemeMapper()
        names = [s.name for s in mapper.all_schemes()]
        assert "PM-KISAN" in names


# ---------------------------------------------------------------------------
# PanchayatLevel enum tests
# ---------------------------------------------------------------------------


class TestPanchayatLevelEnum:
    def test_gram_value(self) -> None:
        assert PanchayatLevel.GRAM.value == "gram"

    def test_block_value(self) -> None:
        assert PanchayatLevel.BLOCK.value == "block"

    def test_district_value(self) -> None:
        assert PanchayatLevel.DISTRICT.value == "district"


# ---------------------------------------------------------------------------
# SchemeInfo model tests
# ---------------------------------------------------------------------------


class TestSchemeInfoModel:
    def test_defaults(self) -> None:
        scheme = SchemeInfo(name="Test Scheme", ministry="Test Ministry", description="A test scheme")
        assert scheme.allocation_type == ""
        assert scheme.eligible_panchayats == "all"

    def test_custom_eligible_panchayats(self) -> None:
        scheme = SchemeInfo(
            name="Test",
            ministry="Test Ministry",
            description="Desc",
            eligible_panchayats="all_rural",
        )
        assert scheme.eligible_panchayats == "all_rural"


# ---------------------------------------------------------------------------
# MeetingRecord model tests
# ---------------------------------------------------------------------------


class TestMeetingRecordModel:
    def test_defaults(self) -> None:
        meeting = MeetingRecord(panchayat_id="GP001", date="2025-01-01", attendees_count=10)
        assert meeting.agenda_items == []
        assert meeting.decisions == []
        assert meeting.action_items == []

    def test_attendees_count_can_be_zero(self) -> None:
        meeting = MeetingRecord(panchayat_id="GP001", date="2025-01-01", attendees_count=0)
        assert meeting.attendees_count == 0

    def test_attendees_cannot_be_negative(self) -> None:
        with pytest.raises(ValidationError):
            MeetingRecord(panchayat_id="GP001", date="2025-01-01", attendees_count=-1)
