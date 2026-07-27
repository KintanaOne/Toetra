# Public Python API

> Status: Frozen for `1.0.0rc3`
>
> Supported import surface: `toetra`

The public Python API is deliberately small. The nine names exported by
`toetra.__all__` are the complete supported facade:

```python
from toetra import (
    CounterexampleReplay,
    ReplayUnavailableError,
    VerificationConfigurationError,
    VerificationFinding,
    VerificationReport,
    VerificationRuntimeError,
    VerificationSession,
    VerificationStatus,
    verify,
)
```

| Symbol | Role |
|---|---|
| [`verify`](verify.md) | Compile and execute every property in one specification |
| [`VerificationSession`](sessions-and-findings.md#verificationsession) | Complete result of one `verify(...)` call |
| [`VerificationFinding`](sessions-and-findings.md#verificationfinding) | Ergonomic view of one completed property |
| [`VerificationReport`](reports-and-status.md#verificationreport) | Backend-neutral, serializable property report |
| [`VerificationStatus`](reports-and-status.md#verificationstatus) | Logical conclusion of one property |
| [`CounterexampleReplay`](replay-and-errors.md#counterexamplereplay) | Comparison of formal evidence with concrete model execution |
| [`VerificationRuntimeError`](replay-and-errors.md#public-error-hierarchy) | Base class for public runtime orchestration errors |
| [`VerificationConfigurationError`](replay-and-errors.md#verificationconfigurationerror) | Ambiguous or inconsistent verification inputs |
| [`ReplayUnavailableError`](replay-and-errors.md#replayunavailableerror) | Formal evidence cannot be replayed completely |

## Object lifecycle

```text
verify(...)
→ VerificationSession
→ VerificationFinding / VerificationReport
→ optional CounterexampleReplay
```

One session contains one report and one finding per property. Reports preserve
the normalized logical result, routing evidence, diagnostics, numeric
compatibility and provenance. Replay is a separate concrete check: it never
upgrades the scope of a formal conclusion.

## Stability boundary

Only imports from `toetra` belong to the public V1 Python contract. Modules
beneath `toetra._*` are implementation details: they may be useful while
developing Toetra itself, but applications must not depend on their import
paths, constructors or concrete types.

Some advanced keyword arguments of `verify(...)` accept current internal
compiler, routing or adapter objects. Their presence in the runtime signature
does not promote those private types to the public V1 facade. See
[advanced injection hooks](verify.md#advanced-injection-hooks) before using
them.

The public classes are primarily returned by Toetra. Constructing them directly
is not a supported application workflow unless a constructor is explicitly
documented here.

## Compatibility

- incompatible changes to these nine names require a major version;
- report JSON has its own versioned compatibility contract;
- private imports and sequence items returned from internal execution layers do
  not receive public compatibility guarantees;
- language support is governed separately by the
  [Public V1 profile](../public-v1-profile.md).
