"""Checkout Lambda. Reads a feature flag from AWS AppConfig (via the AppConfig
Lambda extension on localhost:2772) so behaviour can change *independently of
code* (VOIS: Versioned, Observable, Independent, Safe), with a SAFE DEFAULT
when the flag can't be read."""
import json
import os
import urllib.request

VERSION = os.environ.get("AWS_LAMBDA_FUNCTION_VERSION", "dev")
FLAG_URL = os.environ.get(
    "APPCONFIG_URL",
    "http://localhost:2772/applications/checkout/environments/prod/configurations/flags",
)
SAFE_DEFAULTS = {"recommendations": {"enabled": False}}  # explicit safe default


def flags() -> dict:
    try:
        with urllib.request.urlopen(FLAG_URL, timeout=0.2) as r:
            return json.loads(r.read())
    except Exception:  # degrade, don't fail: config is an optional dependency here
        return SAFE_DEFAULTS


def lambda_handler(event, context):
    f = flags()
    body = {"ok": True, "version": VERSION}
    if f.get("recommendations", {}).get("enabled"):
        body["recommendations"] = ["sku-123", "sku-456"]
    return {
        "statusCode": 200,
        # client-focused change supervision: expose the serving version
        "headers": {"x-served-by-version": VERSION},
        "body": json.dumps(body),
    }
