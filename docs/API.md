# API and contract

`Hierarchy(colors=4, max_vertices=6, max_degree=3)` is a frozen configuration.
All inputs must be integers: 1<=max_vertices<=8, 1<=max_degree<=3, and
max_degree<colors<=16. The forced star formulas require this color range.
`build_hierarchy(config)` returns an immutable `LinearSystem` containing exact
sparse row tuples, rational rhs, ordered variable descriptors, shape, constant
identity count and deterministic semantic-system digest. It uses no solver,
float arithmetic, randomized search or global precision/thread mutation.

The system is A x=b, x>=0. A variable for an n-vertex colored tree is **q^n times
the probability of one specified color word**, not its orbit's total probability.
Color-permutation and vertex-automorphism quotienting impose the declared
symmetry ansatz. These assumptions must match the user's mathematical setting.

`proper_patterns(adjacency, colors)` is a separate reusable primitive: it returns
color-renaming orbits of proper colorings of a labelled undirected loopless graph
(up to ten vertices and sixteen colors). It does not quotient by graph
automorphisms and does not return probability weights. Input adjacency is copied.
Restricted-growth backtracking prunes improper prefixes and caps the number of
used colors. The exhaustive benchmark reference refuses >2 million assignments.

`search_infeasibility(system, max_denominator=1_000_000)` uses optional SciPy/HiGHS
with a 30-second solve limit to search a bounded dual polytope. It then reconstructs
rationals and checks every sign/equality exactly. Status is one of:

- EXACT_INFEASIBILITY_CERTIFICATE: a checked record is returned.
- RATIONAL_RECONSTRUCTION_FAILED: floating evidence could not be made exact.
- NO_EXACT_CERTIFICATE_FOUND: inconclusive, including solver limits/failure.
- FINITE_HIERARCHY_NO_UNKNOWN_CONSTRAINTS: no unknown-variable constraints.

The result never asserts existence of an infinite law. LP costs are distinct from
pattern enumeration; a solver limit is not mathematical infeasibility.

`certificate_from_multipliers(system, {row_index: rational, ...})` checks the
canonical semantic-system match, yA>=0 componentwise and yb<0 using `Fraction`.
It raises ValueError on a false certificate. `verify_certificate(record)` rebuilds
the hierarchy from its geometry descriptor, checks its digest and the exact
Farkas inequalities; it never trusts a stored floating matrix. False or malformed
records return False. Exported configuration dictionaries are detached.
Certificates concern only the versioned `tree-coloring-cylinders-v1` rule set.
The verifier shares the semantic compiler, so independent hand-derived rule tests
are still necessary; it is independent of the floating solver, not a formally
verified independent implementation of every probability axiom.

The bounded compiler can still grow combinatorially. No arbitrary graph hierarchy,
higher-order dependence, nonlinear solver, GPU or infinite-law construction is
advertised. Invalid input and nonlinear compilation raise ValueError. Patches
preserve the model meanings and schema; breaking rules require a new rule version.
