from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Payflow"
    environment: str = "dev"
    
settings = Settings()
