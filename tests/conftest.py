import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pytest  # noqa: E402

from classmate.config import AppConfig  # noqa: E402
from classmate.courses import CourseCatalog  # noqa: E402


@pytest.fixture
def cfg(tmp_path):
    return AppConfig(str(tmp_path / "config.json"))


@pytest.fixture
def catalog(cfg):
    return CourseCatalog(
        [ROOT / "data" / "courses_a.json", ROOT / "data" / "courses_b.json"], cfg)


@pytest.fixture
def phrase():
    from classmate.phrase_engine import PhraseEngine
    pe = PhraseEngine(sensitivity=55)
    pe.set_names(["李小明", "Xiao Ming", "小明"])
    return pe
