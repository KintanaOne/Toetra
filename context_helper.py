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
        files = sorted(
            [f for f in base_path.rglob("*.py") if f.is_file()]
        )
    else:
        files = sorted(
            [f for f in base_path.glob("*.py") if f.is_file()]
        )

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
    concat_files_in_folder("dsl/", recursive=True, output_file="context/dsl.txt")
    concat_files_in_folder("dsl/ast", recursive=True, output_file="context/ast.txt")
    concat_files_in_folder("dsl/semantic", recursive=True, output_file="context/semantic.txt")
    concat_files_in_folder("dsl/builder", recursive=True, output_file="context/builder.txt")
    concat_files_in_folder("dsl/language", recursive=True, output_file="context/language.txt")
    concat_files_in_folder("dsl/parser", recursive=True, output_file="context/parser.txt")
    concat_files_in_folder("dsl/ir", recursive=True, output_file="context/ir.txt")
