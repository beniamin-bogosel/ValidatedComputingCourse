"""Report the software and floating-point assumptions used by the course."""

from importlib.metadata import version
import platform
import sys
import gmpy2
import flint


def report():
    """Return printable environment information without changing arithmetic contexts."""
    packages = ("numpy", "matplotlib", "gmpy2", "python-flint", "jupytext", "ipykernel")
    return {"Python": platform.python_version(), "platform": platform.platform(),
            **{name: version(name) for name in packages},
            "GMP": gmpy2.mp_version(), "MPFR": gmpy2.mpfr_version(),
            "MPC": gmpy2.mpc_version(), "FLINT": flint.__FLINT_VERSION__}


def require_binary64():
    """Check the representation assumptions of the binary64 teaching examples."""
    info = sys.float_info
    if (info.radix, info.mant_dig, info.max_exp, info.min_exp) != (2, 53, 1024, -1021):
        raise RuntimeError("These examples require IEEE-style binary64 Python floats.")

