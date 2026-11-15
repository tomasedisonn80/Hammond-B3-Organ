#!/usr/bin/env python3
"""Explicit command for one synthetic offline fractional-contact report."""

from __future__ import annotations

import argparse
import sys
import time

import contact_switching_io as contact_io


class _Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise ValueError(message)


class _Once(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if getattr(namespace, self.dest, None) is not None:
            raise ValueError(f"{option_string} may occur only once")
        setattr(namespace, self.dest, values)


def _diagnostic(error: BaseException) -> None:
    text = " ".join(str(error).split())
    text = "".join(character if character.isprintable() else "?" for character in text)
    text = text[:480] or type(error).__name__
    print("contact-switching: " + text, file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    started_at = time.perf_counter()
    parser = _Parser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--input", required=True, action=_Once, metavar="FILE")
    parser.add_argument("--factor", required=True, action=_Once,
                        choices=("32", "64", "128", "256"), metavar="L")
    parser.add_argument("--output", required=True, action=_Once, metavar="REPORT")
    try:
        arguments = parser.parse_args(argv)
        hashes = contact_io.implementation_hashes()
        plan = contact_io.preflight_paths(arguments.input, arguments.output)
        document = contact_io.load_input(plan.input_path, expected_signature=plan.input_signature)
        report = contact_io.build_report(document, int(arguments.factor), started_at=started_at,
                                         source_hashes=hashes)
        contact_io.atomic_write_report(plan, report)
        return 0
    except KeyboardInterrupt:
        _diagnostic(ValueError("interrupted; invocation incomplete"))
        return 130
    except Exception as error:
        _diagnostic(error)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
