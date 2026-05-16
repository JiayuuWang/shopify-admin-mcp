import asyncio
import os
from shopify import shopify_tools
from shopify.tools import (
    list_products,
    get_product,
    create_product,
    update_product,
    list_orders,
    get_order,
    create_draft_order,
    list_customers,
    get_customer,
    list_inventory_levels,
    list_collections,
)


async def main():
    print("Shopify Admin MCP Client Test")
    print("=" * 50)

    print("\n1. Testing list_products...")
    result = await list_products(first=5)
    print(f"Result: {result[:200]}...")

    print("\n2. Testing list_orders...")
    result = await list_orders(first=5)
    print(f"Result: {result[:200]}...")

    print("\n3. Testing list_customers...")
    result = await list_customers(first=5)
    print(f"Result: {result[:200]}...")

    print("\n4. Testing list_collections...")
    result = await list_collections(first=5)
    print(f"Result: {result[:200]}...")

    print("\n5. Testing list_inventory_levels...")
    result = await list_inventory_levels(first=5)
    print(f"Result: {result[:200]}...")

    print("\nAll tests completed!")


if __name__ == "__main__":
    asyncio.run(main())