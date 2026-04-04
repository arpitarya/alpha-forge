"""Trade execution endpoints — place, modify, cancel orders."""

from __future__ import annotations

from enum import Enum

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.logging import get_logger

router = APIRouter()
logger = get_logger("routes.trade")


class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    SL = "SL"
    SL_M = "SL-M"


class ProductType(str, Enum):
    CNC = "CNC"  # Cash and Carry (delivery)
    MIS = "MIS"  # Margin Intraday Settlement
    NRML = "NRML"  # Normal (F&O)


class PlaceOrderRequest(BaseModel):
    symbol: str
    exchange: str = "NSE"
    side: OrderSide
    order_type: OrderType = OrderType.MARKET
    product: ProductType = ProductType.CNC
    quantity: int = Field(gt=0)
    price: float | None = None
    trigger_price: float | None = None


class OrderResponse(BaseModel):
    order_id: str
    status: str
    message: str


@router.post("/order", response_model=OrderResponse)
async def place_order(body: PlaceOrderRequest):
    """Place a new order via connected broker."""
    logger.info("Order request: %s %s %s qty=%d", body.side, body.order_type, body.symbol, body.quantity)
    # TODO: send to broker API
    raise HTTPException(status_code=501, detail="Order placement not yet implemented")


@router.put("/order/{order_id}")
async def modify_order(order_id: str):
    """Modify an existing pending order."""
    raise HTTPException(status_code=501, detail="Order modification not yet implemented")


@router.delete("/order/{order_id}")
async def cancel_order(order_id: str):
    """Cancel a pending order."""
    raise HTTPException(status_code=501, detail="Order cancellation not yet implemented")
