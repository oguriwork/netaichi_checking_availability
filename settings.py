from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # ここでpythonの変数にする
    test:str
    test2:bool = False
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
settings=Settings()