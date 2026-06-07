"""FastMCP core: app instance, service wiring, helpers, middleware, and main()."""

from __future__ import annotations

import argparse
import json
import os
from typing import Any

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from mcp.types import CallToolResult, TextContent

from ..adapters import build_broker_adapter
from ..service import InvestorService
from ..storage import Storage

load_dotenv()

_INSTRUCTIONS = """\
Personal investment-portfolio assistant (read-only, RU market).

For ANY question about the portfolio, its risks, news, or "what should I buy / rebalance /
should I do X", proactively and WITHOUT being explicitly asked:
1) call investor_get_news_digest (and, for buy/rebalance questions, investor_recommend_next_action)
   — they return, computed DYNAMICALLY from the user's holdings/goals: research_targets
   (top issuers/sectors with tailored queries) AND context_lenses (the macro/geopolitical/
   commodity/credit/FX/sector factors that matter for THIS book, each with why + queries);
2) WEB-SEARCH those targets and lenses to get the CURRENT picture (key-rate trajectory,
   sanctions/geopolitics, oil & metals cycle, credit spreads on the over-concentrated bond
   issuers, ruble outlook, sector regulation, equity valuations — whichever the data flags);
3) only THEN give the answer/recommendation, weaving in that macro & political context plus
   the user's long-term goals (profile.goals), with rationale, risks and alternatives.

The server never fabricates or fetches news/macro itself — it tells you WHAT to research; you
do the searching and judgement. Treat every output as analysis/scenarios, not a
guaranteed-return investment recommendation."""

mcp = FastMCP("Investor MCP", instructions=_INSTRUCTIONS)
_db_path = os.getenv("INVESTOR_MCP_STORAGE_PATH", "./data/investor_mcp.db")
_cache_ttl = int(os.getenv("INVESTOR_MCP_CACHE_TTL_SECONDS", "86400"))  # default: 1 day
service = InvestorService(
    broker=build_broker_adapter(),
    storage=Storage(_db_path),
    cache_ttl_seconds=_cache_ttl,
)


def _json(data: dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)


class _BearerAuthMiddleware:
    """Minimal ASGI middleware: require ``Authorization: Bearer <token>`` on HTTP.

    Active only when ``INVESTOR_MCP_AUTH_TOKEN`` is set. Defence-in-depth for a
    publicly reachable endpoint that exposes the user's whole portfolio.
    """

    def __init__(self, app: Any, token: str) -> None:
        self.app = app
        self._expected = f"Bearer {token}"

    async def __call__(self, scope: Any, receive: Any, send: Any) -> None:
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return
        headers = dict(scope.get("headers") or [])
        if headers.get(b"authorization", b"").decode() == self._expected:
            await self.app(scope, receive, send)
            return
        await send(
            {
                "type": "http.response.start",
                "status": 401,
                "headers": [(b"content-type", b"application/json"), (b"www-authenticate", b"Bearer")],
            }
        )
        await send({"type": "http.response.body", "body": b'{"error":"unauthorized"}'})


def _result(payload: dict[str, Any]) -> CallToolResult:
    """Wrap a service response dict into an MCP CallToolResult.

    The full payload is serialized into the ``content`` text (so every MCP client,
    incl. those that ignore ``structuredContent`` when no outputSchema is declared,
    actually shows the model the data), AND mirrored into ``structuredContent`` for
    clients that use it. ``isError`` is derived from ``ok``.
    """
    summary = payload.get("summary") or ("Ошибка." if not payload.get("ok", True) else "Готово.")
    text = f"{summary}\n\n{_json(payload)}"
    return CallToolResult(
        content=[TextContent(type="text", text=text)],
        structuredContent=payload,
        isError=not payload.get("ok", True),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Investor MCP server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "streamable-http"],
        default="stdio",
        help="MCP transport to use.",
    )
    parser.add_argument(
        "--host",
        default=os.getenv("INVESTOR_MCP_HOST", "127.0.0.1"),
        help="Host for streamable-http transport.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("INVESTOR_MCP_PORT", "8000")),
        help="Port for streamable-http transport.",
    )
    parser.add_argument(
        "--mcp-path",
        default=os.getenv("INVESTOR_MCP_PATH", "/mcp"),
        help="HTTP path for streamable MCP endpoint.",
    )
    args = parser.parse_args()
    if args.transport == "stdio":
        mcp.run()
    else:
        mcp.settings.host = args.host
        mcp.settings.port = args.port
        mcp.settings.streamable_http_path = args.mcp_path
        # The server binds to localhost behind a trusted reverse proxy/tunnel, so the
        # built-in DNS-rebinding Host check (localhost-only) would reject proxied
        # requests. Disable it by default; set INVESTOR_MCP_ALLOWED_HOSTS for strict mode.
        allowed = os.getenv("INVESTOR_MCP_ALLOWED_HOSTS")
        if allowed:
            hosts = [h.strip() for h in allowed.split(",") if h.strip()]
            mcp.settings.transport_security = TransportSecuritySettings(
                enable_dns_rebinding_protection=True,
                allowed_hosts=hosts,
                allowed_origins=[f"https://{h}" for h in hosts],
            )
        else:
            mcp.settings.transport_security = TransportSecuritySettings(
                enable_dns_rebinding_protection=False
            )
        token = os.getenv("INVESTOR_MCP_AUTH_TOKEN")
        if token:
            import uvicorn

            app = _BearerAuthMiddleware(mcp.streamable_http_app(), token)
            uvicorn.run(app, host=args.host, port=args.port, log_level="info")
        else:
            mcp.run(transport="streamable-http")
