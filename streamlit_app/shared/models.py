"""Shared Pydantic models for the Streamlit teaching app.

These intentionally mirror the models in the course notebooks so the app and
the notebooks tell the same story.
"""

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class Person(BaseModel):
    name: str
    age: int = Field(ge=0, le=120)
    city: str

    @field_validator("name")
    @classmethod
    def name_must_be_capitalized(cls, v: str) -> str:
        fixed = v.strip().title()
        if fixed != v:
            raise ValueError(f"name must be capitalized, got {v!r}")
        return v


class SentimentResult(BaseModel):
    label: Literal["positive", "negative", "neutral"]


class LineItem(BaseModel):
    description: str
    quantity: int = Field(gt=0)
    unit_price: float = Field(gt=0)
    total: float


class Invoice(BaseModel):
    invoice_number: str
    customer_name: str
    items: list[LineItem]
    subtotal: float
    tax_rate: float = Field(ge=0, le=1)
    total_amount: float
    payment_status: Literal["paid", "pending", "overdue"]
