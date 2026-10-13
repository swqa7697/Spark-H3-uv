"""Ampere SM86 fused Spark kernel.

SM86 supports the warp MMA and cp.async instructions used by the SM80
implementation. CuTe compiles the inherited mainloop for the active device.
"""

from .spark_reweight_sm80 import SparkReweightForwardSm80


class SparkReweightForwardSm86(SparkReweightForwardSm80):
    """Compile the Ampere cp.async Spark mainloop for SM86."""


__all__ = ["SparkReweightForwardSm86"]
