"""Discover a finite contradiction, then replay it without trusting solver floats."""

from finite_dependence import Hierarchy, build_hierarchy, search_infeasibility, verify_certificate

system = build_hierarchy(Hierarchy(colors=3, max_vertices=6, max_degree=2))
result = search_infeasibility(system)  # Requires the optional [solver] extra.
assert result["certificate"] is not None, result["status"]
assert verify_certificate(result["certificate"])
print(result["status"], system.shape)
