from __future__ import annotations

import argparse
import subprocess
import sys
from collections import defaultdict
from typing import Sequence

from tokenize_rt import reversed_enumerate
from tokenize_rt import src_to_tokens
from tokenize_rt import Token
from tokenize_rt import tokens_to_src


def _run_flake8(code: str, filenames: Sequence[str]) -> dict[str, list[int]]:
    proc = subprocess.run(
        (
            sys.executable, '-mflake8',
            '--select', code,
            '--format', '%(path)s %(row)s',
            *filenames,
        ),
        capture_output=True,
        text=True,
    )

    # extract filenames and line numbers
    results: dict[str, list[int]] = defaultdict(list)
    for line in proc.stdout.splitlines():
        filename_, lineno_ = line.rsplit(maxsplit=1)
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
    tokens = src_to_tokens(src)
    lines = set(linenos)

    for idx, token in reversed_enumerate(tokens):
        if token.line not in lines:
            continue
        if not token.src.strip():
            continue

        if token.name == 'COMMENT':
            new_comment = _add_code_to_comment(token.src, code)
            tokens[idx] = tokens[idx]._replace(src=new_comment)
        else:
            tokens.insert(idx+1, Token('COMMENT', f'# noqa: {code}'))
            tokens.insert(idx+1, Token('UNIMPORTANT_WS', '  '))

        lines.remove(token.line)

    return tokens_to_src(tokens)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('code')
    parser.add_argument('filenames', nargs='*')
    args = parser.parse_args(argv)

    print('-> running flake8', file=sys.stderr)
    violations = _run_flake8(args.code, args.filenames)

    if not violations:
        print('no violations found', file=sys.stderr)
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
