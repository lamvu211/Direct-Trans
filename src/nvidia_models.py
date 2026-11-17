"""NVIDIA NIM model list — fixed catalog (no API fetch)."""

from __future__ import annotations

from constants import NVIDIA_DEFAULT_MODEL

# Load Models for NVIDIA NIM: static list only (per product requirement).
NVIDIA_MODEL_CHOICES: tuple[str, ...] = (NVIDIA_DEFAULT_MODEL,)


def list_nvidia_model_choices() -> list[str]:
    return list(NVIDIA_MODEL_CHOICES)