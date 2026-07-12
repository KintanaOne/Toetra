from pathlib import Path


def concat_files_in_folder(
    folder_path: str,
    extension: str = ".py",
    recursive: bool = False,
    encoding: str = "utf-8",
    output_file: str = "tmp_context.txt",
) -> None:
    """
    Concatène le contenu de tous les fichiers {extension} d'un dossier
    et écrit le résultat dans un fichier.

    Args:
        folder_path: chemin du dossier
        extension: extension des fichiers à concaténer
        recursive: si True, parcourt aussi les sous-dossiers
        encoding: encodage des fichiers texte
        output_file: fichier de sortie
    """
    base_path = Path(folder_path)

    if recursive:
        files = sorted([f for f in base_path.rglob(f"*{extension}") if f.is_file()])
    else:
        files = sorted([f for f in base_path.glob(f"*{extension}") if f.is_file()])

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

    # docs
    concat_files_in_folder(
        "docs",
        recursive=True,
        extension=".md",
        output_file="context/docs.txt",
    )

    # DSL
    concat_files_in_folder(
        "dsl",
        recursive=True,
        extension=".py",
        output_file="context/dsl.txt",
    )

    # model
    concat_files_in_folder(
        "model",
        recursive=True,
        output_file="context/model/model.txt",
    )

    # test
    concat_files_in_folder(
        "test",
        recursive=True,
        output_file="context/test.txt",
    )
