import os

from dotenv import load_dotenv


load_dotenv()


class AppConfig:
    # Env
    ENV: str = os.getenv("ENV", "development")

    # File Config
    ALLOWED_EXTENSIONS: set[str] = {".pdf", ".docx", ".png", ".jpg", ".jpeg"}
    MAX_FILE_SIZE_MB: int = 2

    # Mataparser API
    API_URL: str = os.getenv("MATAPARSER_API_URL", "https://mataparser.cloud/platform/api/v1")
    API_KEY: str = os.getenv("MATAPARSER_API_KEY", "")


app_config = AppConfig()
