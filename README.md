# Shopify Admin API MCP Server

A Type 4 OAuth MCP server for the Shopify Admin GraphQL API. Exposes tools for managing products, orders, customers, inventory, and collections.

## Tools

### Products
- `list_products` - List products with filtering and pagination
- `get_product` - Get a single product by ID
- `create_product` - Create a new product
- `update_product` - Update an existing product

### Orders
- `list_orders` - List orders with filtering and pagination
- `get_order` - Get a single order by ID
- `create_draft_order` - Create a draft order

### Customers
- `list_customers` - List customers with filtering and pagination
- `get_customer` - Get a single customer by ID

### Inventory
- `list_inventory_levels` - List inventory levels for locations

### Collections
- `list_collections` - List collections

## Setup

1. Create a Shopify Partner account at [partners.shopify.com](https://partners.shopify.com)
2. Create an app and configure OAuth scopes
3. Set the redirect URI to your Dedalus deployment URL
4. Copy `.env.example` to `.env` and fill in your OAuth credentials

## OAuth Configuration

The server uses per-shop OAuth subdomains. The `{shop}` value is extracted from the OAuth flow and used to construct the API endpoint.

Required environment variables:
- `OAUTH_CLIENT_ID` - Your Shopify app client ID
- `OAUTH_CLIENT_SECRET` - Your Shopify app client secret
- `OAUTH_SCOPES_AVAILABLE` - Comma-separated list of scopes

## Usage

```python
from dedalus_mcp import runner

result = await runner.run(
    input="List all products in my store",
    mcp_servers=["dedalus-labs/shopify-admin-mcp"],
)
```