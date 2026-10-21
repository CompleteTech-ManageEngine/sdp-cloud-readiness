#!/usr/bin/env python3
"""Start the read-only ServiceDesk Plus migration assessment."""

import sys

if sys.version_info < (3, 10):
    raise SystemExit("Python 3.10 or newer is required.")

from sdp_audit.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
