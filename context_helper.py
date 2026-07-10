from pathlib import Path


def concat_files_in_folder(
    folder_path: str,
    recursive: bool = False,
    encoding: str = "utf-8",
    output_file: str = "tmp_context.txt",
) -> None:
    """
    Concatène le contenu de tous les fichiers .py d'un dossier
    et écrit le résultat dans un fichier.

    Args:
        folder_path: chemin du dossier
        recursive: si True, parcourt aussi les sous-dossiers
        encoding: encodage des fichiers texte
        output_file: fichier de sortie
    """
    base_path = Path(folder_path)

    if recursive:
        files = sorted([f for f in base_path.rglob("*") if f.is_file()])
    else:
        files = sorted([f for f in base_path.glob("*") if f.is_file()])

    parts = []

    for file_path in files:
        try:
            content = file_path.read_text(encoding=encoding)
        except Exception as e:
            content = f"[ERROR reading file: {e}]"

        parts.append(f"\n===== {file_path} =====\n")
        parts.append(content)

    final_content = "\n".join(parts)

    Path(output_file).write_text(final_content, encoding=encoding)


if __name__ == "__main__":
    # all
    concat_files_in_folder("dsl/", recursive=True, output_file="context/dsl.txt")

    # dsl subfolders
    concat_files_in_folder("dsl/ast", recursive=True, output_file="context/dsl/ast.txt")
    concat_files_in_folder(
        "dsl/semantic", recursive=True, output_file="context/dsl/semantic.txt"
    )
    concat_files_in_folder(
        "dsl/builder", recursive=True, output_file="context/dsl/builder.txt"
    )
    concat_files_in_folder(
        "dsl/language", recursive=True, output_file="context/dsl/language.txt"
    )
    concat_files_in_folder(
        "dsl/parser", recursive=True, output_file="context/dsl/parser.txt"
    )
    concat_files_in_folder("dsl/ir", recursive=True, output_file="context/dsl/ir.txt")

    # test
    concat_files_in_folder(
        "model", recursive=True, output_file="context/model/model.txt"
    )

    concat_files_in_folder(
        "test/unit", recursive=True, output_file="context/test/unit.txt"
    )
    concat_files_in_folder(
        "test/hypothesis", recursive=True, output_file="context/test/hypothesis.txt"
    )
    concat_files_in_folder(
        "test/hypothesis/mutation",
        recursive=True,
        output_file="context/test/hypothesis/mutation.txt",
    )

    # core
    concat_files_in_folder(
        "test/hypothesis/mutation/core",
        recursive=True,
        output_file="context/test/hypothesis/mutations/core.txt",
    )

    # decorators
    concat_files_in_folder(
        "test/hypothesis/mutation/decorators",
        recursive=True,
        output_file="context/test/hypothesis/mutations/decorator.txt",
    )

    # metadata
    concat_files_in_folder(
        "test/hypothesis/mutation/metadata",
        recursive=True,
        output_file="context/test/hypothesis/mutations/metadata.txt",
    )

    # strategies
    concat_files_in_folder(
        "test/hypothesis/strategies/valid",
        recursive=True,
        output_file="context/test/hypothesis/strategies/valid.txt",
    )
    concat_files_in_folder(
        "test/hypothesis/strategies/invalid",
        recursive=True,
        output_file="context/test/hypothesis/strategies/invalid.txt",
    )

    concat_files_in_folder(
        "test/hypothesis/mutation/functions/semantic",
        recursive=True,
        output_file="context/test/hypothesis/mutation/semantic.txt",
    )

    concat_files_in_folder(
        "test/hypothesis/mutation/functions/semantic/helper",
        recursive=True,
        output_file="context/test/hypothesis/mutation/helper.txt",
    )

    # docs
    concat_files_in_folder(
        "docs/architecture/ast",
        recursive=True,
        output_file="context/architecture/ast.txt",
    )

    concat_files_in_folder(
        "docs/architecture/forml",
        recursive=True,
        output_file="context/architecture/forml.txt",
    )

    concat_files_in_folder(
        "docs/architecture/layers",
        recursive=True,
        output_file="context/architecture/layers.txt",
    )

    concat_files_in_folder(
        "docs/architecture/parsing",
        recursive=True,
        output_file="context/architecture/parsing.txt",
    )

    concat_files_in_folder(
        "model",
        recursive=True,
        output_file="context/model/model.txt",
    )

    concat_files_in_folder(
        "dsl/backends",
        recursive=True,
        output_file="context/dsl/backends.txt",
    )
