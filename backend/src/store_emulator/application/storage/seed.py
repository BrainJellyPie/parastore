import logging
import shutil
from pathlib import Path

from .io import DATA_DIR

logger = logging.getLogger(__name__)

# backend/src/store_emulator/application/storage/seed.py → backend/sample_data
_SAMPLE_DATA_DIR = Path(__file__).resolve().parents[4] / "sample_data"


def seed_sample_projects() -> int:
    """Copy every `proj_*` directory under `backend/sample_data/` into `.data/`
    if a project of the same id doesn't already exist locally.

    Intended to give a fresh clone a ready-to-explore project on first boot.
    Existing projects are never overwritten, so subsequent boots are no-ops
    and user edits are preserved.
    """
    if not _SAMPLE_DATA_DIR.is_dir():
        return 0

    data_root = Path(DATA_DIR)
    data_root.mkdir(parents=True, exist_ok=True)

    copied = 0
    for sample in sorted(_SAMPLE_DATA_DIR.iterdir()):
        if not sample.is_dir() or not sample.name.startswith("proj_"):
            continue
        destination = data_root / sample.name
        if destination.exists():
            continue
        shutil.copytree(sample, destination)
        logger.info(f"server start: seeded sample project {sample.name}")
        copied += 1
    return copied
