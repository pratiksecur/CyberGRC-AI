"""Root pytest configuration for the backend test suite.

This file is loaded before tests/conftest.py, so the setting below is in
place before the application (and its password hashing context) is imported.
"""

import os

# Cheapest bcrypt cost for tests. Production uses 12 (see app/auth/hashing.py).
os.environ.setdefault("BCRYPT_ROUNDS", "4")