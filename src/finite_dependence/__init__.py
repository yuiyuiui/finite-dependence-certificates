"""Bounded finite tree-coloring constraints and exact certificate replay."""

from .combinatorics import proper_patterns
from .model import Hierarchy, LinearSystem, build_hierarchy
from .certificate import certificate_from_multipliers, search_infeasibility, verify_certificate

__version__ = "0.1.0"
__all__ = [
    "Hierarchy",
    "LinearSystem",
    "build_hierarchy",
    "proper_patterns",
    "certificate_from_multipliers",
    "search_infeasibility",
    "verify_certificate",
]
