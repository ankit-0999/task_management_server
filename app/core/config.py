import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Team Task Manager"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-super-secret-key-for-jwt")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    SQLALCHEMY_DATABASE_URI: str = os.getenv("DATABASE_URL")

settings = Settings()
