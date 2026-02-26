"""
AODE Configuration Module.
Centralizes environment variables, constants, and configuration for the entire system.
Architectural Rationale: Using a single configuration module prevents import cycles,
ensures type safety, and provides a single source of truth for system parameters.
"""
import os
import sys
from dataclasses import dataclass
from typing import Optional, Dict, Any
from enum import Enum
import logging

# Safety: Verify .env existence before attempting to load
if not os.path.exists('.env'):
    logging.warning(".env file not found. Relying on system environment variables.")
else:
    from dotenv import load_dotenv
    load_dotenv()

class AssetClass(Enum):
    """Supported asset classes for opportunity discovery."""
    CRYPTO = "cryptocurrency"
    EQUITY = "equity"
    FOREX = "forex"
    COMMODITY = "commodity"
    DERIVATIVE = "derivative"

@dataclass(frozen=True)
class DataSourceConfig:
    """Configuration for a specific data source."""
    name: str
    base_url: str
    api_key_env_var: str
    rate_limit_per_minute: int
    is_active: bool = True

class AODEConfig:
    """Main configuration class with validation."""
    
    def __init__(self) -> None:
        # Core system settings
        self.DEBUG: bool = os.getenv('AODE_DEBUG', 'False').lower() == 'true'
        self.SYSTEM_NAME: str = "AODE v1.0"
        
        # Firebase configuration (CRITICAL ECOSYSTEM CONSTRAINT)
        self.FIREBASE_CREDENTIALS_PATH: str = os.getenv('FIREBASE_CREDENTIALS_PATH', '')
        self.FIREBASE_PROJECT_ID: str = os.getenv('FIREBASE_PROJECT_ID', '')
        
        # Data collection settings
        self.DEFAULT_POLLING_INTERVAL: int = int(os.getenv('POLLING_INTERVAL', '300'))
        self.MAX_RETRIES: int = 3
        self.RETRY_DELAY: float = 2.0
        
        # Trading parameters
        self.SUPPORTED_ASSET_CLASSES: list[AssetClass] = [
            AssetClass.CRYPT0,
            AssetClass.EQUITY,
            AssetClass.FOREX
        ]
        
        # Model thresholds
        self.OPPORTUNITY_CONFIDENCE_THRESHOLD: float = 0.75
        self.ANOMALY_Z_SCORE_THRESHOLD: float = 3.0
        
        # Data source configurations
        self.DATA_SOURCES: Dict[str, DataSourceConfig] = {
            'binance': DataSourceConfig(
                name='Binance',
                base_url='https://api.binance.com',
                api_key_env_var='BINANCE_API_KEY',
                rate_limit_per_minute=1200
            ),
            'alpha_vantage': DataSourceConfig(
                name='Alpha Vantage',
                base_url='https://www.alphavantage.co/query',
                api_key_env_var='ALPHA_VANTAGE_API_KEY',
                rate_limit_per_minute=5
            ),
            'polygon': DataSourceConfig(
                name='Polygon.io',
                base_url='https://api.polygon.io',
                api_key_env_var='POLYGON_API_KEY',
                rate_limit_per_minute=5
            )
        }
        
        # Validation
        self._validate_config()
    
    def _validate_config(self) -> None:
        """Validate critical configuration parameters."""
        errors = []
        
        if not self.FIREBASE_CREDENTIALS_PATH:
            errors.append("FIREBASE_CREDENTIALS_PATH environment variable not set")
        elif not os.path.exists(self.FIREBASE_CREDENTIALS_PATH):
            errors.append(f"Firebase credentials file not found at {self.FIREBASE_CREDENTIALS_PATH}")
        
        if not self.FIREBASE_PROJECT_ID:
            errors.append("FIREBASE_PROJECT_ID environment variable not set")
        
        for source_name, config in self.DATA_SOURCES.items():
            if config.is_active and not os.getenv(config.api_key_env_var):
                errors.append(f"API key for {source_name} ({config.api_key_env_var}) not found in environment")
        
        if errors:
            error_msg = "Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in errors)
            logging.critical(error_msg)
            raise ValueError(error_msg)
    
    def get_api_key(self, source_name: str) -> Optional[str]:
        """Safely retrieve API key for a data source."""
        if source_name not in self.DATA_SOURCES:
            logging.error(f"Unknown data source: {source_name}")
            return None
        
        return os.getenv(self.DATA_SOURCES[source_name].api_key_env_var)

# Singleton instance for global access
config = AODEConfig()