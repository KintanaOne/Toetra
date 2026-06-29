# Installation

> Status: Draft  
> Scope: Developer setup  
> Implementation: To be stabilized

## Purpose

This document describes the expected installation flow for FORML during the V1 development phase.

Because FORML is still under active development, installation instructions should remain simple and developer-oriented.

## Recommended setup

Clone the repository:

```bash
git clone https://github.com/KintanaOne/FORML.git
cd FORML
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it:

=== "Windows"

    ```bash
    .venv\Scripts\activate
    ```

=== "Linux / macOS"

    ```bash
    source .venv/bin/activate
    ```

Install development dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## Expected dependencies

FORML currently depends on several categories of packages:

| Category | Purpose |
|---|---|
| Parser | DSL parsing |
| Testing | unit tests, property-based tests, fuzzing |
| ML frameworks | model loading and introspection |
| Solver | Z3 backend |
| Documentation | MkDocs site generation |

## Z3 requirement

Z3 is the minimal backend target for the first functional V1.

A working V1 should be able to go from:

```text
.forml + model
→ Z3 query
→ verification result
```

## Optional dependencies

Some dependencies may remain optional depending on enabled features:

| Dependency | Purpose |
|---|---|
| scikit-learn | ModelBridge sklearn support |
| xgboost | ModelBridge XGBoost support |
| pandas | dataset/schema introspection |
| hypothesis | property-based testing |
| miova | mutation campaigns and contract testing |

## Documentation build

Install documentation dependencies and run:

```bash
mkdocs serve
```

or:

```bash
mkdocs build --strict
```

The strict build should eventually be part of CI.

## Stabilization note

This page should be updated once the project exposes a stable package interface and installation command.
