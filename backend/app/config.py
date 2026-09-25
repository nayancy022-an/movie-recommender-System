from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./movies.db"
    secret_key: str = "dev-secret-change-me"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    tmdb_api_key: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
