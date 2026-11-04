"""Run the repository's test functions without requiring pytest."""
from __future__ import annotations

import inspect
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
import test_main  # noqa: E402


def main() -> int:
    tests = [
        fn for name, fn in inspect.getmembers(test_main, inspect.isfunction)
        if name.startswith("test_")
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print(f"{len(tests)} tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
