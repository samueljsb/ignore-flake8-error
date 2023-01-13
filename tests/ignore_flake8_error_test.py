from __future__ import annotations

from ignore_flake8_error import main


def test_ignore_flake8_error(tmp_path):
    python_module = tmp_path / 't.py'
    python_module.write_text("""\
import sys
from json import *  # additional comment
from os import *  # noqa: F403
from pathlib import *  # noqa: F403  # additional comment
""")

    main(('F401', str(python_module)))

    assert python_module.read_text() == """\
import sys  # noqa: F401
from json import *  # additional comment  # noqa: F401
from os import *  # noqa: F401,F403
from pathlib import *  # noqa: F401,F403  # additional comment
"""
