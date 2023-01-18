from __future__ import annotations

import pytest

from ignore_flake8_error import _add_code_to_comment
from ignore_flake8_error import _add_comments
from ignore_flake8_error import main


def test_main(tmp_path):
    python_module = tmp_path / 't.py'
    python_module.write_text("""\
import sys
from json import *  # additional comment
from os import *  # noqa: F403
from pathlib import *  # noqa: F403  # additional comment
""")

    ret = main(('F401', str(python_module)))

    assert ret == 1
    assert python_module.read_text() == """\
import sys  # noqa: F401
from json import *  # additional comment  # noqa: F401
from os import *  # noqa: F401,F403
from pathlib import *  # noqa: F401,F403  # additional comment
"""


def test_main_no_violations(tmp_path):
    src = """\
def foo():
    print('hello there')
"""

    python_module = tmp_path / 't.py'
    python_module.write_text(src)

    ret = main(('F401', str(python_module)))

    assert ret == 0

    assert python_module.read_text() == src


@pytest.mark.parametrize(
    'comment, expected',
    (
        ('# some comment', '# some comment  # noqa: ABC123'),
        ('# noqa: DEF456', '# noqa: ABC123,DEF456'),
        (
            '# some comment  # noqa: DEF456',
            '# some comment  # noqa: ABC123,DEF456',
        ),
        (
            '# noqa: DEF456  # some comment',
            '# noqa: ABC123,DEF456  # some comment',
        ),
    ),
)
def test_add_code_to_comment(comment, expected):
    assert _add_code_to_comment(comment, 'ABC123') == expected


@pytest.mark.xfail
def test_add_comments():
    src = """\
# a single-line statement on line 2
foo = 'bar'

# a function on line 5
def baz(
    a: int,
    b: int,
) -> str: ...

# a multi-line string on line 11
s = '''
hello there
'''
"""

    print(src)

    assert _add_comments(src, [2, 5, 1], 'ABC123') == """\
# a single-line statement on line 2
foo = 'bar'  # noqa: ABC123

# a function on line 5
def baz(  # noqa: ABC123
    a: int,
    b: int,
) -> str: ...

# a multi-line string on line 11
s = '''
hello there
'''  # noqa: ABC123
"""
