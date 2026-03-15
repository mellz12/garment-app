from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str = "mysql+aiomysql://root:password@localhost/kis"

    model_config = ConfigDict(env_file=".env")

settings = Settings()