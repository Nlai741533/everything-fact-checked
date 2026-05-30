#!/usr/bin/env python3
"""Backward-compatible entry point — delegates to the packaged module."""
from efc._check_links import main
if __name__ == "__main__":
    raise SystemExit(main())
