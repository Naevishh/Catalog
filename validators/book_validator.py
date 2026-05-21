from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class ValidationResult:
    """Структурированный результат проверки"""
    is_valid: bool
    errors: Dict[str, List[str]] = field(default_factory=dict)


class BookValidator:
    """
    Доменная валидация для книг (Вариант 15)
    Не зависит от PyQt. Можно легко покрыть юнит-тестами.
    """
    MIN_TITLE_LEN = 2
    MAX_TITLE_LEN = 200
    MIN_AUTHOR_LEN = 3
    MAX_AUTHOR_LEN = 100
    MIN_PUBLISHER_LEN = 2
    MAX_PUBLISHER_LEN = 100
    MIN_VOLUMES = 1
    MAX_VOLUMES = 1000
    MIN_CIRCULATION = 1
    MAX_CIRCULATION = 10_000_000

    @classmethod
    def validate(cls, data: dict) -> ValidationResult:
        errors: Dict[str, List[str]] = {}

        title = data.get("name", "").strip()
        if not title:
            errors["name"] = ["Название книги обязательно"]
        elif len(title) < cls.MIN_TITLE_LEN:
            errors.setdefault("name", []).append(f"Минимум {cls.MIN_TITLE_LEN} символа")
        elif len(title) > cls.MAX_TITLE_LEN:
            errors.setdefault("name", []).append(f"Максимум {cls.MAX_TITLE_LEN} символов")

        author = data.get("author", "").strip()
        if not author:
            errors["author"] = ["ФИО автора обязательно"]
        elif len(author) < cls.MIN_AUTHOR_LEN:
            errors.setdefault("author", []).append(f"Минимум {cls.MIN_AUTHOR_LEN} символа")
        elif len(author.split()) < 2:
            errors.setdefault("author", []).append("Введите фамилию и имя")
        elif len(author) > cls.MAX_AUTHOR_LEN:
            errors.setdefault("author", []).append(f"Максимум {cls.MAX_AUTHOR_LEN} символов")

        publisher = data.get("publisher", "").strip()
        if not publisher:
            errors["publisher"] = ["Издательство обязательно"]
        elif len(publisher) < cls.MIN_PUBLISHER_LEN:
            errors.setdefault("publisher", []).append(f"Минимум {cls.MIN_PUBLISHER_LEN} символа")
        elif len(publisher) > cls.MAX_PUBLISHER_LEN:
            errors.setdefault("publisher", []).append(f"Максимум {cls.MAX_PUBLISHER_LEN} символов")

        volumes = data.get("number_of_volumes")
        if not (cls.MIN_VOLUMES <= volumes <= cls.MAX_VOLUMES):
            errors["number_of_volumes"] = [f"От {cls.MIN_VOLUMES} до {cls.MAX_VOLUMES}"]

        circulation = data.get("circulation")
        if not (cls.MIN_CIRCULATION <= circulation <= cls.MAX_CIRCULATION):
            errors["circulation"] = [f"От {cls.MIN_CIRCULATION} до {cls.MAX_CIRCULATION}"]

        return ValidationResult(is_valid=len(errors) == 0, errors=errors)
