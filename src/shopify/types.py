from dataclasses import dataclass
from typing import Optional


@dataclass
class Product:
    id: str
    title: str
    description_html: Optional[str] = None
    handle: Optional[str] = None
    vendor: Optional[str] = None
    product_type: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@dataclass
class Order:
    id: str
    name: str
    email: Optional[str] = None
    created_at: Optional[str] = None
    total_price: Optional[str] = None
    financial_status: Optional[str] = None
    fulfillment_status: Optional[str] = None
    status: Optional[str] = None


@dataclass
class Customer:
    id: str
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    verified_email: bool = False
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@dataclass
class InventoryLevel:
    id: str
    available: int
    location_id: str
    product_id: str


@dataclass
class Collection:
    id: str
    title: str
    handle: Optional[str] = None
    description_html: Optional[str] = None
    sort_order: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None