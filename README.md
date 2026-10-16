# Finite Dependence Certificates

Build finite probability-cylinder constraints for proper finitely dependent
tree colorings, search their supported linear fragment, and export **exact
rational infeasibility certificates**. Rebuild every certificate from geometry
and probability rules using Python's standard library.

```sh
python -m pip install 'finite-dependence-certificates[solver] @ git+https://github.com/yuiyuiui/finite-dependence-certificates.git'
```

```python
from finite_dependence import (
    Hierarchy, build_hierarchy, search_infeasibility, verify_certificate,
)

system = build_hierarchy(Hierarchy(colors=3, max_vertices=5, max_degree=2))
result = search_infeasibility(system)  # Optional SciPy discovery backend.
assert result['certificate'] is not None, result['status']
assert verify_certificate(result['certificate'])  # Exact semantic replay.
print(system.shape, result['status'])
```

The core, `proper_patterns`, exact assembly and saved-certificate replay have
**no runtime dependency** beyond Python >=3.11. Only LP discovery needs NumPy
and SciPy (`[solver]`). Run `python examples/verify_saved.py` to replay a supplied
three-color path certificate without a solver. This is a known finite obstruction,
not a newly claimed coloring theorem.

## Scope and usefulness

The package saves researchers from rewriting color-renaming orbits, tree
symmetries, marginalization and exact dual checks for each local coloring model.
The supported hierarchy contains all unlabelled trees through at most eight
vertices and maximum degree at most three, with q>maximum degree. It assumes
proper coloring, color-permutation invariance, tree-isomorphism invariance,
one-dependence and the resulting forced star laws. These assumptions are part
of the model; this is not a test of arbitrary inhomogeneous random processes.

A verified certificate proves infeasibility of its **named finite hierarchy**.
A feasible finite relaxation does not construct an infinite process. Floating
solver output is only discovery evidence until exact reconstruction succeeds.
Products of unknown component probabilities are nonlinear; they are rejected
rather than silently compiled as linear constraints. The eight-vertex envelope
is essential to the supported compiler, not a general linearization theorem.

[Inflation](https://github.com/ecboghiu/inflation) already provides sophisticated
probabilistic compatibility modeling, and
[fast-inflation](https://github.com/vgitton/fast-inflation) includes exact rational
certificate work. This package specializes in local coloring semantics and
standalone rational replay; it is not a new LP solver or general causal-inference
replacement. No first-certificate or solver-speed claim is made.

See [contract/API](docs/API.md), [rules and provenance](docs/METHOD.md),
[benchmarks](bench/README.md), [readiness](docs/RELEASE_READINESS.md),
[contributing](CONTRIBUTING.md) and [citation](CITATION.cff).

Code, tests and documentation were developed with AI assistance under Kaiwen
Jin's direction. Exact finite arithmetic is not formal verification, human peer
review or an unrestricted infinite-process theorem.
