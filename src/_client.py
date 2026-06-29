# Copyright (c) 2026 Dedalus Labs, Inc. and its contributors
# SPDX-License-Identifier: MIT

"""End-to-end client test for the Shopify Admin MCP server.

Runs against the deployed marketplace server via the Dedalus runner,
passing credentials through the DAuth SecretValues path (the same path a
real marketplace user hits). Every tool is exercised at least once and a
deterministic PASS/FAIL line is printed per tool.

Required environment variables:
    DEDALUS_API_KEY         Dedalus API key (dsk-live-...)
    SHOPIFY_ACCESS_TOKEN    Shopify Admin API access token (shpat_...)

Optional:
    DEDALUS_API_URL   Override Dedalus API base (default https://api.dedaluslabs.ai)
    DEDALUS_AS_URL    Override Dedalus AS base  (default https://as.dedaluslabs.ai)
    MCP_SERVER_SLUG   Marketplace slug (default JiayuWang/shopify-admin-mcp)

Usage:
    PYTHONPATH=src python src/_client.py
"""

import asyncio
import os
import sys

from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from shopify import shopify  # noqa: E402
from dedalus_mcp.auth import Connection as _Conn
from dedalus_labs.lib.mcp.request import slug_to_connection_name as _s2c


def _rebind(conn, slug):
    return _Conn(name=_s2c(slug), secrets=conn.secrets, base_url=conn.base_url,
                 auth_header_name=conn.auth_header_name, auth_header_format=conn.auth_header_format)


DEDALUS_API_KEY = os.getenv("DEDALUS_API_KEY", "")
DEDALUS_API_URL = os.getenv("DEDALUS_API_URL", "https://api.dedaluslabs.ai")
DEDALUS_AS_URL = os.getenv("DEDALUS_AS_URL", "https://as.dedaluslabs.ai")
SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN", "")
MCP_SERVER_SLUG = os.getenv("MCP_SERVER_SLUG", "JiayuWang/shopify-admin-mcp")
MODEL = os.getenv("DEDALUS_TEST_MODEL", "anthropic/claude-sonnet-4-5")

REQUIRED_TOOLS = [
    "list_products",
    "get_product",
    "list_orders",
    "get_order",
    "list_customers",
    "get_customer",
    "list_inventory_levels",
    "list_collections",
    "create_product",
    "update_product",
    "create_draft_order",
]


def _passed(tool_name: str, tool_events: list) -> bool:
    """A tool counts as exercised if it was successfully called.

    Checks on_tool_event records for actual tool invocation with the expected name.
    """
    if not tool_events:
        return False

    for event in tool_events:
        if hasattr(event, 'name') and tool_name in event.name:
            return True
        if isinstance(event, dict) and tool_name in event.get('name', ''):
            return True

    return False


async def _run_tool(runner, creds, tool_name: str, instruction: str) -> bool:
    print(f"\n--- {tool_name} ---")
    tool_events = []

    def on_tool_event(event):
        tool_events.append(event)

    try:
        result = await runner.run(
            input=instruction,
            model=MODEL,
            mcp_servers=[MCP_SERVER_SLUG],
            credentials=creds,
            max_steps=6,
            max_tokens=4096,
            on_tool_event=on_tool_event,
        )
        output = getattr(result, "output", str(result)) or ""
        print(output[:600])
        ok = _passed(tool_name, tool_events)
        if ok:
            print(f"✓ Tool called: {len(tool_events)} invocation(s)")
    except Exception as exc:  # noqa: BLE001
        print(f"exception: {exc!r}")
        ok = False
    print(f"[{'PASS' if ok else 'FAIL'}] {tool_name}")
    return ok


async def main() -> int:
    if not DEDALUS_API_KEY:
        print("Error: DEDALUS_API_KEY not set")
        return 1
    if not SHOPIFY_ACCESS_TOKEN:
        print("Error: SHOPIFY_ACCESS_TOKEN not set")
        return 1

    from dedalus_labs import AsyncDedalus, DedalusRunner
    from dedalus_mcp.auth import SecretValues

    creds = [SecretValues(_rebind(shopify, MCP_SERVER_SLUG), token=SHOPIFY_ACCESS_TOKEN)]

    client = AsyncDedalus(
        api_key=DEDALUS_API_KEY,
        base_url=DEDALUS_API_URL,
        as_base_url=DEDALUS_AS_URL,
    )
    runner = DedalusRunner(client)

    print(f"Testing Shopify Admin MCP server: {MCP_SERVER_SLUG}")
    print("=" * 60)

    results: dict[str, bool] = {}

    # 1. Read-only discovery.
    results["list_products"] = await _run_tool(
        runner, creds, "list_products",
        "Call the list_products tool with first 5 and list each product id and title.",
    )
    results["get_product"] = await _run_tool(
        runner, creds, "get_product",
        "Call list_products with first 1 to get a product id, then call "
        "get_product on that id and show its title.",
    )
    results["list_orders"] = await _run_tool(
        runner, creds, "list_orders",
        "Call the list_orders tool with first 5 and list each order id.",
    )
    results["get_order"] = await _run_tool(
        runner, creds, "get_order",
        "Call list_orders with first 1 to get an order id, then call get_order "
        "on that id. If there are no orders, report the empty result.",
    )
    results["list_customers"] = await _run_tool(
        runner, creds, "list_customers",
        "Call the list_customers tool with first 5 and list each customer id.",
    )
    results["get_customer"] = await _run_tool(
        runner, creds, "get_customer",
        "Call list_customers with first 1 to get a customer id, then call "
        "get_customer on that id. If there are no customers, report that.",
    )
    results["list_inventory_levels"] = await _run_tool(
        runner, creds, "list_inventory_levels",
        "Call the list_inventory_levels tool and list the inventory levels.",
    )
    results["list_collections"] = await _run_tool(
        runner, creds, "list_collections",
        "Call the list_collections tool with first 5 and list each collection title.",
    )

    # 2. Write tools against isolated smoke-test fixtures. The product we create
    #    is the one we then update; the draft order is a draft (not a real
    #    placed order) so it is inherently non-destructive.
    results["create_product"] = await _run_tool(
        runner, creds, "create_product",
        "Call create_product with title 'Dedalus Smoke Test Product'. Report "
        "the new product id.",
    )
    results["update_product"] = await _run_tool(
        runner, creds, "update_product",
        "Call create_product with title 'Dedalus Update Test' to get a product "
        "id, then call update_product on that id setting title to "
        "'Dedalus Updated Product'.",
    )
    results["create_draft_order"] = await _run_tool(
        runner, creds, "create_draft_order",
        "Call create_draft_order with a single line item that has title "
        "'Dedalus Smoke Test Item', quantity 1 and price '1.00'. Report the "
        "draft order id.",
    )

    print("\n" + "=" * 60)
    print("Summary")
    for name in REQUIRED_TOOLS:
        ok = results.get(name, False)
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")

    all_pass = all(results.get(t, False) for t in REQUIRED_TOOLS)
    print("\nRESULT:", "ALL PASS" if all_pass else "SOME FAILED")
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))