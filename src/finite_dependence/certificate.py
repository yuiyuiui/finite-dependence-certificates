"""Farkas certificate reconstruction and verification using exact rationals."""

from fractions import Fraction as Q
from dataclasses import asdict

from .model import Hierarchy, LinearSystem, build_hierarchy


def _check(system, multipliers):
    columns = [Q(0)] * len(system.variables)
    value = Q(0)
    for row, weight in multipliers.items():
        value += weight * system.rhs[row]
        for j, c in system.rows[row]:
            columns[j] += weight * c
    return all(c >= 0 for c in columns) and value < 0


def certificate_from_multipliers(system, multipliers):
    """Return a certificate only after exact checking of yA>=0 and yb<0."""
    if not isinstance(system, LinearSystem):
        raise TypeError("system must be a LinearSystem")
    if system.digest != build_hierarchy(system.hierarchy).digest:
        raise ValueError("System does not match the named semantic hierarchy")
    weights = {}
    for i, value in multipliers.items():
        if isinstance(i, bool) or not isinstance(i, int) or not 0 <= i < len(system.rows):
            raise ValueError("Multiplier row index outside the exact system")
        weight = Q(value)
        if weight:
            weights[i] = weight
    if not _check(system, weights):
        raise ValueError("Exact Farkas inequalities do not hold")
    return {
        "format_version": 1,
        "rules": "tree-coloring-cylinders-v1",
        "hierarchy": asdict(system.hierarchy),
        "system_sha256": system.digest,
        "multipliers": [[i, str(c)] for i, c in sorted(weights.items())],
    }


def verify_certificate(record):
    """Rebuild A,b from geometry/rules; do not trust a stored solver matrix.

    No NumPy/SciPy is needed. This proves infeasibility of the named finite
    hierarchy under its explicit invariance and forced-star assumptions.
    """
    try:
        if record["format_version"] != 1 or record["rules"] != "tree-coloring-cylinders-v1":
            return False
        system = build_hierarchy(Hierarchy(**record["hierarchy"]))
        if system.digest != record["system_sha256"]:
            return False
        weights = {}
        for i, value in record["multipliers"]:
            if (
                isinstance(i, bool)
                or not isinstance(i, int)
                or not 0 <= i < len(system.rows)
                or i in weights
            ):
                return False
            weights[i] = Q(value)
        return _check(system, weights)
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        return False


def search_infeasibility(system, *, max_denominator=1000000):
    """Optional floating LP discovery followed by exact rational reconstruction.

    Return an exact certificate or an honest inconclusive diagnostic. A failed
    reconstruction never becomes a proof; feasible finite LPs imply no infinite law.
    """
    if not isinstance(system, LinearSystem):
        raise TypeError("system must be a LinearSystem")
    if (
        isinstance(max_denominator, bool)
        or not isinstance(max_denominator, int)
        or max_denominator < 1
    ):
        raise ValueError("max_denominator must be a positive integer")
    try:
        import numpy as np
        from scipy.optimize import linprog
        from scipy.sparse import coo_matrix
    except ImportError as exc:
        raise RuntimeError(
            "Install finite-dependence-certificates[solver] for LP discovery"
        ) from exc
    m, n = system.shape
    if not m:
        return {"status": "FINITE_HIERARCHY_NO_UNKNOWN_CONSTRAINTS", "certificate": None}
    ii, jj, vv = [], [], []
    for i, row in enumerate(system.rows):
        for j, c in row:
            ii.append(i)
            jj.append(j)
            vv.append(float(c))
    matrix = coo_matrix((vv, (ii, jj)), shape=(m, n)).tocsr()
    objective = np.array(list(map(float, system.rhs)))
    # Bounded Farkas search: scaling any genuine dual ray fits this box.
    result = linprog(
        objective,
        A_ub=-matrix.T,
        b_ub=np.zeros(n),
        bounds=[(-1, 1)] * m,
        method="highs",
        options={"time_limit": 30},
    )
    if result.success and result.fun < -1e-9:
        weights = {
            i: Q(float(value)).limit_denominator(max_denominator)
            for i, value in enumerate(result.x)
            if value
        }
        try:
            record = certificate_from_multipliers(system, weights)
            return {
                "status": "EXACT_INFEASIBILITY_CERTIFICATE",
                "certificate": record,
                "solver_message": result.message,
                "discovery_objective": float(result.fun),
            }
        except ValueError:
            return {
                "status": "RATIONAL_RECONSTRUCTION_FAILED",
                "certificate": None,
                "solver_message": result.message,
                "discovery_objective": float(result.fun),
            }
    return {
        "status": "NO_EXACT_CERTIFICATE_FOUND",
        "certificate": None,
        "solver_message": result.message,
        "solver_status": int(result.status),
    }
