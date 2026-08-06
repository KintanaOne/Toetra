## Summary

Describe the problem, the chosen change, and any user-visible consequence.

Do not submit outside code or documentation unless a maintainer has confirmed
that the required contributor agreement is in place. Opening a pull request
does not by itself grant commercial relicensing rights.

## Contract impact

- Public API or behavior changed: yes / no
- Verification or numeric guarantee changed: yes / no
- JSON schema changed: yes / no
- Documentation or release evidence changed: yes / no

If any frozen `1.0.0rc4` boundary would change, link the accepted design
decision before requesting review.

## Validation

- [ ] I added or updated focused tests where needed.
- [ ] `make ci` passes.
- [ ] Relevant demos pass.
- [ ] Distribution or review-bundle gates pass when affected.
- [ ] Documentation matches the implemented behavior.
- [ ] The change contains no credentials, private data, generated build output, or patch artifact.
- [ ] The change does not widen the `1.0.0rc4` capability profile or declare
      the stable `1.0.0` release.
