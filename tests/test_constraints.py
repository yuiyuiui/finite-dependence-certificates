import copy
import itertools
import json
from pathlib import Path

import pytest
from finite_dependence import (
    Hierarchy,
    build_hierarchy,
    proper_patterns,
    search_infeasibility,
    verify_certificate,
    certificate_from_multipliers,
)
from finite_dependence.combinatorics import exhaustive_patterns, star_density, enumerate_trees


def test_patterns_against_all_assignments_and_color_counts():
    for n in range(1, 6):
        for q in (2, 3, 4):
            for edges in [
                [],
                [(i, i + 1) for i in range(n - 1)],
                list(itertools.combinations(range(n), 2)),
            ]:
                adjacency = [set() for _ in range(n)]
                for a, b in edges:
                    adjacency[a].add(b)
                    adjacency[b].add(a)
                assert set(proper_patterns(adjacency, q)) == set(exhaustive_patterns(adjacency, q))


def test_tree_enumeration_and_forced_probabilities():
    trees = enumerate_trees(5, 3)
    # Unlabelled trees with maximum degree <=3: 1,1,1,2,2.
    assert [sum(len(t.adj) == n for t in trees) for n in range(1, 6)] == [1, 1, 1, 2, 2]
    star = next(t for t in trees if len(t.adj) == 3)
    from fractions import Fraction as Q

    equal_leaves = next(c for c in star.partitions if len(set(c)) == 2)
    distinct = next(c for c in star.partitions if len(set(c)) == 3)
    assert star_density(star, equal_leaves, 4) / 4**3 == Q(1, 48)
    assert star_density(star, distinct, 4) / 4**3 == Q(1, 32)


def test_small_linear_model_from_hand_marginalization():
    s = build_hierarchy(Hierarchy(3, 4, 2))
    # Three color-renaming/reflection classes on a four-vertex path.
    assert s.shape == (4, 3)
    from fractions import Fraction as Q

    # Endpoint marginalization gives A+B=9/2, B+C=9. Deleting an
    # interior vertex and applying one-dependence forces B=C=9/2.
    names = {pattern: i for i, (_, pattern) in enumerate(s.variables)}
    A, B, C = (names[c] for c in [(0, 1, 0, 1), (0, 1, 0, 2), (0, 1, 2, 0)])
    expected = {
        (tuple(sorted(((A, Q(1)), (B, Q(1))))), Q(9, 2)),
        (tuple(sorted(((B, Q(1)), (C, Q(1))))), Q(9)),
        (((B, Q(1)),), Q(9, 2)),
        (((C, Q(1)),), Q(9, 2)),
    }
    assert set(zip(s.rows, s.rhs)) == expected
    assert all(all(c.denominator == 1 for _, c in row) for row in s.rows)
    assert s.digest == build_hierarchy(Hierarchy(3, 4, 2)).digest


def test_exact_certificate_geometry_replay_and_tampering():
    path = Path(__file__).resolve().parents[1] / "examples/three_color_path_certificate.json"
    record = json.loads(path.read_text())
    assert verify_certificate(record)
    wrong = copy.deepcopy(record)
    wrong["multipliers"][0][1] = "999999"
    assert not verify_certificate(wrong)
    wrong = copy.deepcopy(record)
    wrong["hierarchy"]["colors"] += 1
    assert not verify_certificate(wrong)
    wrong = copy.deepcopy(record)
    wrong["multipliers"].append(wrong["multipliers"][0])
    assert not verify_certificate(wrong)
    wrong = copy.deepcopy(record)
    wrong["system_sha256"] = "0" * 64
    assert not verify_certificate(wrong)


def test_optional_solver_search_is_exactly_checked():
    s = build_hierarchy(Hierarchy(3, 6, 2))
    result = search_infeasibility(s)
    assert result["status"] == "EXACT_INFEASIBILITY_CERTIFICATE"
    assert verify_certificate(result["certificate"])
    # A four-color path hierarchy has no contradiction at this bounded level.
    feasible = search_infeasibility(build_hierarchy(Hierarchy(4, 4, 2)))
    assert feasible["certificate"] is None
    with pytest.raises(ValueError):
        certificate_from_multipliers(s, {})


@pytest.mark.parametrize(
    "args", [(3, 9, 2), (3, 6, 3), (4, 6, 4), (4, True, 2), (4.0, 6, 2), (17, 6, 2), (4, 0, 2)]
)
def test_invalid_hierarchies(args):
    with pytest.raises(ValueError):
        Hierarchy(*args)


@pytest.mark.parametrize(
    "adj,q", [([{1}, set()], 3), ([{0}], 3), ([{2}, set()], 3), ([set()], True), ([set()], 0)]
)
def test_invalid_pattern_inputs(adj, q):
    with pytest.raises(ValueError):
        proper_patterns(adj, q)


def test_certificate_configuration_is_detached_from_system():
    s = build_hierarchy(Hierarchy(3, 5, 2))
    result = search_infeasibility(s)
    result["certificate"]["hierarchy"]["colors"] = 99
    assert s.hierarchy.colors == 3
