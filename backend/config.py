"""Configuration management for TEMA."""

import os
import json
from dataclasses import dataclass, asdict
from typing import Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class TransportConfig:
    interface: str = 'eth0'
    port: int = 5353
    buffer_size: int = 1048576  # 1MB
    timeout: float = 30.0
    max_payload_size: int = 65536


@dataclass
class SecurityConfig:
    enable_encryption: bool = True
    enable_tls: bool = True
    certificate_path: str = '/etc/tema/certs/server.crt'
    key_path: str = '/etc/tema/certs/server.key'
    trusted_peers_path: str = '/etc/tema/peers.json'
    key_exchange_algorithm: str = 'ECDH'


@dataclass
class AIConfig:
    model_cache_dir: str = '/tmp/tema_models'
    enable_music_analysis: bool = True
    analyzer_sample_rate: int = 22050
    enable_recommendations: bool = True
    recommendation_model: str = 'collaborative'


@dataclass
class MusicConfig:
    library_path: str = '~/Music'
    supported_formats: tuple = ('.mp3', '.flac', '.wav', '.ogg')
    streaming_bitrate: int = 320  # kbps
    cache_dir: str = '/tmp/tema_music_cache'
    chunk_size: int = 8192  # bytes


@dataclass
class TEMAConfig:
    """Master configuration for TEMA application."""
    device_name: str = 'TEMA-Device'
    device_id: Optional[int] = None
    log_level: str = 'INFO'
    log_file: Optional[str] = None
    
    transport: TransportConfig = None
    security: SecurityConfig = None
    ai: AIConfig = None
    music: MusicConfig = None
    
    def __post_init__(self):
        if self.transport is None:
            self.transport = TransportConfig()
        if self.security is None:
            self.security = SecurityConfig()
        if self.ai is None:
            self.ai = AIConfig()
        if self.music is None:
            self.music = MusicConfig()
    
    @classmethod
    def from_file(cls, config_path: str) -> 'TEMAConfig':
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                data = json.load(f)
            
            config = cls(
                device_name=data.get('device_name', 'TEMA-Device'),
                device_id=data.get('device_id'),
                log_level=data.get('log_level', 'INFO'),
                log_file=data.get('log_file')
            )
            
            # Load sub-configs if provided
            if 'transport' in data:
                config.transport = TransportConfig(**data['transport'])
            if 'security' in data:
                config.security = SecurityConfig(**data['security'])
            if 'ai' in data:
                config.ai = AIConfig(**data['ai'])
            if 'music' in data:
                config.music = MusicConfig(**data['music'])
            
            logger.info(f"Loaded config from {config_path}")
            return config
        
        except Exception as e:
            logger.warning(f"Failed to load config file: {e}, using defaults")
            return cls()
    
    def to_dict(self) -> dict:
        """Convert config to dictionary."""
        return {
            'device_name': self.device_name,
            'device_id': self.device_id,
            'log_level': self.log_level,
            'log_file': self.log_file,
            'transport': asdict(self.transport),
            'security': asdict(self.security),
            'ai': asdict(self.ai),
            'music': asdict(self.music)
        }
    
    def save(self, config_path: str) -> bool:
        """Save configuration to JSON file."""
        try:
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w') as f:
                json.dump(self.to_dict(), f, indent=2)
            logger.info(f"Saved config to {config_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            return False
