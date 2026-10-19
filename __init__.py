"""ComfyUI entry point for the Spark-H3 custom node."""

import os
from pathlib import Path

if __package__:
    from .comfyui_nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS
else:  # pytest/importlib may load a custom-node root as ``__init__``.
    from comfyui_nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

WEB_DIRECTORY = "./web"

# Ref2VA runners load the released standalone Spark-H3 package alongside this
# development tree. Avoid registering two implementations under the same ids.
if (
    os.environ.get("MINIMAX_H3_REF2VA_ONLY") == "1"
    and Path(__file__).resolve().parent.name == "MiniMax-H3"
):
    _SPARK_NODE_NAMES = {
        "MiniMaxH3SparkAttentionSM120",
        "MiniMaxH3SparkAttentionSM89",
        "MiniMaxH3SparkAttentionSM86",
        "MiniMaxH3SolAttentionSM120",
    }
    NODE_CLASS_MAPPINGS = {
        name: node for name, node in NODE_CLASS_MAPPINGS.items()
        if name not in _SPARK_NODE_NAMES
    }
    NODE_DISPLAY_NAME_MAPPINGS = {
        name: display for name, display in NODE_DISPLAY_NAME_MAPPINGS.items()
        if name not in _SPARK_NODE_NAMES
    }

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
