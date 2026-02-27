"""aumai-smartgram quickstart example.

Demonstrates five common usage patterns for the aumai-smartgram library.
Run directly to verify your installation:

    python examples/quickstart.py

DISCLAIMER: This tool is an administrative aid. Verify all information with
local gram panchayat officials. All decisions must follow official Panchayati
Raj guidelines and be approved through proper administrative channels.

All demo data is fictional and for illustration purposes only.
"""

from __future__ import annotations

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
    ServiceCategory,
    ServiceRequest,
)

_DISCLAIMER = (
    "\nNOTE: This tool is an administrative aid. Verify all information with "
    "local gram panchayat officials.\n"
)


# ---------------------------------------------------------------------------
# Demo 1: Register a gram panchayat and query basic statistics
# ---------------------------------------------------------------------------


def demo_panchayat_registry() -> None:
    """Register gram panchayats and query them by district, state, and density.

    PanchayatRegistry is an in-memory store. In production it would be backed
    by a database or an e-Gram Swaraj API client.
    """
    print("=== Demo 1: Panchayat Registry ===")

    registry = PanchayatRegistry()

    panchayats = [
        GramPanchayat(
            panchayat_id="GP-MH-PUN-001",
            name="Shivajinagar Gram Panchayat",
            block="Haveli",
            district="Pune",
            state="Maharashtra",
            population=4500,
            households=890,
            area_sq_km=12.5,
        ),
        GramPanchayat(
            panchayat_id="GP-MH-PUN-002",
            name="Khed Gram Panchayat",
            block="Khed",
            district="Pune",
            state="Maharashtra",
            population=3200,
            households=640,
            area_sq_km=8.0,
        ),
        GramPanchayat(
            panchayat_id="GP-RJ-JDP-001",
            name="Mandore Gram Panchayat",
            block="Mandore",
            district="Jodhpur",
            state="Rajasthan",
            population=6100,
            households=1150,
            area_sq_km=22.0,
        ),
    ]

    for panchayat in panchayats:
        registry.register(panchayat)

    print(f"Total registered panchayats: {len(registry.all_panchayats())}")

    # Lookup by ID
    found = registry.get("GP-MH-PUN-001")
    if found:
        density = registry.population_density(found.panchayat_id)
        print(f"\nLookup GP-MH-PUN-001:")
        print(f"  Name:       {found.name}")
        print(f"  District:   {found.district}, {found.state}")
        print(f"  Population: {found.population:,}")
        print(f"  Density:    {density} persons/sq km")

    # Search by district
    pune_panchayats = registry.search_by_district("Pune")
    print(f"\nPanchayats in Pune district: {len(pune_panchayats)}")
    for p in pune_panchayats:
        print(f"  - {p.name} ({p.panchayat_id})")

    print(_DISCLAIMER)


# ---------------------------------------------------------------------------
# Demo 2: Track service requests
# ---------------------------------------------------------------------------


def demo_service_tracker() -> None:
    """Create, track, and resolve citizen service requests.

    ServiceTracker manages requests by status and provides resolution
    rate analytics per panchayat.
    """
    print("=== Demo 2: Service Request Tracker ===")

    tracker = ServiceTracker()

    requests = [
        ServiceRequest(
            request_id="SR-2024-001",
            panchayat_id="GP-MH-PUN-001",
            category=ServiceCategory.WATER,
            description="Handpump at ward 3 non-functional since June 2024",
            submitted_date="2024-06-10",
            priority=1,
        ),
        ServiceRequest(
            request_id="SR-2024-002",
            panchayat_id="GP-MH-PUN-001",
            category=ServiceCategory.ROADS,
            description="Pothole on main road near school requires repair",
            submitted_date="2024-06-15",
            priority=2,
        ),
        ServiceRequest(
            request_id="SR-2024-003",
            panchayat_id="GP-MH-PUN-001",
            category=ServiceCategory.SANITATION,
            description="Open drain near community centre needs attention",
            submitted_date="2024-06-18",
            priority=3,
        ),
    ]

    for request in requests:
        tracker.create(request)

    # List pending requests (sorted by priority, highest first)
    pending = tracker.get_pending(panchayat_id="GP-MH-PUN-001")
    print(f"Pending requests for GP-MH-PUN-001: {len(pending)}")
    for req in pending:
        print(f"  [P{req.priority}] {req.request_id}: {req.category.value} - {req.description[:55]}")

    # Resolve one request
    tracker.update_status("SR-2024-001", status="resolved", resolved_date="2024-06-25")

    # Resolution analytics
    rate = tracker.resolution_rate("GP-MH-PUN-001")
    stats = tracker.category_stats("GP-MH-PUN-001")
    print(f"\nResolution rate: {rate}%")
    print(f"Requests by category: {stats}")

    print(_DISCLAIMER)


# ---------------------------------------------------------------------------
# Demo 3: Budget utilisation analysis
# ---------------------------------------------------------------------------


def demo_budget_analyzer() -> None:
    """Analyse scheme-wise budget utilisation and identify reallocation opportunities.

    BudgetAnalyzer flags under-utilised schemes and generates plain-text
    recommendations for redistribution of unspent funds.
    """
    print("=== Demo 3: Budget Utilization Analysis ===")

    panchayat_id = "GP-MH-PUN-001"
    year = "2024-25"

    analyzer = BudgetAnalyzer()

    allocations = [
        BudgetAllocation(
            panchayat_id=panchayat_id,
            financial_year=year,
            scheme_name="MGNREGA",
            allocated_amount=500_000.0,
            utilized_amount=320_000.0,
        ),
        BudgetAllocation(
            panchayat_id=panchayat_id,
            financial_year=year,
            scheme_name="Jal Jeevan Mission",
            allocated_amount=800_000.0,
            utilized_amount=760_000.0,
        ),
        BudgetAllocation(
            panchayat_id=panchayat_id,
            financial_year=year,
            scheme_name="PMAY-Gramin",
            allocated_amount=300_000.0,
            utilized_amount=90_000.0,
        ),
        BudgetAllocation(
            panchayat_id=panchayat_id,
            financial_year=year,
            scheme_name="Swachh Bharat Mission (Gramin)",
            allocated_amount=150_000.0,
            utilized_amount=148_000.0,
        ),
    ]

    for allocation in allocations:
        analyzer.add(allocation)

    total_allocated = analyzer.total_allocation(panchayat_id, year)
    total_utilized = analyzer.total_utilized(panchayat_id, year)
    overall_pct = (total_utilized / total_allocated * 100) if total_allocated else 0

    print(f"Budget summary for {panchayat_id} | FY {year}")
    print(f"  Total allocated: Rs {total_allocated:,.0f}")
    print(f"  Total utilized:  Rs {total_utilized:,.0f} ({overall_pct:.1f}%)")

    print("\nScheme-wise utilization:")
    for scheme, pct in analyzer.utilization_by_scheme(panchayat_id, year).items():
        flag = "  LOW" if pct < 50 else "   OK"
        print(f"  {scheme:<38s} {pct:>6.1f}%  {flag}")

    recs = analyzer.recommend_reallocation(panchayat_id, year)
    if recs:
        print("\nReallocation recommendations:")
        for rec in recs:
            print(f"  - {rec}")

    print(_DISCLAIMER)


# ---------------------------------------------------------------------------
# Demo 4: Meeting records and action item tracking
# ---------------------------------------------------------------------------


def demo_meeting_manager() -> None:
    """Record gram sabha meetings and extract consolidated action items.

    MeetingManager stores decisions and follow-up actions so nothing
    falls through after a gram sabha session.
    """
    print("=== Demo 4: Meeting Manager ===")

    manager = MeetingManager()

    meetings = [
        MeetingRecord(
            panchayat_id="GP-MH-PUN-001",
            date="2024-07-15",
            attendees_count=58,
            agenda_items=["Water supply review", "MGNREGA work allocation"],
            decisions=["Approve handpump repair tender for ward 3"],
            action_items=[
                "Junior Engineer to inspect handpump by 2024-07-20",
                "Submit MGNREGA work demand to block office by 2024-07-31",
            ],
        ),
        MeetingRecord(
            panchayat_id="GP-MH-PUN-001",
            date="2024-08-10",
            attendees_count=44,
            agenda_items=["Road repair status", "Sanitation scheme update"],
            decisions=["Contract awarded to registered contractor for road repair"],
            action_items=[
                "Contractor to begin work by 2024-08-20",
                "Gram Rozgar Sevak to update job cards by 2024-08-15",
            ],
        ),
    ]

    for meeting in meetings:
        manager.record(meeting)

    count = manager.meeting_count("GP-MH-PUN-001")
    print(f"Recorded meetings for GP-MH-PUN-001: {count}")

    all_action_items = manager.all_action_items("GP-MH-PUN-001")
    print(f"\nAll pending action items ({len(all_action_items)} total):")
    for item in all_action_items:
        print(f"  - {item}")

    print(_DISCLAIMER)


# ---------------------------------------------------------------------------
# Demo 5: Government scheme lookup
# ---------------------------------------------------------------------------


def demo_scheme_mapper() -> None:
    """Look up eligible central government schemes for a panchayat.

    SchemeMapper ships with 15 built-in schemes and supports keyword
    search. In a full integration this data would be refreshed from the
    ministry's scheme portal.
    """
    print("=== Demo 5: Government Scheme Lookup ===")

    mapper = SchemeMapper()

    # Keyword search for water-related schemes
    water_schemes = mapper.search("water")
    print(f"Water-related schemes ({len(water_schemes)} found):")
    for scheme in water_schemes:
        print(f"  - {scheme.name}")
        print(f"    Ministry: {scheme.ministry}")
        print(f"    {scheme.description}")
        print()

    # Find schemes eligible for a specific panchayat
    panchayat = GramPanchayat(
        panchayat_id="GP-MH-PUN-001",
        name="Shivajinagar Gram Panchayat",
        block="Haveli",
        district="Pune",
        state="Maharashtra",
        population=4500,
        households=890,
        area_sq_km=12.5,
    )

    eligible = mapper.find_eligible(panchayat)
    print(f"Eligible schemes for {panchayat.name}: {len(eligible)}")
    for scheme in eligible:
        print(f"  - {scheme.name} ({scheme.allocation_type})")

    print(_DISCLAIMER)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    """Run all aumai-smartgram quickstart demos."""
    print("aumai-smartgram quickstart")
    print("=" * 55)
    print()
    demo_panchayat_registry()
    demo_service_tracker()
    demo_budget_analyzer()
    demo_meeting_manager()
    demo_scheme_mapper()
    print("All demos complete.")


if __name__ == "__main__":
    main()
