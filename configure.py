from pydantic_settings import BaseSettings, SettingsConfigDict

class Setting(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REDIS_URL: str = "redis://localhost:6379" 
      
    CACHE_TTL: int = 3600

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

settings = Setting()