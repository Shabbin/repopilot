from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    project_name: str = "RepoPilot"
    project_version: str = "0.1.0"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()