"""Tests for aumai-smartgram CLI."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from click.testing import CliRunner

from aumai_smartgram.cli import main


def make_panchayat_json() -> dict:
    return {
        "panchayat_id": "GP001",
        "name": "Rampur",
        "block": "Block A",
        "district": "Sitapur",
        "state": "Uttar Pradesh",
        "population": 2000,
        "households": 400,
        "area_sq_km": 10.0,
    }


def make_service_request_json() -> dict:
    return {
        "request_id": "REQ001",
        "panchayat_id": "GP001",
        "category": "water",
        "description": "Pipeline repair needed at village center",
        "submitted_date": "2025-01-15",
        "priority": 2,
    }


def make_budget_json() -> list[dict]:
    return [
        {
            "panchayat_id": "GP001",
            "financial_year": "2024-25",
            "scheme_name": "MGNREGA",
            "allocated_amount": 500000,
            "utilized_amount": 200000,
        },
        {
            "panchayat_id": "GP001",
            "financial_year": "2024-25",
            "scheme_name": "PMAY-Gramin",
            "allocated_amount": 300000,
            "utilized_amount": 280000,
        },
    ]


class TestCLIVersion:
    def test_cli_version(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output

    def test_cli_help(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "SmartGram" in result.output or "panchayat" in result.output.lower()


class TestRegisterCommand:
    def test_register_valid_panchayat(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            Path("gp.json").write_text(json.dumps(make_panchayat_json()))
            result = runner.invoke(main, ["register", "--input", "gp.json"])
            assert result.exit_code == 0
            assert "Rampur" in result.output
            assert "GP001" in result.output

    def test_register_shows_population(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            Path("gp.json").write_text(json.dumps(make_panchayat_json()))
            result = runner.invoke(main, ["register", "--input", "gp.json"])
            assert "2,000" in result.output or "2000" in result.output

    def test_register_missing_file(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["register", "--input", "nonexistent.json"])
        assert result.exit_code != 0


class TestServiceCommand:
    def test_service_create(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            Path("req.json").write_text(json.dumps(make_service_request_json()))
            result = runner.invoke(main, ["service", "--create", "req.json"])
            assert result.exit_code == 0
            assert "REQ001" in result.output

    def test_service_resolve(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["service", "--resolve", "REQ001"])
        assert result.exit_code == 0
        assert "REQ001" in result.output

    def test_service_status(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["service", "--status"])
        assert result.exit_code == 0
        assert "Pending" in result.output or "pending" in result.output.lower()

    def test_service_no_options(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["service"])
        assert result.exit_code == 0
        assert "Use" in result.output


class TestBudgetCommand:
    def test_budget_analysis(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            Path("budget.json").write_text(json.dumps(make_budget_json()))
            result = runner.invoke(main, ["budget", "--input", "budget.json", "--panchayat", "GP001", "--year", "2024-25"])
            assert result.exit_code == 0
            assert "Budget Analysis" in result.output

    def test_budget_shows_utilization(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            Path("budget.json").write_text(json.dumps(make_budget_json()))
            result = runner.invoke(main, ["budget", "--input", "budget.json", "--panchayat", "GP001", "--year", "2024-25"])
            assert "MGNREGA" in result.output

    def test_budget_shows_recommendations(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            Path("budget.json").write_text(json.dumps(make_budget_json()))
            result = runner.invoke(main, ["budget", "--input", "budget.json", "--panchayat", "GP001", "--year", "2024-25"])
            # MGNREGA is at 40% utilization — should trigger recommendation
            assert "Reallocate" in result.output or "recommendation" in result.output.lower()


class TestSchemesCommand:
    def test_schemes_all(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["schemes"])
        assert result.exit_code == 0
        assert "MGNREGA" in result.output

    def test_schemes_search(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["schemes", "--search", "employment"])
        assert result.exit_code == 0

    def test_schemes_search_no_results(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["schemes", "--search", "xyznonexistent12345"])
        assert result.exit_code == 0
        assert "0 scheme" in result.output
