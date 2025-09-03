from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    test: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()  # type: ignore
