"""Exact finite-cylinder constraints for a local tree-invariant coloring ansatz."""

from dataclasses import dataclass
from fractions import Fraction as Q
import hashlib
import json

from .combinatorics import (
    enumerate_trees,
    normalize,
    components_after_delete,
    proper_partitions,
    star_density,
)


@dataclass(frozen=True)
class Hierarchy:
    colors: int = 4
    max_vertices: int = 6
    max_degree: int = 3

    def __post_init__(self):
        for key, value in vars(self).items():
            if isinstance(value, bool) or not isinstance(value, int):
                raise ValueError(f"{key} must be an integer")
        if not 1 <= self.max_vertices <= 8 or not 1 <= self.max_degree <= 3:
            raise ValueError("Supported envelope: 1..8 vertices, maximum degree 1..3")
        if not self.max_degree < self.colors <= 16:
            raise ValueError("Require max_degree < colors <=16 for forced star laws")


@dataclass(frozen=True)
class LinearSystem:
    hierarchy: Hierarchy
    variables: tuple
    rows: tuple
    rhs: tuple
    constant_checks: int

    @property
    def digest(self):
        record = [
            vars(self.hierarchy),
            self.variables,
            [[[i, str(c)] for i, c in row] for row in self.rows],
            [str(v) for v in self.rhs],
        ]
        return hashlib.sha256(json.dumps(record, separators=(",", ":")).encode()).hexdigest()

    @property
    def shape(self):
        return len(self.rows), len(self.variables)


def build_hierarchy(hierarchy=Hierarchy()):
    """Build exact A x=b with x>=0, preserving specified-word probabilities.

    Unknowns are q^n times specified-color cylinder probabilities. The rules
    assume proper coloring, color-permutation and tree-isomorphism invariance,
    one-dependence and their forced star laws. Finite feasibility never implies
    an infinite process. The linear envelope is at most eight vertices.
    """
    if not isinstance(hierarchy, Hierarchy):
        raise TypeError("Pass a Hierarchy configuration")
    q = hierarchy.colors
    trees = enumerate_trees(hierarchy.max_vertices, hierarchy.max_degree)
    by_code = {t.code: t for t in trees}
    variables = {}
    for t in trees:
        if t.star_center is None:
            for c in sorted(set(t.orbit.values())):
                if max(c) < q:
                    variables[t.code, c] = len(variables)
    rows, rhs, seen = [], [], set()
    constant_checks = 0

    def item(t, colors):
        colors = normalize(colors)
        if t.star_center is not None:
            return None, star_density(t, colors, q)
        return variables[t.code, t.orbit[colors]], Q(1)

    for tree in trees:
        n = len(tree.adj)
        if n == 1:
            continue
        for vertex in range(n):
            rest = tuple(u for u in range(n) if u != vertex)
            reduced = tuple(
                frozenset(rest.index(w) for w in tree.adj[u] if w != vertex) for u in rest
            )
            components = components_after_delete(tree, vertex)
            for colors in proper_partitions(reduced, q):
                k = 1 + max(colors)
                full = dict(zip(rest, colors))
                row, constant = {}, Q(0)
                for color in range(k + (k < q)):
                    if any(full[u] == color for u in tree.adj[vertex]):
                        continue
                    full[vertex] = color
                    index, value = item(tree, tuple(full[u] for u in range(n)))
                    multiplier = q - k if color == k else 1
                    if index is None:
                        constant += multiplier * value
                    else:
                        row[index] = row.get(index, Q(0)) + multiplier
                product, target_index = Q(q), None
                for code, order in components:
                    index, value = item(by_code[code], tuple(full[u] for u in order))
                    product *= value
                    if index is not None:
                        if target_index is not None:
                            raise ValueError("Nonlinear factor product; cannot compile as an LP")
                        target_index = index
                if target_index is not None:
                    row[target_index] = row.get(target_index, Q(0)) - product
                    target = -constant
                else:
                    target = product - constant
                terms = tuple(sorted((i, Q(c)) for i, c in row.items() if c))
                if not terms:
                    if target:
                        raise ArithmeticError("A forced-star constant identity failed")
                    constant_checks += 1
                    continue
                key = terms, target
                if key not in seen:
                    seen.add(key)
                    rows.append(terms)
                    rhs.append(target)
    return LinearSystem(hierarchy, tuple(variables), tuple(rows), tuple(rhs), constant_checks)
