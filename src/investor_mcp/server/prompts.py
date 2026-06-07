"""MCP prompt definitions (registered on import via @mcp.prompt decorators)."""

from __future__ import annotations

from .app import mcp


@mcp.prompt()
def portfolio_weekly_review(week_ending: str | None = None) -> str:
    window = f" на неделю, заканчивающуюся {week_ending}," if week_ending else ""
    return (
        f"Подготовь недельный обзор портфеля{window}: проверь свежесть данных, получи портфель, "
        "объясни изменения, просканируй риски, добавь новостную выжимку и сформируй отчет."
    )


@mcp.prompt()
def portfolio_drop_explainer(period: str = "day") -> str:
    return (
        f"Объясни, почему портфель изменился за период: {period}. "
        "Отдели рыночный шум от возможных фундаментальных причин."
    )


@mcp.prompt()
def next_purchase_advice(amount: float, currency: str = "RUB") -> str:
    return (
        f"Подбери варианты для следующего пополнения на {amount} {currency}. "
        "Учитывай цели, текущую аллокацию, риски и альтернативы."
    )


@mcp.prompt()
def instrument_deep_dive(instrument: str, depth: str = "standard") -> str:
    return (
        f"Сделай разбор инструмента {instrument} (глубина: {depth}): получи карточку и позицию, "
        "подготовь исследование, оцени риски и роль актива в портфеле относительно целей."
    )


@mcp.prompt()
def risk_review() -> str:
    return (
        "Покажи, что сейчас требует внимания: просканируй риски портфеля, "
        "подмешай важные новости и события и предложи приоритетные действия."
    )
