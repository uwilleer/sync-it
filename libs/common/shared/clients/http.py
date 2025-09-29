from httpx import AsyncClient, Limits


__all__ = [
    "http_client",
]


limits = Limits(
    max_connections=1000,
    max_keepalive_connections=500,
    keepalive_expiry=30,
)

http_client: AsyncClient = AsyncClient(limits=limits)
