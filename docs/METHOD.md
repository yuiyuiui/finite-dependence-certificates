# Probability rules and provenance

Trees are canonicalized by sorted rooted subtree codes; finite automorphisms and
color-renaming restricted-growth strings identify symmetric cylinder variables.
Deleting a vertex splits a tree into components. One-dependence makes component
color laws independent because distinct components are at graph distance >=2.
Marginalization sums the allowed colors at the deleted vertex; an unused color
represents q−k interchangeable choices when k named colors already appear.

Unknowns are normalized densities rho(T,c)=q^|T| P(specified word c).
A star with k different leaf colors has rho=q/(q−k): its leaves are independent
uniform colors, while symmetry makes the center uniform among the q−k remaining
colors. A deletion identity is therefore

    sum_allowed_center_colors rho(T,c) = q * product_components rho(component,c).

Only a product with at most one unknown factor is linear. Every tree on <=8
vertices leaves at most seven vertices after deletion, so two nonstar components
(each needs at least four vertices) cannot both occur. The compiler still checks
this condition explicitly. Fixed star factors are substituted exactly. Other
constraints are nonnegativity of the named unknown densities; no unproved
extension inequalities from an infinite-volume argument are added.

For A x=b, x>=0, a rational y with yA>=0 and yb<0 is a Farkas contradiction:
if a feasible x existed, yb=(yA)x>=0. Discovery minimizes b^T y with A^T y>=0 and
−1<=y_i<=1 in floating arithmetic. A true ray can be scaled into this box;
floating success alone is insufficient. Exact reconstruction checks the full
rational inequalities and may fail without a certificate.

The combinatorics and finite hierarchy were adapted from the user's AIM-583
computational seed. The requirement to reconstruct rules semantically and replay
rational combinations was informed by AIM-584's exact verifier. AIM-584's special
branched-ray affine parameters and infinite-volume extension inequality were
**not imported as generic finite probability rules**. No private proof archives,
research controls or original Git history are distributed.

Prior software includes [Inflation](https://github.com/ecboghiu/inflation) and
[fast-inflation](https://github.com/vgitton/fast-inflation). The optional optimizer
is the established [SciPy HiGHS interface](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linprog.html).
The software contribution is bounded coloring-specific model assembly, precise
symmetry/probability conventions, exact replay, tests and distribution. The
supplied three-color path obstruction is a regression example, not a novelty claim.

## Direct-use result

For integer q>D, q<=16, maximum tree degree 1<=D<=3 and truncation
1<=n<=8 vertices, `build_hierarchy` constructs exact finite equations A x=b,
x>=0 under proper coloring, color-permutation/tree-isomorphism invariance and
one-dependence with the forced star laws. Each coordinate of x is q^k times
the specified-word probability for its k-vertex tree. A returned verified
certificate supplies rational row weights y satisfying yA>=0 and yb<0, and
therefore rules out this finite hierarchy. The verifier rebuilds A,b from the
geometry and versioned rules. Failure to find a certificate, or finite feasibility,
has no implication of existence of an infinite random process.
