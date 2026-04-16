#core/config.py


from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
from zoneinfo import ZoneInfo



class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file= ".env",
        extra="ignore"
    )

    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    JWT_EXPIRE_MINUTES: int

    CREATOR_REGISTRATION_KEY: str

    RESOURCES_TIME_ZONE: str

    @computed_field
    @property
    def time_zone(self) -> ZoneInfo:
        return ZoneInfo(self.RESOURCES_TIME_ZONE)

    @computed_field
    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


settings = Settings()
