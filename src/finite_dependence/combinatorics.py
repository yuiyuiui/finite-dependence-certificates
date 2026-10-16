"""Finite tree combinatorics adapted from the AIM-583 computational seed.

Color patterns are specified-color cylinders, quotiented by color renaming and
finite tree automorphisms. This module has no solver or floating dependency.
"""

from __future__ import annotations
import itertools
from dataclasses import dataclass
from fractions import Fraction

Graph = tuple[frozenset[int], ...]


def rooted_code(adj: dict[int, set[int]], v: int, parent: int = -1) -> str:
    return "(" + "".join(sorted(rooted_code(adj, u, v) for u in adj[v] if u != parent)) + ")"


def canonical_order(adj: dict[int, set[int]]) -> tuple[str, tuple[int, ...]]:
    root = min(adj, key=lambda v: (rooted_code(adj, v), v))
    order: list[int] = []

    def visit(v: int, parent: int) -> None:
        order.append(v)
        children = sorted(
            (u for u in adj[v] if u != parent), key=lambda u: (rooted_code(adj, u, v), u)
        )
        for u in children:
            visit(u, v)

    visit(root, -1)
    return rooted_code(adj, root), tuple(order)


def normalize(colors: tuple[int, ...]) -> tuple[int, ...]:
    mapping: dict[int, int] = {}
    return tuple(mapping.setdefault(c, len(mapping)) for c in colors)


def proper_partitions(adj: Graph, q: int = 16) -> list[tuple[int, ...]]:
    out: list[tuple[int, ...]] = []

    def add(colors: tuple[int, ...], max_color: int) -> None:
        v = len(colors)
        if v == len(adj):
            out.append(colors)
            return
        forbidden = {colors[u] for u in adj[v] if u < v}
        for c in range(min(q, max_color + 2)):
            if c not in forbidden:
                add(colors + (c,), max(max_color, c))

    add((), -1)
    return out


def automorphisms(adj: Graph) -> list[tuple[int, ...]]:
    n = len(adj)
    order = sorted(range(n), key=lambda v: (-len(adj[v]), v))
    mapping = [-1] * n
    used: set[int] = set()
    out: list[tuple[int, ...]] = []

    def step(k: int) -> None:
        if k == n:
            out.append(tuple(mapping))
            return
        v = order[k]
        for w in range(n):
            if w in used or len(adj[w]) != len(adj[v]):
                continue
            if any((u in adj[v]) != (mapping[u] in adj[w]) for u in order[:k]):
                continue
            mapping[v] = w
            used.add(w)
            step(k + 1)
            used.remove(w)
            mapping[v] = -1

    step(0)
    return out


@dataclass
class Tree:
    code: str
    adj: Graph
    partitions: list[tuple[int, ...]]
    orbit: dict[tuple[int, ...], tuple[int, ...]]
    star_center: int | None


def tree_from_adj(adj: dict[int, set[int]]) -> Tree:
    code, order = canonical_order(adj)
    remap = {v: i for i, v in enumerate(order)}
    graph = tuple(frozenset(remap[u] for u in adj[v]) for v in order)
    patterns = proper_partitions(graph)
    autos = automorphisms(graph)
    orbit = {}
    for c in patterns:
        if c not in orbit:
            images = {normalize(tuple(c[p[i]] for i in range(len(c)))) for p in autos}
            representative = min(images)
            orbit.update((image, representative) for image in images)
    center = next((v for v in range(len(graph)) if len(graph[v]) == len(graph) - 1), None)
    return Tree(code, graph, patterns, orbit, center)


def enumerate_trees(max_n: int, degree: int) -> list[Tree]:
    levels = [{"()": tree_from_adj({0: set()})}]
    for n in range(1, max_n):
        nxt: dict[str, Tree] = {}
        for tree in levels[-1].values():
            for v in range(n):
                if len(tree.adj[v]) >= degree:
                    continue
                adj = {u: set(tree.adj[u]) for u in range(n)}
                adj[v].add(n)
                adj[n] = {v}
                code, _ = canonical_order(adj)
                if code not in nxt:
                    nxt[code] = tree_from_adj(adj)
        levels.append(nxt)
    return [tree for level in levels for _, tree in sorted(level.items())]


def components_after_delete(tree: Tree, v: int) -> list[tuple[str, tuple[int, ...]]]:
    unseen = set(range(len(tree.adj))) - {v}
    out: list[tuple[str, tuple[int, ...]]] = []
    while unseen:
        todo = [min(unseen)]
        comp: set[int] = set()
        while todo:
            a = todo.pop()
            if a in comp:
                continue
            comp.add(a)
            todo.extend(u for u in tree.adj[a] if u != v and u not in comp)
        unseen -= comp
        adj = {a: set(tree.adj[a]) & comp for a in comp}
        out.append(canonical_order(adj))
    return out


def star_density(tree: Tree, colors: tuple[int, ...], q: int) -> Fraction:
    assert tree.star_center is not None
    k = len({colors[u] for u in tree.adj[tree.star_center]})
    if k >= q:
        raise ValueError("An iid star boundary can exhaust all colors")
    return Fraction(q, q - k)


def proper_patterns(adjacency, colors):
    """Color-renaming orbits of proper colorings of a labelled undirected graph.

    At most 10 vertices and 16 colors; no vertex-isomorphism quotient here.
    Returns restricted-growth strings, not the probability mass of each orbit.
    """
    if isinstance(colors, bool) or not isinstance(colors, int) or not 1 <= colors <= 16:
        raise ValueError("colors must be an integer in 1..16")
    graph = tuple(frozenset(neighbors) for neighbors in adjacency)
    if len(graph) > 10:
        raise ValueError("At most 10 vertices are admitted")
    for i, neighbors in enumerate(graph):
        if any(
            isinstance(j, bool)
            or not isinstance(j, int)
            or j == i
            or not 0 <= j < len(graph)
            or i not in graph[j]
            for j in neighbors
        ):
            raise ValueError("Adjacency must be symmetric, loopless and in range")
    return tuple(proper_partitions(graph, colors))


def exhaustive_patterns(adjacency, colors):
    """Simple independent enumerator for bounded tests and benchmarks only."""
    if colors ** len(adjacency) > 2000000:
        raise ValueError("Exhaustive reference exceeds two million assignments")
    return tuple(
        sorted(
            {
                normalize(c)
                for c in itertools.product(range(colors), repeat=len(adjacency))
                if all(c[i] != c[j] for i, row in enumerate(adjacency) for j in row)
            }
        )
    )
