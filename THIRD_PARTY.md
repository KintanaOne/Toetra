# Third-party material

Toetra source code and original documentation are licensed under the
[PolyForm Noncommercial License 1.0.0](LICENSE). The asset below keeps its own
license; the PolyForm project license does not replace or narrow that license.

## UCI Heart Disease — processed Cleveland data

Repository path:

```text
demo/classification/cleveland/data/heart-disease-cleveland.csv
```

Attribution:

> Janosi, A., Steinbrunn, W., Pfisterer, M., & Detrano, R. (1989).
> *Heart Disease* [Dataset]. UCI Machine Learning Repository.
> <https://doi.org/10.24432/C52P4X>

- Creators: Andras Janosi, William Steinbrunn, Matthias Pfisterer, and
  Robert Detrano.
- Source: `processed.cleveland.data` from the
  [UCI Heart Disease dataset](https://archive.ics.uci.edu/dataset/45/heart%2Bdisease).
- Source file SHA-256:
  `a74b7efa387bc9d108d7d0115d831fe9b414b29ae7124f331b622b4efa0427c8`.
- Repository file canonical-LF SHA-256:
  `bc9bd5b0af3c54a0ca87cae80799fbf24a670de839d97f97b3f55a754bc84615`.
- License:
  [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/legalcode)
  (CC BY 4.0).

### Changes made by Toetra

The repository copy preserves all 303 records and all 14 published processed
Cleveland columns. Toetra:

1. added the CSV header;
2. named the original `num` response column `target`;
3. normalized textual decimal notation for integer-valued entries, for example
   `63.0` to `63`.

The six original `?` missing-value markers are preserved. A numeric comparison
against the UCI source confirms that no observed value changed.
The repository digest is computed after normalizing CRLF to LF so the same
tracked CSV passes on Windows and POSIX checkouts.

The UCI metadata states that patient names and social-security numbers were
removed and replaced with dummy values before distribution.

This dataset is provided only as a public demonstration workspace. It is not
part of the installed `toetra` Python distribution and does not imply medical
fitness, diagnostic validity, or endorsement by the dataset creators or UCI.
