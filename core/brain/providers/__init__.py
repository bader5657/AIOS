"""Concrete inference providers owned by AIOS Brain."""

from .ollama import OllamaInferenceProvider, OllamaProviderConfig

__all__ = ["OllamaInferenceProvider", "OllamaProviderConfig"]
