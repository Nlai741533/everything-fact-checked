#!/usr/bin/env python3
"""Check that all version numbers in the repo are aligned."""
import json
import re
import sys
import tomllib

versions = {}

# plugin.json
with open(".claude-plugin/plugin.json") as f:
    versions["plugin.json"] = json.load(f)["version"]

# marketplace.json
with open(".claude-plugin/marketplace.json") as f:
    versions["marketplace.json"] = json.load(f)["plugins"][0]["version"]

# pyproject.toml
with open("pyproject.toml", "rb") as f:
    versions["pyproject.toml"] = tomllib.load(f)["project"]["version"]

# __init__.py
with open("src/efc/__init__.py") as f:
    m = re.search(r'__version__\s*=\s*["\']([^"\']+)', f.read())
    versions["__init__.py"] = m.group(1)

# Print all
for loc, ver in versions.items():
    print(f"  {loc:20s} {ver}")

# Check consistency
values = set(versions.values())
if len(values) != 1:
    print(f"\nERROR: versions differ: {dict(versions)}")
    sys.exit(1)

print(f"\nAll versions aligned: {values.pop()} ✅")
