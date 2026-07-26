from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QSpinBox, QPushButton, QFormLayout,
                             QMessageBox, QGroupBox)

from validators.book_validator import BookValidator


class EditDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.result_data = None
        self.setWindowTitle("Добавление книги")
        self.setMinimumWidth(450)
        self._init_ui()
        self._setup_input_filters()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        group = QGroupBox("Параметры книги")
        form = QFormLayout()

        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Введите название книги")

        self.author_edit = QLineEdit()
        self.author_edit.setPlaceholderText("Фамилия Имя Отчество")

        self.publisher_edit = QLineEdit()
        self.publisher_edit.setPlaceholderText("Введите издательство")

        self.volumes_spin = QSpinBox()
        self.volumes_spin.setRange(BookValidator.MIN_VOLUMES, BookValidator.MAX_VOLUMES)
        self.volumes_spin.setValue(1)
        self.volumes_spin.setSuffix(" том(ов)")

        self.circulation_spin = QSpinBox()
        self.circulation_spin.setRange(BookValidator.MIN_CIRCULATION, BookValidator.MAX_CIRCULATION)
        self.circulation_spin.setValue(100)
        self.circulation_spin.setSuffix(" экз.")

        self.total_label = QLabel("0")
        self.total_label.setStyleSheet("font-weight: bold; color: #0056b3;")

        form.addRow("Название книги:", self.title_edit)
        form.addRow("ФИО автора:", self.author_edit)
        form.addRow("Издательство:", self.publisher_edit)
        form.addRow("Число томов:", self.volumes_spin)
        form.addRow("Тираж:", self.circulation_spin)
        form.addRow("Итого томов:", self.total_label)
        group.setLayout(form)
        layout.addWidget(group)

        self.volumes_spin.valueChanged.connect(self._update_total)
        self.circulation_spin.valueChanged.connect(self._update_total)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("💾 Сохранить")
        cancel_btn = QPushButton("❌ Отмена")
        save_btn.clicked.connect(self._save)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        self._update_total()

    def _setup_input_filters(self):
        """Блокировка ввода недопустимых символов на уровне ОС/Qt"""
        text_regex = QRegularExpression(r'^[А-Яа-яЁёA-Za-z0-9\s\.\,\-\"\']*$')
        self.title_edit.setValidator(QRegularExpressionValidator(text_regex))
        self.publisher_edit.setValidator(QRegularExpressionValidator(text_regex))

        name_regex = QRegularExpression(r'^[А-Яа-яЁёA-Za-z\s\.\-]*$')
        self.author_edit.setValidator(QRegularExpressionValidator(name_regex))

    def _highlight_field(self, widget, has_error=True, message=""):
        """Визуальная подсветка ошибочного поля"""
        if has_error:
            widget.setStyleSheet("border: 2px solid #dc3545; background-color: #fff5f5;")
            widget.setToolTip(message)
        else:
            widget.setStyleSheet("")
            widget.setToolTip("")

    def _update_total(self):
        """Пересчёт: Число томов × Тираж"""
        total = self.volumes_spin.value() * self.circulation_spin.value()
        self.total_label.setText(f"{total:,}".replace(",", " "))

    def _save(self):
        """Делегирование проверки в BookValidator"""
        for w in (self.title_edit, self.author_edit, self.publisher_edit):
            self._highlight_field(w, False)

        data = {
            "name": self.title_edit.text().strip(),
            "author": self.author_edit.text().strip(),
            "publisher": self.publisher_edit.text().strip(),
            "number_of_volumes": self.volumes_spin.value(),
            "circulation": self.circulation_spin.value()
        }

        result = BookValidator.validate(data)

        if not result.is_valid:
            error_msgs = []
            for field_name, msgs in result.errors.items():
                if field_name == "name":
                    self._highlight_field(self.title_edit, True, msgs[0])
                elif field_name == "author":
                    self._highlight_field(self.author_edit, True, msgs[0])
                elif field_name == "publisher":
                    self._highlight_field(self.publisher_edit, True, msgs[0])
                error_msgs.extend(msgs)

            QMessageBox.warning(self, "Ошибка валидации", "• " + "\n• ".join(error_msgs))

            if "name" in result.errors:
                self.title_edit.setFocus()
            elif "author" in result.errors:
                self.author_edit.setFocus()
            elif "publisher" in result.errors:
                self.publisher_edit.setFocus()
            return

        self.result_data = data
        self.accept()