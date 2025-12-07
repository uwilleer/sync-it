from common.shared.clients import BaseClient
from parsers import BaseParser


class BaseParserClient(BaseClient):
    parser: type[BaseParser]
