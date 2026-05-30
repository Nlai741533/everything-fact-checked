#!/usr/bin/env python3
"""Backward-compatible entry point — delegates to the packaged module."""
from efc._verify_source import main
if __name__ == "__main__":
    raise SystemExit(main())
