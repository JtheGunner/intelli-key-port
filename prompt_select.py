#!/usr/bin/env python3
"""
Interactive checkbox picker - stdlib only, POSIX + Windows.

    from prompt_select import choose, PromptUnavailable

    picked = choose(["VS Code", "Cursor"], title="Import into which IDEs?")
    # -> list of selected indices (e.g. [0, 1]), or None if the user cancelled

Keys:  up/down (or k/j) move, space toggles, a toggles all, enter confirms,
esc / q / ctrl-c cancels.  Every entry starts checked unless `preselected`
says otherwise.  Rows are colour-coded (green [x], dim [ ], cyan cursor);
set NO_COLOR to disable.

Raises PromptUnavailable when there is no interactive terminal to draw on;
callers are expected to catch it and fall back to a non-interactive default.
"""

from __future__ import annotations

import os
import sys
from typing import Iterable, Sequence

__all__ = ["choose", "PromptUnavailable"]

_HINT = "up/down move · space toggle · a all · enter confirm · esc cancel"

# ANSI styling - suppressed when NO_COLOR is set (https://no-color.org).
_COLOR = os.environ.get("NO_COLOR") is None
_RESET = "\x1b[0m" if _COLOR else ""
_BOLD = "\x1b[1m" if _COLOR else ""
_DIM = "\x1b[2m" if _COLOR else ""
_GREEN = "\x1b[32m" if _COLOR else ""
_CYAN = "\x1b[36m" if _COLOR else ""


def _row(pointer_on: bool, checked: bool, label: str) -> str:
    pointer = f"{_CYAN}{_BOLD}❯{_RESET}" if pointer_on else " "
    box = f"{_GREEN}[x]{_RESET}" if checked else f"{_DIM}[ ]{_RESET}"
    text = f"{_BOLD}{label}{_RESET}" if pointer_on else label
    return f"{pointer} {box} {text}"


class PromptUnavailable(Exception):
    """Raised when an interactive terminal UI cannot be started."""


def choose(
    options: Sequence[str],
    *,
    title: str = "",
    preselected: Iterable[int] | None = None,
) -> list[int] | None:
    """Show a checkbox list; return the chosen indices, or None if cancelled."""
    labels = list(options)
    if not labels:
        return []

    if preselected is None:
        selected = [True] * len(labels)
    else:
        pre = set(preselected)
        selected = [i in pre for i in range(len(labels))]

    if not (sys.stdin.isatty() and sys.stdout.isatty()):
        raise PromptUnavailable("stdin/stdout is not a tty")

    try:
        import msvcrt  # noqa: F401  (Windows only)
    except ImportError:
        return _run_posix(labels, selected, title)
    return _run_windows(labels, selected, title)


def _interact(labels, selected, title, read_key) -> list[int] | None:
    """Shared render + key loop, driven by a platform-specific read_key()."""
    cursor = 0
    n = len(labels)
    prev_lines = 0

    def render() -> None:
        nonlocal prev_lines
        lines = []
        if title:
            lines.append(f"{_BOLD}{title}{_RESET}")
        for i, label in enumerate(labels):
            lines.append(_row(i == cursor, selected[i], label))
        lines.append("")
        lines.append(f"{_DIM}  {_HINT}{_RESET}")

        out = f"\x1b[{prev_lines}A" if prev_lines else ""
        out += "".join(f"\x1b[2K{line}\r\n" for line in lines)
        sys.stdout.write(out)
        sys.stdout.flush()
        prev_lines = len(lines)

    sys.stdout.write("\x1b[?25l")  # hide cursor
    try:
        render()
        while True:
            try:
                key = read_key()
            except KeyboardInterrupt:
                return None

            if key in ("up", "k"):
                cursor = (cursor - 1) % n
            elif key in ("down", "j"):
                cursor = (cursor + 1) % n
            elif key == " ":
                selected[cursor] = not selected[cursor]
            elif key in ("a", "A"):
                fill = not all(selected)
                selected[:] = [fill] * n
            elif key in ("\r", "\n"):
                return [i for i, on in enumerate(selected) if on]
            elif key in ("\x1b", "q", "Q", "\x03"):
                return None
            render()
    finally:
        sys.stdout.write("\x1b[?25h\r\n")  # show cursor, drop to a fresh line
        sys.stdout.flush()


def _run_posix(labels, selected, title) -> list[int] | None:
    import select as _select
    import termios
    import tty

    fd = sys.stdin.fileno()
    try:
        old_attr = termios.tcgetattr(fd)
    except (termios.error, ValueError) as exc:
        raise PromptUnavailable(f"no termios: {exc}") from exc

    def read_key() -> str:
        # Raw byte reads only - mixing buffered sys.stdin with select() on the
        # fd swallows escape sequences (the "[" and "B" land in the buffer,
        # select sees nothing, and a bare arrow key reads as ESC/cancel).
        ch = os.read(fd, 1)
        if ch != b"\x1b":
            return ch.decode("utf-8", "replace")
        ready, _, _ = _select.select([fd], [], [], 0.05)
        if not ready:
            return "\x1b"
        rest = os.read(fd, 2)
        if rest[:1] != b"[":
            return "\x1b"
        return {b"A": "up", b"B": "down"}.get(rest[1:2], "")

    try:
        tty.setcbreak(fd)
        return _interact(labels, selected, title, read_key)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_attr)


def _run_windows(labels, selected, title) -> list[int] | None:
    import msvcrt

    def read_key() -> str:
        ch = msvcrt.getwch()
        if ch == "\x03":  # ctrl-c is delivered as a byte here
            raise KeyboardInterrupt
        if ch in ("\x00", "\xe0"):  # arrow / function key prefix
            return {"H": "up", "P": "down"}.get(msvcrt.getwch(), "")
        return ch

    return _interact(labels, selected, title, read_key)
