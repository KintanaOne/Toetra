import re


def format_lark_output(lines: list[str]) -> str:
    formatted = []
    i = 0
    n = len(lines)

    def is_section_line(line: str) -> bool:
        return line.strip().startswith("#")

    def is_rule(line: str) -> bool:
        return ":" in line and not line.strip().startswith("#")
    
    def split_outside_regex(s: str, sep: str = "|") -> list[str]:
        parts = []
        current = []
        in_regex = False

        i = 0
        while i < len(s):
            c = s[i]

            if c == "/" and (i == 0 or s[i-1] != "\\"):
                in_regex = not in_regex
                current.append(c)

            elif c == sep and not in_regex:
                parts.append("".join(current).strip())
                current = []
            else:
                current.append(c)

            i += 1

        if current:
            parts.append("".join(current).strip())

        return parts
    
    def normalize_or_spacing(s: str) -> str:
        parts = re.split(r"(/[^/]+/)", s)
        result = []

        for part in parts:
            if part.startswith("/") and part.endswith("/"):
                result.append(part)
            else:
                result.append(re.sub(r"\s*\|\s*", " | ", part))

        return "".join(result)

    while i < n:
        line = lines[i]

        # =========================
        # SECTION BLOCKS
        # =========================
        if is_section_line(line):
            block = []
            while i < n and is_section_line(lines[i]):
                block.append(lines[i])
                i += 1

            if formatted:
                formatted.append("")

            formatted.extend(block)
            formatted.append("")
            continue

        # =========================
        # RULE FORMATTING (FIXED)
        # =========================
        if is_rule(line):
            lhs, rhs = line.split(":", 1)
            lhs = lhs.strip()
            rhs = rhs.strip()

            # normalize spacing
            rhs = re.sub(r"\s*\|\s*", "|", rhs)
            # rhs = re.sub(r"\s*,\s*", ", ", rhs)
            rhs = re.sub(r"\(\s+", "(", rhs)
            rhs = re.sub(r"\s+\)", ")", rhs)

            parts = split_outside_regex(rhs)

            # SINGLE LINE SAFE
            if len(parts) <= 1:
                formatted.append(f"{lhs} : {parts[0]}")
            else:
                for j,part in enumerate(parts):
                    # 🔥 CRITICAL: always same prefix, no variation
                    if j == 0:
                        formatted.append(f"{lhs} : {part}")
                    else:
                        formatted.append(f"    | {part}")

            i += 1
            continue

        # =========================
        # DEFAULT
        # =========================
        formatted.append(line)
        i += 1

    # =========================
    # 🔥 FINAL FIX (ANTI _NL_OR)
    # =========================
    result = "\n".join(formatted)

    # force clean newline + pipe formatting
    result = re.sub(r"\n\s*\|", "\n    |", result)

    return result