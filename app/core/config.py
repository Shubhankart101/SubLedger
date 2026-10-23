import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./subledger.db")
APP_ENV = os.getenv("APP_ENV", "development")