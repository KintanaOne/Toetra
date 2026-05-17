# Header Structure

## Overview

The **header** is the mandatory first section of a FORML program. It defines the global context required to interpret and verify the rest of the specification.

A valid header **must** declare:

1. the model under verification, and
2. the target variable of interest.

Optionally, it may also declare variables used later in the program.

---

## Purpose of the Header

The header serves as the **contextual anchor** of a FORML specification. It answers the fundamental questions:

* *Which model is being verified?*
* *Which target does the verification refer to?*
* *Which symbolic variables are available to express properties?*

Without a valid header, no semantic interpretation of the program is possible.

---

## Global Syntax

Formally, the header is defined by the following EBNF rule:

```
header = padding , model_declaration , padding , target_declaration , padding , [ variables_declaration , padding ] ;
```

This definition enforces:

* a **strict ordering** of declarations,
* tolerance to comments and empty lines via `padding`,
* optional variable declarations appearing **after** the target declaration.

---

## Header Components

### Padding

`padding` represents any combination of:

* comments,
* empty lines,
* whitespace.

Padding may appear:

* before the first declaration,
* between declarations,
* after the last declaration.

Padding has **no semantic impact**.

---

### Model Declaration (mandatory)

The model declaration specifies the model to be verified.

**Syntax**:

```
model := "<path_or_identifier>"
```

**Constraints**:

* Must appear **exactly once** in the header.
* Must be the **first declaration** (excluding padding).
* The model path or identifier must be a quoted string.

---

### Target Declaration (mandatory)

The target declaration identifies the output variable of the model that is subject to verification.

**Syntax**:

```
target := <Identifier>
```

**Constraints**:

* Must appear **exactly once** in the header.
* Must appear **after** the model declaration.
* The target must be a valid identifier.

---

### Variables Declaration (optional)

The variables declaration introduces symbolic variables that can be referenced later in the program (e.g. in properties or constraints).

**Syntax**:

```
var0 = value0
var1 = value1
```

**Constraints**:

* Optional.
* If present, must appear **after** the target declaration.
* Cannot appear more than once.

---

## Ordering Rules

The order of declarations in the header is **strict and non-negotiable**:

1. `model_declaration`
2. `target_declaration`
3. `variables_declaration` (optional)

Any deviation from this order results in a parsing error.

---

## Valid Example

```
# This is a comment
# Another comment
model := "path/to/model.onnx"
target := MyTargetColumn
```

This header is valid because:

* padding is allowed before declarations,
* the model is declared first,
* the target is declared second,
* no forbidden or misplaced declaration appears.

---

## Invalid Examples

### Target before model

```
target := MyTargetColumn
model := "path/to/model.onnx"
```

❌ Invalid: the model declaration must come first.

---

### Multiple model declarations

```
model := "model_a.onnx"
model := "model_b.onnx"
target := MyTargetColumn
```

❌ Invalid: the model declaration must be unique.

---

### Variables before target

```
model := "path/to/model.onnx"
x = 0
target := MyTargetColumn
```

❌ Invalid: variables must be declared after the target.

---

## Notes and Constraints

* The header is **mandatory** in every FORML program.
* Declarations outside the header are not permitted.
* The header defines the **global semantic context** shared by all subsequent sections.

In the overall FORML structure, the header is followed by the body and the footer, each relying on the context established here.
