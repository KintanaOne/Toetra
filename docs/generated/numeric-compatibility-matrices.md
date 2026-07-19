# Numeric compatibility matrices

This page is generated from the normative numeric compatibility registry. 
Do not edit the tables manually.

## Support matrix

| Rule | Framework | Model family | Source profile | Encoder | Backend kind | Backend profile | Property requirements | Support |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| forml.v1.sklearn-affine-to-smt-exact-real-abstraction | sklearn | affine_regression | * | forml.affine-equation@1 | smt | z3 / smt_real_affine_exact | — | supported |

## Semantic guarantee matrix

| Rule | Classification | Semantic target | Conclusion scope | Permitted conclusions | Replay required for | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| forml.v1.sklearn-affine-to-smt-exact-real-abstraction | lossy | forml.real_affine_extracted_model | semantic_target_only | existential_no_witness, existential_witness, universal_counterexample, universal_proof | existential_witness, universal_counterexample | ADR-0018#initial-v1-instantiation |

## Reading the matrices

- `*` means that the rule intentionally matches any value on that axis.
- Support describes implementation availability; it does not imply an exact guarantee.
- The semantic target and conclusion scope define what a result is allowed to claim.
- A route classified as `lossy` may still be executable when conclusions are explicitly limited to the declared semantic target.
