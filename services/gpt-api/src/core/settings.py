from pydantic_settings import BaseSettings, SettingsConfigDict


class ServiceConfig(BaseSettings):
    cloudflare_api_token: str
    cloudflare_account_id: str
    cloudflare_model: str = "@cf/meta/llama-3.1-70b-instruct"

    model_config = SettingsConfigDict(env_prefix="GPT_API_")


service_config = ServiceConfig()
