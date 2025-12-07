import pickle  # noqa: S403
from typing import Any

from common.shared.serializers import AbstractSerializer


class PickleSerializer(AbstractSerializer):
    def serialize(self, obj: Any) -> bytes:  # noqa: PLR6301
        return pickle.dumps(obj)

    def deserialize(self, obj: bytes) -> Any:  # noqa: PLR6301
        return pickle.loads(obj)  # noqa: S301
