import json
from typing import Any

from dedalus_mcp import HttpMethod, HttpRequest, get_context, tool
from dedalus_mcp.auth import Connection, SecretKeys
from dedalus_mcp.types import ToolAnnotations


shopify = Connection(
    name="shopify",
    secrets=SecretKeys(access_token="SHOPIFY_ACCESS_TOKEN"),
    base_url="https://{shop}.myshopify.com/admin/api/2024-01",
    auth_header_format="Bearer {api_key}",
)

ShopifyResult = list[Any]


async def _graphql_req(query: str, variables: dict | None = None) -> ShopifyResult:
    ctx = get_context()
    body: dict[str, Any] = {"query": query}
    if variables:
        body["variables"] = variables
    resp = await ctx.dispatch(
        "shopify",
        HttpRequest(method=HttpMethod.POST, path="/graphql.json", body=body),
    )
    if resp.success:
        data = resp.response.body if resp.response.body else {}
        errors = data.get("errors", [])
        if errors:
            return [f"GraphQL Error: {json.dumps(errors)}"]
        return [json.dumps(data, indent=2)]
    error = resp.error.message if resp.error else "Request failed"
    return [f"Error: {error}"]


LIST_PRODUCTS_QUERY = """
query listProducts($first: Int!, $after: String, $query: String, $sortKey: ProductSortKeys, $reverse: Boolean) {
  products(first: $first, after: $after, query: $query, sortKey: $sortKey, reverse: $reverse) {
    edges {
      node {
        id
        title
        descriptionHtml
        handle
        vendor
        productType
        status
        tags
        createdAt
        updatedAt
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
"""

GET_PRODUCT_QUERY = """
query getProduct($id: ID!) {
  product(id: $id) {
    id
    title
    descriptionHtml
    handle
    vendor
    productType
    status
    tags
    createdAt
    updatedAt
    images(first: 10) {
      edges {
        node {
          id
          src
          altText
        }
      }
    }
    variants(first: 20) {
      edges {
        node {
          id
          title
          price
          sku
          barcode
          inventoryQuantity
          inventoryPolicy
        }
      }
    }
  }
}
"""

CREATE_PRODUCT_MUTATION = """
mutation createProduct($input: ProductInput!) {
  productCreate(input: $input) {
    product {
      id
      title
      handle
      status
      createdAt
    }
    userErrors {
      field
      message
    }
  }
}
"""

UPDATE_PRODUCT_MUTATION = """
mutation updateProduct($input: ProductInput!) {
  productUpdate(input: $input) {
    product {
      id
      title
      handle
      status
      updatedAt
    }
    userErrors {
      field
      message
    }
  }
}
"""

LIST_ORDERS_QUERY = """
query listOrders($first: Int!, $after: String, $query: String, $sortKey: OrderSortKeys, $reverse: Boolean) {
  orders(first: $first, after: $after, query: $query, sortKey: $sortKey, reverse: $reverse) {
    edges {
      node {
        id
        name
        email
        createdAt
        totalPrice {
          amount
          currencyCode
        }
        financialStatus
        fulfillmentStatus
        status
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
"""

GET_ORDER_QUERY = """
query getOrder($id: ID!) {
  order(id: $id) {
    id
    name
    email
    createdAt
    totalPrice {
      amount
      currencyCode
    }
    financialStatus
    fulfillmentStatus
    status
    lineItems(first: 10) {
      edges {
        node {
          id
          title
          quantity
          variant {
            id
            title
            price
          }
        }
      }
    }
    shippingAddress {
      address1
      city
      province
      country
      zip
    }
    billingAddress {
      address1
      city
      province
      country
      zip
    }
  }
}
"""

CREATE_DRAFT_ORDER_MUTATION = """
mutation createDraftOrder($input: DraftOrderInput!) {
  draftOrderCreate(input: $input) {
    draftOrder {
      id
      name
      status
      totalPrice {
        amount
        currencyCode
      }
    }
    userErrors {
      field
      message
    }
  }
}
"""

LIST_CUSTOMERS_QUERY = """
query listCustomers($first: Int!, $after: String, $query: String, $sortKey: CustomerSortKeys, $reverse: Boolean) {
  customers(first: $first, after: $after, query: $query, sortKey: $sortKey, reverse: $reverse) {
    edges {
      node {
        id
        email
        firstName
        lastName
        phone
        verifiedEmail
        createdAt
        updatedAt
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
"""

GET_CUSTOMER_QUERY = """
query getCustomer($id: ID!) {
  customer(id: $id) {
    id
    email
    firstName
    lastName
    phone
    verifiedEmail
    createdAt
    updatedAt
    addresses {
      edges {
        node {
          address1
          city
          province
          country
          zip
        }
      }
    }
    orders(first: 10) {
      edges {
        node {
          id
          name
          createdAt
          totalPrice {
            amount
          }
        }
      }
    }
  }
}
"""

LIST_INVENTORY_LEVELS_QUERY = """
query listInventoryLevels($first: Int!, $after: String, $locations: [ID!]) {
  inventoryLevels(first: $first, after: $after, locationId: $locations) {
    edges {
      node {
        id
        available
        location {
          id
          name
        }
        item {
          id
          product {
            id
            title
          }
          variant {
            id
            title
          }
        }
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
"""

LIST_COLLECTIONS_QUERY = """
query listCollections($first: Int!, $after: String, $query: String, $sortKey: CollectionSortKeys, $reverse: Boolean) {
  collections(first: $first, after: $after, query: $query, sortKey: $sortKey, reverse: $reverse) {
    edges {
      node {
        id
        title
        handle
        descriptionHtml
        sortOrder
        createdAt
        updatedAt
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
"""


@tool(
    description="List products in the store with optional filtering and pagination",
    tags=["products", "read"],
    annotations=ToolAnnotations(readOnlyHint=True),
)
async def list_products(
    first: int = 10,
    after: str = "",
    query: str = "",
    sort_key: str = "CREATED_AT",
    reverse: bool = True,
) -> ShopifyResult:
    variables: dict[str, Any] = {"first": first, "sortKey": sort_key, "reverse": reverse}
    if after:
        variables["after"] = after
    if query:
        variables["query"] = query
    return await _graphql_req(LIST_PRODUCTS_QUERY, variables)


@tool(
    description="Get a single product by ID",
    tags=["products", "read"],
    annotations=ToolAnnotations(readOnlyHint=True),
)
async def get_product(id: str) -> ShopifyResult:
    return await _graphql_req(GET_PRODUCT_QUERY, {"id": id})


@tool(
    description="Create a new product",
    tags=["products", "write"],
    annotations=ToolAnnotations(readOnlyHint=False),
)
async def create_product(
    title: str,
    description_html: str = "",
    vendor: str = "",
    product_type: str = "",
    status: str = "DRAFT",
    tags: str = "",
) -> ShopifyResult:
    input_data: dict[str, Any] = {"title": title, "status": status}
    if description_html:
        input_data["descriptionHtml"] = description_html
    if vendor:
        input_data["vendor"] = vendor
    if product_type:
        input_data["productType"] = product_type
    if tags:
        input_data["tags"] = tags
    return await _graphql_req(CREATE_PRODUCT_MUTATION, {"input": input_data})


@tool(
    description="Update an existing product",
    tags=["products", "write"],
    annotations=ToolAnnotations(readOnlyHint=False),
)
async def update_product(
    id: str,
    title: str = "",
    description_html: str = "",
    vendor: str = "",
    product_type: str = "",
    status: str = "",
    tags: str = "",
) -> ShopifyResult:
    input_data: dict[str, Any] = {"id": id}
    if title:
        input_data["title"] = title
    if description_html:
        input_data["descriptionHtml"] = description_html
    if vendor:
        input_data["vendor"] = vendor
    if product_type:
        input_data["productType"] = product_type
    if status:
        input_data["status"] = status
    if tags:
        input_data["tags"] = tags
    return await _graphql_req(UPDATE_PRODUCT_MUTATION, {"input": input_data})


@tool(
    description="List orders with optional filtering and pagination",
    tags=["orders", "read"],
    annotations=ToolAnnotations(readOnlyHint=True),
)
async def list_orders(
    first: int = 10,
    after: str = "",
    query: str = "",
    sort_key: str = "CREATED_AT",
    reverse: bool = True,
) -> ShopifyResult:
    variables: dict[str, Any] = {"first": first, "sortKey": sort_key, "reverse": reverse}
    if after:
        variables["after"] = after
    if query:
        variables["query"] = query
    return await _graphql_req(LIST_ORDERS_QUERY, variables)


@tool(
    description="Get a single order by ID",
    tags=["orders", "read"],
    annotations=ToolAnnotations(readOnlyHint=True),
)
async def get_order(id: str) -> ShopifyResult:
    return await _graphql_req(GET_ORDER_QUERY, {"id": id})


@tool(
    description="Create a draft order",
    tags=["orders", "write"],
    annotations=ToolAnnotations(readOnlyHint=False),
)
async def create_draft_order(
    line_items: str = "",
    customer_id: str = "",
    note: str = "",
    tags: str = "",
) -> ShopifyResult:
    input_data: dict[str, Any] = {}
    if line_items:
        import json as _json
        try:
            input_data["lineItems"] = _json.loads(line_items)
        except Exception:
            return ["Error: line_items must be valid JSON array"]
    if customer_id:
        input_data["customerId"] = customer_id
    if note:
        input_data["note"] = note
    if tags:
        input_data["tags"] = tags
    return await _graphql_req(CREATE_DRAFT_ORDER_MUTATION, {"input": input_data})


@tool(
    description="List customers with optional filtering and pagination",
    tags=["customers", "read"],
    annotations=ToolAnnotations(readOnlyHint=True),
)
async def list_customers(
    first: int = 10,
    after: str = "",
    query: str = "",
    sort_key: str = "CREATED_AT",
    reverse: bool = True,
) -> ShopifyResult:
    variables: dict[str, Any] = {"first": first, "sortKey": sort_key, "reverse": reverse}
    if after:
        variables["after"] = after
    if query:
        variables["query"] = query
    return await _graphql_req(LIST_CUSTOMERS_QUERY, variables)


@tool(
    description="Get a single customer by ID",
    tags=["customers", "read"],
    annotations=ToolAnnotations(readOnlyHint=True),
)
async def get_customer(id: str) -> ShopifyResult:
    return await _graphql_req(GET_CUSTOMER_QUERY, {"id": id})


@tool(
    description="List inventory levels for locations",
    tags=["inventory", "read"],
    annotations=ToolAnnotations(readOnlyHint=True),
)
async def list_inventory_levels(
    first: int = 10,
    after: str = "",
    location_ids: str = "",
) -> ShopifyResult:
    variables: dict[str, Any] = {"first": first}
    if after:
        variables["after"] = after
    if location_ids:
        variables["locations"] = location_ids.split(",")
    return await _graphql_req(LIST_INVENTORY_LEVELS_QUERY, variables)


@tool(
    description="List collections",
    tags=["collections", "read"],
    annotations=ToolAnnotations(readOnlyHint=True),
)
async def list_collections(
    first: int = 10,
    after: str = "",
    query: str = "",
    sort_key: str = "CREATED_AT",
    reverse: bool = True,
) -> ShopifyResult:
    variables: dict[str, Any] = {"first": first, "sortKey": sort_key, "reverse": reverse}
    if after:
        variables["after"] = after
    if query:
        variables["query"] = query
    return await _graphql_req(LIST_COLLECTIONS_QUERY, variables)


shopify_tools = [
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
]