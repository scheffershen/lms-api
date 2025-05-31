from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    PROJECT_NAME: str = "LMS API"
    VERSION: str = "3.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security settings
    SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database settings
    MYSQL_HOST: str = "127.0.0.1" #os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_USER: str = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD: str = os.getenv('MYSQL_ROOT_PASSWORD')
    MYSQL_DATABASE: str = "lms_umg" #os.getenv('MYSQL_DATABASE', 'medflixs')
    
    # Redis settings
    REDIS_HOST: str = "127.0.0.1" #os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT: int = int(os.getenv('REDIS_PORT', 6379))
    
    # Admin credentials
    ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL", "admin@example.com")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "change-this-password")

settings = Settings() 