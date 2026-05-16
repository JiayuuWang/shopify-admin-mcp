import asyncio
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
from server import create_server


async def main():
    server = create_server()
    server.collect(
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
    await server.serve(port=8080)


if __name__ == "__main__":
    asyncio.run(main())