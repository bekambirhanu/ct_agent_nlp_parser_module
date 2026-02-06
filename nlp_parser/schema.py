from typing import Optional, Literal
from pydantic import BaseModel, Field

class TradeOrder(BaseModel):
    action: Literal["BUY", "SELL"]
    symbol: str = Field(description="The ticker symbol, e.g., EURUSD, BTCUSD")
    volume: float = Field(description="The lot size or quantity")
    order_type: Literal["MARKET", "LIMIT", "STOP"] = "MARKET"
    price: Optional[float] = Field(None, description="Entry price for limit/stop orders")
    sl: Optional[float] = Field(None, description="Stop Loss price")
    tp: Optional[float] = Field(None, description="Take Profit price")

class ParserResponse(BaseModel):
    success: bool
    order: Optional[TradeOrder] = None
    error_message: Optional[str] = None
    raw_text: str