"""MCP tool definitions (registered on import via @mcp.tool decorators)."""

from __future__ import annotations

from typing import Any

from mcp.types import CallToolResult

from .app import mcp, service, _result


@mcp.tool()
def investor_sync_data(
    mode: str = "incremental",
    account_ids: list[str] | None = None,
    force: bool = False,
    from_date: str | None = None,
    to_date: str | None = None,
) -> CallToolResult:
    """Synchronize broker and market data. Read-only in MVP."""
    return _result(service.sync_data(mode, account_ids, force, from_date, to_date))


@mcp.tool()
def investor_get_sync_status() -> CallToolResult:
    """Return last sync status and data freshness."""
    return _result(service.get_sync_status())


@mcp.tool()
def investor_get_profile() -> CallToolResult:
    """Return investment goals, risk profile, and limits."""
    return _result(service.get_profile())


@mcp.tool()
def investor_save_profile(profile: dict[str, Any]) -> CallToolResult:
    """Save local investment profile. Does not change broker data."""
    return _result(service.save_profile(profile))


@mcp.tool()
def investor_list_accounts(include_inactive: bool = False) -> CallToolResult:
    """List broker accounts available for analysis."""
    return _result(service.list_accounts(include_inactive))


@mcp.tool()
def investor_select_accounts(account_ids: list[str]) -> CallToolResult:
    """Select broker accounts included in portfolio analysis."""
    return _result(service.select_accounts(account_ids))


@mcp.tool()
def investor_get_portfolio(
    account_ids: list[str] | None = None,
    refresh: bool = False,
    include_positions: bool = True,
    include_allocation: bool = True,
) -> CallToolResult:
    """Return current aggregated portfolio."""
    return _result(service.get_portfolio(account_ids, refresh, include_positions, include_allocation))


@mcp.tool()
def investor_analyze_portfolio(
    account_ids: list[str] | None = None,
    as_of: str | None = None,
    include_goal_comparison: bool = True,
) -> CallToolResult:
    """Analyze allocation, concentration, and goal deviation."""
    return _result(service.analyze_portfolio(account_ids, as_of, include_goal_comparison))


@mcp.tool()
def investor_explain_portfolio_change(
    period: str = "week",
    from_date: str | None = None,
    to_date: str | None = None,
    account_ids: list[str] | None = None,
    include_news: bool = True,
) -> CallToolResult:
    """Explain portfolio change for a period. Date range uses from_date/to_date."""
    return _result(service.explain_portfolio_change(period, from_date, to_date, account_ids, include_news))


@mcp.tool()
def investor_get_operations(
    from_date: str,
    to_date: str,
    account_ids: list[str] | None = None,
    instrument: dict[str, Any] | None = None,
    operation_types: list[str] | None = None,
) -> CallToolResult:
    """Return account operations for a date range (from_date/to_date)."""
    return _result(service.get_operations(from_date, to_date, account_ids, instrument, operation_types))


@mcp.tool()
def investor_get_instrument(
    instrument: dict[str, Any],
    include_position: bool = True,
    include_events: bool = True,
) -> CallToolResult:
    """Return instrument card and portfolio position. ``instrument`` is {id_type, id}."""
    return _result(service.get_instrument(instrument, include_position, include_events))


@mcp.tool()
def investor_scan_risks(
    account_ids: list[str] | None = None,
    risk_types: list[str] | None = None,
    severity_min: str = "low",
) -> CallToolResult:
    """Scan portfolio risk signals."""
    return _result(service.scan_risks(account_ids, risk_types, severity_min))


@mcp.tool()
def investor_get_news_digest(
    period: str = "week",
    from_date: str | None = None,
    to_date: str | None = None,
    account_ids: list[str] | None = None,
    importance_min: str = "medium",
) -> CallToolResult:
    """Dynamic research brief: portfolio-derived targets + tailored search queries.

    The server does NOT fetch news; it computes WHAT to look up (top issuers/sectors,
    rate sensitivity) from the current holdings. The assistant then web-searches the
    returned research_targets and reports the impact on the portfolio.
    """
    return _result(service.get_news_digest(period, from_date, to_date, account_ids, importance_min))


@mcp.tool()
def investor_recommend_next_action(
    available_cash: dict[str, Any],
    goal: str = "next_purchase",
    max_options: int = 3,
    account_ids: list[str] | None = None,
) -> CallToolResult:
    """Recommend next analytical action, usually for a cash contribution."""
    return _result(service.recommend_next_action(available_cash, goal, max_options, account_ids))


@mcp.tool()
def investor_simulate_action(
    actions: list[dict[str, Any]],
    account_ids: list[str] | None = None,
) -> CallToolResult:
    """Simulate buy/sell/reduce/increase actions as a 'what-if'.

    Each action is {action, instrument: {id_type, id}, amount: {amount, currency}}.
    Does NOT place any broker order.
    """
    return _result(service.simulate_action(actions, account_ids))


@mcp.tool()
def investor_generate_report(
    report_type: str = "weekly",
    from_date: str | None = None,
    to_date: str | None = None,
    account_ids: list[str] | None = None,
    format: str = "markdown",
) -> CallToolResult:
    """Generate a portfolio report (markdown or json)."""
    return _result(service.generate_report(report_type, from_date, to_date, account_ids, format))


@mcp.tool()
def investor_get_goal_progress(
    account_ids: list[str] | None = None,
    expected_return_percent: float = 12.0,
) -> CallToolResult:
    """Progress to the user's long-term goals: capital target %, passive-income coverage
    (coupons + dividends vs target), and a rough timeline projection."""
    return _result(service.get_goal_progress(account_ids, expected_return_percent))


@mcp.tool()
def investor_get_bond_calendar(
    horizon_days: int = 90,
    account_ids: list[str] | None = None,
) -> CallToolResult:
    """Bond calendar: upcoming coupons/maturities/offers, maturity ladder, 12m coupon income."""
    return _result(service.get_bond_calendar(account_ids, horizon_days))


@mcp.tool()
def investor_research_instrument(
    instrument: dict[str, Any],
    depth: str = "standard",
    focus: list[str] | None = None,
) -> CallToolResult:
    """Prepare an instrument/issuer research draft (external sources not wired yet).

    ``instrument`` is {id_type, id}. ``depth`` is brief|standard|deep.
    """
    return _result(service.research_instrument(instrument, depth, focus))
