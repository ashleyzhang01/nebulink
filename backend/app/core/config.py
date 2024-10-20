from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URL: str = "sqlite:///./sql_app.db"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = "your-secret-key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 300
    GITHUB_TOKEN: str | None = None
    FETCHAI_API_KEY: str | None = None
    LINKEDIN_PASSWORD_ENCRYPTION_KEY: str
    HYPERBOLIC_API_KEY: str | None = None

    class Config:
        env_file = ".env"


settings = Settings()
