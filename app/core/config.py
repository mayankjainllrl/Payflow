from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Payflow"
    environment: str = "dev"
    database_url: str = "postgresql+sqlalchemy://payflow:payflow@db:5432/payflow"
    
settings = Settings()
