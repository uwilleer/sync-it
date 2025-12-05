from pydantic_settings import BaseSettings, SettingsConfigDict


class ServiceConfig(BaseSettings):
    db_schema: str = "vacancy_parser"

    model_config = SettingsConfigDict(env_prefix="VACANCY_PARSER_")


service_config = ServiceConfig()
