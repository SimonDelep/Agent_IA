import os

API_BASE_URL = os.getenv("NORDTRAIL_API_URL", "http://127.0.0.1:8001").rstrip("/")
REQUEST_TIMEOUT = float(os.getenv("NORDTRAIL_API_TIMEOUT", "30"))
