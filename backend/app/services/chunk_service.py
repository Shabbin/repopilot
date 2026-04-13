from pathlib import Path

TEXT_FILE_EXTENSIONS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".go", ".rs",
    ".cpp", ".c", ".h", ".hpp", ".cs", ".rb", ".php", ".swift",
    ".kt", ".scala", ".sql", ".html", ".css", ".md", ".json", ".yaml", ".yml"
}


def is_chunkable_file(file_path: str) -> bool:
    return Path(file_path).suffix.lower() in TEXT_FILE_EXTENSIONS


def read_file_content(full_path: str) -> list[str]:
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            return f.readlines()
    except UnicodeDecodeError:
        try:
            with open(full_path, "r", encoding="latin-1") as f:
                return f.readlines()
        except Exception:
            return []
    except Exception:
        return []


def chunk_lines(lines: list[str], chunk_size: int = 80, overlap: int = 20) -> list[dict]:
    chunks = []
    if not lines:
        return chunks

    start = 0
    chunk_index = 0

    while start < len(lines):
        end = min(start + chunk_size, len(lines))
        chunk_content = "".join(lines[start:end]).strip()

        if chunk_content:
            chunks.append({
                "chunk_index": chunk_index,
                "content": chunk_content,
                "start_line": start + 1,
                "end_line": end,
            })

        if end == len(lines):
            break

        start += chunk_size - overlap
        chunk_index += 1

    return chunks