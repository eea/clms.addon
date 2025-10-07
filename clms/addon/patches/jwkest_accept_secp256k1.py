"""
Monkeypatch for jwkest.ecc.NISTEllipticCurve.by_name
to treat 'secp256k1' as equivalent to 'P-256'.

This reproduces the quick fix tested directly in jwkest/ecc.py.
It prevents 'Unknown curve secp256k1' errors during EU Login validation.
"""

import logging
from jwkest.ecc import NISTEllipticCurve

log = logging.getLogger(__name__)

# keep reference to the original implementation
_original_by_name = NISTEllipticCurve.by_name


def _patched_by_name(name):
    """Patched version that accepts secp256k1 as P-256."""
    # convert bytes to str for consistent comparison
    if isinstance(name, bytes):
        name = name.decode("utf-8")

    if name == "secp256k1":
        log.info("[PATCH] 'secp256k1' as 'P-256' for jwkest compatibility")
        return NISTEllipticCurve(256)

    # fallback to the original behavior
    return _original_by_name(name)


# apply the patch
NISTEllipticCurve.by_name = staticmethod(_patched_by_name)
log.info("[PATCH] Applied jwkest 'secp256k1' → 'P-256' compatibility fix")
