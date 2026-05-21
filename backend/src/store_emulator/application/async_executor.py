"""Shared ThreadPoolExecutor for background work — simulation + layout/persona generation share this pool."""

from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=10)
