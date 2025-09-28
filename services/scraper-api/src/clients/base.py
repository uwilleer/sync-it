from common.shared.clients import BaseClient
from parsers import BaseParser


__all__ = ["BaseParserClient"]


class BaseParserClient(BaseClient):
    parser: type[BaseParser]
