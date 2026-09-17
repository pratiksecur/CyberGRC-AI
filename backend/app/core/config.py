from dotenv import load_dotenv
import os


load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv(
        "ACCESS_TOKEN_EXPIRE_MINUTES",
        30,
    )
)

PROJECT_NAME = os.getenv("PROJECT_NAME")
PROJECT_VERSION = os.getenv("PROJECT_VERSION")