"""edit-slice's old flat module names must keep resolving to the package.

Seventy-nine scripts import them, and their recorded results depend on the same
code. If these break, numbers stop being comparable across the two projects.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

#: edit-slice has lived at two paths. This checked only the first, so once the
#: project moved under open-concept-lab these three tests SKIPPED on every run
#: and the suite still reported green -- a guard that stops guarding without
#: ever failing. Candidates are tried in order; EDITSLICE_SRC overrides.
_CANDIDATES = (
    Path(__file__).resolve().parents[2] / "edit-slice" / "src",
    Path(__file__).resolve().parents[2] / "open-concept-lab" / "ai" / "edit-slice" / "src",
)


def _find_edit_slice_src() -> Path | None:
    override = os.environ.get("EDITSLICE_SRC")
    if override:
        return Path(override) if Path(override).is_dir() else None
    return next((c for c in _CANDIDATES if c.is_dir()), None)


EDIT_SLICE_SRC = _find_edit_slice_src()
pytestmark = pytest.mark.skipif(
    EDIT_SLICE_SRC is None,
    reason=f"edit-slice not found at any of {[str(c) for c in _CANDIDATES]}; "
           "set EDITSLICE_SRC to point at its src/")


@pytest.fixture(autouse=True)
def _flat_namespace():
    sys.path.insert(0, str(EDIT_SLICE_SRC))
    yield
    sys.path.remove(str(EDIT_SLICE_SRC))


def test_old_names_are_the_package_objects_not_copies() -> None:
    import editreach.remote as pkg
    import remote as shim                                     # type: ignore
    assert shim.connect is pkg.connect
    assert shim.score_pairs is pkg.score_pairs


def test_the_private_names_scripts_import_still_resolve() -> None:
    from remote import _is_flaky_remote, _quiet_stdout        # type: ignore
    assert callable(_quiet_stdout) and callable(_is_flaky_remote)


def test_edit_forwards_to_rome() -> None:
    import editreach.rome as pkg
    from edit import LAYER, subject_last_index                # type: ignore
    assert subject_last_index is pkg.subject_last_index
    assert LAYER == pkg.LAYER == 5
