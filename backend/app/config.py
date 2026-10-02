from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Base de datos
    DATABASE_URL: str = "sqlite:///./videoapp.db"

    # JWT
    JWT_SECRET_KEY: str = "dev-secret-cambiar"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # AWS 
    AWS_REGION: str = "us-east-1"
    AWS_S3_BUCKET: str = ""  # bucket de videos
    AWS_S3_THUMBNAILS_BUCKET: str = ""  # bucket de miniaturas

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

   
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


settings = Settings()