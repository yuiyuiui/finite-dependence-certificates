# Reproducible core benchmarks

[Raw results](results/core_v0.1.0.json) include five warm samples per variant,
first-call and setup times, source hashes, profiles, validation, settings and
dependency versions. macOS arm64, CPython 3.13.3, one numerical worker and
BLAS/OpenMP thread. Variants alternate execution order between cases and run in
separate fresh processes. No random input seed is hidden.

| Case | Reference median s | Production median s | Ratio | Python peak B (ref/prod) | Process RSS B (ref/prod) |
|---|---:|---:|---:|---:|---:|
| small | 0.000457042 | 6.70808e-06 | 68.13x | 2960 / 3088 | 27377664 / 26968064 |
| medium | 0.00715908 | 2.87089e-05 | 249.37x | 21280 / 4944 | 27279360 / 27115520 |
| large | 0.0281647 | 8.0917e-05 | 348.07x | 74000 / 27600 | 27426816 / 27361280 |

Both paths enumerate exactly the same color-renaming orbits of proper labelled path colorings with four colors. The independent reference visits every q^n assignment then deduplicates; production prunes improper prefixes and introduces colors by restricted-growth backtracking. This is a known symmetry reduction, not a new enumeration algorithm. The comparison covers this reusable combinatorial kernel only: it is not an LP-solver or complete-certificate speedup. Full hierarchy assembly also avoids recalculating images of already processed automorphism orbits. A separate full q4/degree3/eight-vertex profile builds 8510 exact equalities in 2748 unknowns with 26938 nonzeros; its 3.36 seconds includes profiling and tracemalloc overhead and is not a timing comparison. Its traced Python peak was about 9.2 MiB; see hierarchy_profile.json. The remaining work is tree/orbit assembly and exact sparse rule generation.

Validation is excluded from timed calls, repeated after every sample, and must
agree with the independent reference. Separate profiling and tracemalloc calls
do not contribute to timing samples. Setup includes imports, case construction
and the independent reference; it is not a pure production startup measurement.
Process RSS includes these reference/validation dependencies. Python-traced peak
measures one separate call and excludes untraced native memory. Small RSS changes
are noise; no universal process-memory reduction is claimed. These finite cases
do not establish asymptotic speedups or performance on arbitrary hardware.

```sh
python -m pip install '.[dev]'
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python bench/run.py \
  --repeats 5 --output /tmp/core-comparison.json
```

The output path must be new. The driver runs bounded small/medium/large cases;
performance thresholds are intentionally absent from shared CI. No network,
paid backend, GPU or hidden input data is needed. Each JSON `settings` object
specifies its requested output and cost boundary. Keep accuracy settings fixed
when comparing variants.

Full-hierarchy profiling evidence: [hierarchy_profile.json](results/hierarchy_profile.json).
