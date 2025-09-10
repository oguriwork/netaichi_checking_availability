from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    IS_HEADLESS: bool
    ACCOUNT_ID: str
    ACCOUNT_PASSWORD: str
    DB_PATH: str = "netaichi.db"
    LOG_LEVEL: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()  # type: ignore
