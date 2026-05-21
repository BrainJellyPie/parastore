from store_emulator.domain.config import SimulationConfig
from store_emulator.application.config import local_config

_config: SimulationConfig | None = None


def get_config() -> SimulationConfig:
    global _config
    if _config is None:
        _config = local_config()
    return _config
