from common.logger import get_logger


logger = get_logger(__name__)


def validate_health_response(response_text: str | None) -> None:
    expected_responses = {"healthy", "healthy.", "healthy!"}

    if response_text is None or response_text.lower() not in expected_responses:
        raise ValueError(f'Unexpected healthcheck response: "{response_text}"')
