from __future__ import annotations

import sys

from src.snra.cli_v0_1 import main


if __name__ == "__main__":
    argv = sys.argv[1:]
    if argv and argv[0] in {"validate", "score", "audit-card", "demo"}:
        raise SystemExit(main(argv))
    command = "audit-card" if "--input-tsv" in argv else "demo"
    raise SystemExit(main([command, *argv]))
