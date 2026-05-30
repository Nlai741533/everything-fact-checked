#!/usr/bin/env python3
"""Backward-compatible entry point — delegates to the packaged module."""
from efc._extract_claims import main
if __name__ == "__main__":
    raise SystemExit(main())
