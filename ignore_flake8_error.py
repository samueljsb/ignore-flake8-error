from __future__ import annotations

import argparse
import subprocess
import sys
from collections import defaultdict
from typing import Sequence

from tokenize_rt import src_to_tokens
from tokenize_rt import Token
from tokenize_rt import tokens_to_src


def _run_flake8(code: str, filenames: Sequence[str]) -> dict[str, list[int]]:
    proc = subprocess.run(
        (
            'flake8', '--select', code,
            '--format', '%(path)s %(row)s',
            *filenames,
        ),
        capture_output=True,
        text=True,
    )

    # extract filenames and line numbers
    results: dict[str, list[int]] = defaultdict(list)
    for line in proc.stdout.splitlines():
        filename_, lineno_ = line.split()
        results[filename_].append(int(lineno_))

    return results


def _add_code_to_comment(comment: str, code: str) -> str:
    if 'noqa: ' in comment:
        return comment.replace(
            'noqa: ', f'noqa: {code},',
        )
    else:
        return comment + f'  # noqa: {code}'


def _add_comments(src: str, linenos: list[int], code: str) -> str:
    lines = src.splitlines(keepends=True)

    for lineno in linenos:
        line = lines[lineno - 1]
        tokens = src_to_tokens(line)

        if tokens[-3].name == 'COMMENT':
            old_comment = tokens[-3].src
            new_comment = _add_code_to_comment(old_comment, code)
            tokens[-3] = tokens[-3]._replace(src=new_comment)
        else:
            tokens = [
                *tokens[:-2],
                Token('UNIMPORTANT_WS', '  '),
                Token('COMMENT', f'# noqa: {code}'),
                *tokens[-2:],
            ]

        lines[lineno - 1] = tokens_to_src(tokens)

    return ''.join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('code')
    parser.add_argument('filenames', nargs='*')
    args = parser.parse_args(argv)

    print('-> running flake8', file=sys.stderr)
    violations = _run_flake8(args.code, args.filenames)

    if not violations:
        return 0

    print(f'found violations in {len(violations)} files', file=sys.stderr)

    print('-> adding noqa comments', file=sys.stderr)
    ret = 0
    for filename, linenos in violations.items():
        print(filename, file=sys.stderr)
        with open(filename) as f:
            src = f.read()

        src_with_comments = _add_comments(src, linenos, args.code)

        with open(filename, 'w') as f:
            f.write(src_with_comments)

        ret |= src_with_comments != src

    return ret


if __name__ == '__main__':
    raise SystemExit(main())
