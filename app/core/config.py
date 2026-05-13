from pydantic import BaseSettings
from functools import lrucache

class Settings(BaseSettings):
    database_uri: str
    debug: bool = False

    class Config:
        env_file = '.env'

@lrucache
def get_settings() -> Settings:
    return Settings()
