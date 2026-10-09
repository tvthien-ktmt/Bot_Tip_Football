from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    PROJECT_NAME: str = "KèoLab – Football Tip Analyzer"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    ENVIRONMENT: str = "development"
    
    # Database
    DATABASE_URL: str = "sqlite:///./keolab.db"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000", "*"]
    
    # External APIs (Optional - mock/fallback available)
    FOOTBALL_DATA_ORG_KEY: str = ""
    THE_ODDS_API_KEY: str = ""
    
    # Quantitative Risk / Model Tuning
    MIN_EDGE: float = 0.025  # 2.5% minimum edge to issue a tip
    MIN_EV: float = 0.030    # 3.0% minimum expected value
    MAX_MARKET_DIVERGENCE: float = 0.12  # If model deviates > 12%, penalize confidence
    KELLY_FRACTION: float = 0.25         # Quarter Kelly
    MAX_VIRTUAL_STAKE_PCT: float = 0.02  # Max 2% virtual bankroll per tip
    MIN_MATCHES_SAMPLE: int = 10         # Minimum matches for team sample
    
    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
