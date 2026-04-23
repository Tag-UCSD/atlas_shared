from __future__ import annotations

import re

import atlas_shared


def test_version_exposed() -> None:
    assert isinstance(atlas_shared.__version__, str)
    assert atlas_shared.__version__
    assert re.fullmatch(r"\d+\.\d+\.\d+", atlas_shared.__version__)
