import os


SHOPIFY_API_VERSION = "2024-01"


def get_shop_from_context() -> str:
    return os.getenv("SHOPIFY_SHOP", "{shop}")


def get_base_url() -> str:
    shop = get_shop_from_context()
    return f"https://{shop}.myshopify.com/admin/api/{SHOPIFY_API_VERSION}"