"""Allow ``python -m toetra`` to use the installed CLI contract."""

from __future__ import annotations

from toetra._cli.main import main

raise SystemExit(main())
