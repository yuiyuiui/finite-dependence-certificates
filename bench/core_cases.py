"""Bounded independent enumeration of the same labelled path-color orbits."""

from finite_dependence import proper_patterns
from finite_dependence.combinatorics import exhaustive_patterns


def make(case, variant):
    n = {"small": 5, "medium": 7, "large": 8}[case]
    adjacency = [set() for _ in range(n)]
    for i in range(n - 1):
        adjacency[i].add(i + 1)
        adjacency[i + 1].add(i)
    expected = exhaustive_patterns(adjacency, 4)

    def call():
        return (
            exhaustive_patterns(adjacency, 4)
            if variant == "reference"
            else proper_patterns(adjacency, 4)
        )

    def validate(result):
        if tuple(sorted(result)) != expected:
            raise ArithmeticError("Full independent color-orbit enumeration disagrees")
        return {"passed": True, "patterns": len(expected)}

    return (
        call,
        validate,
        {
            "vertices": n,
            "colors": 4,
            "geometry": "labelled path",
            "variant": variant,
            "cost_scope": "pattern enumeration only; not LP solve",
        },
    )
