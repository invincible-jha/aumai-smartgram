"""CLI entry point for aumai-smartgram."""

from __future__ import annotations

import json

import click

from aumai_smartgram.core import BudgetAnalyzer, MeetingManager, PanchayatRegistry, SchemeMapper, ServiceTracker
from aumai_smartgram.models import BudgetAllocation, GramPanchayat, MeetingRecord, ServiceCategory, ServiceRequest

_GOVERNANCE_DISCLAIMER = (
    "\nThis tool provides AI-assisted governance analysis only. "
    "All decisions must follow official Panchayati Raj guidelines and be approved through proper administrative channels.\n"
)


@click.group()
@click.version_option()
def cli() -> None:
    """AumAI SmartGram - Gram panchayat AI assistant."""


@cli.command()
@click.option("--input", "input_file", required=True, type=click.Path(exists=True), help="Panchayat JSON file")
def register(input_file: str) -> None:
    """Register a gram panchayat."""
    try:
        with open(input_file) as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        click.echo(f"Error reading file '{input_file}': {exc}", err=True)
        raise SystemExit(1) from exc
    panchayat = GramPanchayat.model_validate(data)
    registry = PanchayatRegistry()
    registry.register(panchayat)
    click.echo(f"Registered: {panchayat.name} ({panchayat.panchayat_id})")
    click.echo(f"  Block: {panchayat.block}, District: {panchayat.district}, State: {panchayat.state}")
    click.echo(f"  Population: {panchayat.population:,} | Households: {panchayat.households:,}")
    density = panchayat.population / panchayat.area_sq_km if panchayat.area_sq_km > 0 else 0
    click.echo(f"  Population density: {density:.0f}/sq km")
    click.echo(_GOVERNANCE_DISCLAIMER)


@cli.command()
@click.option("--create", "create_file", type=click.Path(exists=True), help="Create from JSON file")
@click.option("--resolve", "resolve_id", help="Resolve a request by ID")
@click.option("--panchayat", help="Filter by panchayat ID")
@click.option("--status", is_flag=True, help="Show pending requests")
def service(create_file: str | None, resolve_id: str | None, panchayat: str | None, status: bool) -> None:
    """Manage service requests."""
    tracker = ServiceTracker()

    if create_file:
        try:
            with open(create_file) as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError) as exc:
            click.echo(f"Error reading file '{create_file}': {exc}", err=True)
            raise SystemExit(1) from exc
        req = ServiceRequest.model_validate(data)
        tracker.create(req)
        click.echo(f"Created service request: {req.request_id} ({req.category.value})")
        click.echo(f"  Priority: {req.priority} | Status: {req.status}")
    elif resolve_id:
        click.echo(f"Resolved request: {resolve_id}")
    elif status:
        pending = tracker.get_pending(panchayat)
        click.echo(f"Pending requests: {len(pending)}")
        for r in pending:
            click.echo(f"  [{r.priority}] {r.request_id}: {r.category.value} - {r.description[:60]}")
    else:
        click.echo("Use --create, --resolve, or --status")
    click.echo(_GOVERNANCE_DISCLAIMER)


@cli.command()
@click.option("--input", "input_file", required=True, type=click.Path(exists=True), help="Budget JSON file")
@click.option("--panchayat", required=True, help="Panchayat ID")
@click.option("--year", required=True, help="Financial year (e.g., 2024-25)")
def budget(input_file: str, panchayat: str, year: str) -> None:
    """Analyze budget utilization."""
    try:
        with open(input_file) as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        click.echo(f"Error reading file '{input_file}': {exc}", err=True)
        raise SystemExit(1) from exc

    analyzer = BudgetAnalyzer()
    for item in data:
        analyzer.add(BudgetAllocation.model_validate(item))

    total_alloc = analyzer.total_allocation(panchayat, year)
    total_used = analyzer.total_utilized(panchayat, year)
    overall_pct = (total_used / total_alloc * 100) if total_alloc > 0 else 0

    click.echo(f"\nBudget Analysis: {panchayat} | FY {year}")
    click.echo(f"{'='*55}")
    click.echo(f"Total allocated: Rs {total_alloc:,.0f}")
    click.echo(f"Total utilized:  Rs {total_used:,.0f} ({overall_pct:.1f}%)\n")

    by_scheme = analyzer.utilization_by_scheme(panchayat, year)
    click.echo(f"{'Scheme':<25s} {'Utilization':>12s}")
    click.echo("-" * 40)
    for scheme, pct in by_scheme.items():
        marker = "!!" if pct < 50 else "OK"
        click.echo(f"{scheme:<25s} {pct:>10.1f}%  {marker}")

    recs = analyzer.recommend_reallocation(panchayat, year)
    if recs:
        click.echo("\nRecommendations:")
        for rec in recs:
            click.echo(f"  - {rec}")
    click.echo(_GOVERNANCE_DISCLAIMER)


@cli.command()
@click.option("--panchayat", help="Panchayat ID")
@click.option("--search", "query", help="Search schemes by keyword")
def schemes(panchayat: str | None, query: str | None) -> None:
    """Find eligible government schemes."""
    mapper = SchemeMapper()

    if query:
        results = mapper.search(query)
    else:
        results = mapper.all_schemes()

    click.echo(f"\n{len(results)} scheme(s) found:\n")
    for s in results:
        click.echo(f"  {s.name}")
        click.echo(f"  Ministry: {s.ministry}")
        click.echo(f"  {s.description}")
        click.echo()
    click.echo(_GOVERNANCE_DISCLAIMER)


main = cli

if __name__ == "__main__":
    cli()
