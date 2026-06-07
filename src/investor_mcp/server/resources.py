"""MCP resource definitions (registered on import via @mcp.resource decorators)."""

from __future__ import annotations

from .app import mcp, service, _json


@mcp.resource("investor://profile/current")
def profile_resource() -> str:
    """Current investment profile."""
    return _json(service.get_profile()["data"])


@mcp.resource("investor://accounts")
def accounts_resource() -> str:
    """Broker accounts selected for analysis."""
    return _json(service.list_accounts()["data"])


@mcp.resource("investor://portfolio/current")
def portfolio_resource() -> str:
    """Current aggregated portfolio."""
    return _json(service.get_portfolio()["data"])


@mcp.resource("investor://risks/current")
def risks_resource() -> str:
    """Current portfolio risk signals."""
    return _json(service.scan_risks()["data"])


@mcp.resource("investor://portfolio/snapshots/{snapshot_id}")
def snapshot_resource(snapshot_id: str) -> str:
    """Historical portfolio snapshot stored at sync time."""
    snapshot = service.get_snapshot(snapshot_id)
    if snapshot is None:
        return _json({"available": False, "snapshot_id": snapshot_id})
    return _json(snapshot)


@mcp.resource("investor://positions/{instrument_id}")
def position_resource(instrument_id: str) -> str:
    """Position detail for an instrument."""
    return _json(service.get_instrument({"id_type": "internal_id", "id": instrument_id})["data"])


@mcp.resource("investor://operations/{account_id}/{from_date}/{to_date}")
def operations_resource(account_id: str, from_date: str, to_date: str) -> str:
    """Operations for an account over a date range."""
    return _json(service.get_operations(from_date, to_date, [account_id])["data"])


@mcp.resource("investor://recommendations/{recommendation_id}")
def recommendation_resource(recommendation_id: str) -> str:
    """A stored recommendation."""
    recommendation = service.get_recommendation(recommendation_id)
    if recommendation is None:
        return _json({"available": False, "recommendation_id": recommendation_id})
    return _json(recommendation)


@mcp.resource("investor://reports/{report_type}/{date}", mime_type="text/markdown")
def report_resource(report_type: str, date: str) -> str:
    """A generated report in Markdown."""
    markdown = service.get_report(report_type, date)
    return markdown if markdown is not None else f"# Отчет не найден\n\n{report_type} / {date}"


@mcp.resource("investor://research/{instrument_id}/{date}", mime_type="text/markdown")
def research_resource(instrument_id: str, date: str) -> str:
    """An instrument research draft in Markdown."""
    result = service.research_instrument({"id_type": "internal_id", "id": instrument_id})
    if not result["ok"]:
        return f"# Инструмент не найден\n\n{instrument_id}"
    return result["data"].get("markdown", "# Исследование недоступно")


@mcp.resource("investor://schema/domain")
def domain_schema_resource() -> str:
    """Description of the normalized domain model."""
    return _json(service.domain_schema())
