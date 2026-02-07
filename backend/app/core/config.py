from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "LLM Eval Platform"
    API_V1_STR: str = "/api/v1"
    
    POSTGRES_USER: str = "user"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_SERVER: str = "localhost" # or 'db' in docker
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "llm_eval_db"
    
    # LLM Keys
    OPENAI_API_KEY: Optional[str] = None
    
    # Constructed DB URL
    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    def __init__(self, **values):
        super().__init__(**values)
        if not self.SQLALCHEMY_DATABASE_URI:
            if self.POSTGRES_SERVER and self.POSTGRES_USER != "user":
                 self.SQLALCHEMY_DATABASE_URI = f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            else:
                import os
                # Ensure we use a consistent path for the SQLite database
                # relative to the backend directory
                base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                db_path = os.path.join(base_dir, "llm_eval.db")
                self.SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path}"


    class Config:
        env_file = ".env"

settings = Settings()
