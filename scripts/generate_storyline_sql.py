#!/usr/bin/env python3
"""
Verify a storyline pack and generate seed SQL with inlined mission markdown.

Prefer the installed entry point when available:
  generate_storyline orientation
  generate_storyline orientation --check
"""

from __future__ import annotations

from radspion.storyline_cli import main

if __name__ == "__main__":
    main()
