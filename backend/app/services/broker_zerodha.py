"""Zerodha Kite Connect broker adapter."""

from __future__ import annotations

from app.services.broker_base import BaseBroker, BrokerOrder, BrokerPosition


class ZerodhaBroker(BaseBroker):
    """Zerodha Kite Connect integration.

    Requires:
    - API key & secret from https://developers.kite.trade
    - Access token obtained via Kite login flow
    """

    def __init__(self, api_key: str, api_secret: str, access_token: str | None = None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token
        self._kite = None

    async def authenticate(self, credentials: dict) -> bool:
        # TODO: use kiteconnect SDK to generate session
        # from kiteconnect import KiteConnect
        # kite = KiteConnect(api_key=self.api_key)
        # data = kite.generate_session(credentials["request_token"], api_secret=self.api_secret)
        # self.access_token = data["access_token"]
        return False

    async def place_order(
        self,
        symbol: str,
        exchange: str,
        side: str,
        order_type: str,
        product: str,
        quantity: int,
        price: float | None = None,
        trigger_price: float | None = None,
    ) -> BrokerOrder:
        # TODO: kite.place_order(...)
        raise NotImplementedError("Zerodha order placement pending integration")

    async def cancel_order(self, order_id: str) -> bool:
        raise NotImplementedError

    async def get_positions(self) -> list[BrokerPosition]:
        raise NotImplementedError

    async def get_holdings(self) -> list[BrokerPosition]:
        raise NotImplementedError

    async def get_order_history(self) -> list[BrokerOrder]:
        raise NotImplementedError

    async def get_quote(self, symbol: str, exchange: str) -> dict:
        raise NotImplementedError
