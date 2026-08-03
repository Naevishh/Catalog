from pathlib import Path

def get_filepath(file_name: str) -> Path:
    current_module_dir = Path(__file__).resolve().parent
    project_root = current_module_dir.parent
    data_dir = project_root / "data"
    # Создаем папку data, если её нет (parents=True создаст и промежуточные папки)
    # exist_ok=True предотвратит ошибку, если папка уже есть
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / file_name