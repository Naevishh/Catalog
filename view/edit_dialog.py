# views/edit_dialog.py
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QSpinBox, QPushButton, QFormLayout,
                             QMessageBox, QGroupBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIntValidator
from model.catalog_manager import CatalogManager


class EditDialog(QDialog):
    def __init__(self, model: CatalogManager, book=None, parent=None):
        super().__init__(parent)
        self.model = model
        self.book = book  # Если передана — режим редактирования
        self.setWindowTitle("Редактирование книги" if book else "Добавление книги")
        self.setMinimumWidth(400)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        # Группировка полей
        group = QGroupBox("Данные книги")
        form = QFormLayout()

        self.title_edit = QLineEdit()
        self.author_edit = QLineEdit()
        self.publisher_edit = QLineEdit()

        self.volumes_spin = QSpinBox()
        self.volumes_spin.setRange(1, 10000)
        self.volumes_spin.setValue(1)

        self.print_run_spin = QSpinBox()
        self.print_run_spin.setRange(1, 1000000)
        self.print_run_spin.setValue(100)

        # Поле "Итого томов" — только для чтения, вычисляется автоматически
        self.total_volumes_label = QLabel("0")
        self.total_volumes_label.setStyleSheet("font-weight: bold; color: #2196F3;")

        form.addRow("Название книги:", self.title_edit)
        form.addRow("ФИО автора:", self.author_edit)
        form.addRow("Издательство:", self.publisher_edit)
        form.addRow("Число томов:", self.volumes_spin)
        form.addRow("Тираж:", self.print_run_spin)
        form.addRow("Итого томов:", self.total_volumes_label)

        group.setLayout(form)
        layout.addWidget(group)

        # Подключение сигналов для авто-расчёта "Итого томов"
        self.volumes_spin.valueChanged.connect(self._update_total)
        self.print_run_spin.valueChanged.connect(self._update_total)

        # Кнопки
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        cancel_btn = QPushButton("Отмена")
        save_btn.clicked.connect(self._save)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        # Если редактируем — заполняем поля
        if self.book:
            self._fill_from_book()

    def _update_total(self):
        total = self.volumes_spin.value() * self.print_run_spin.value()
        self.total_volumes_label.setText(str(total))

    def _fill_from_book(self):
        self.title_edit.setText(self.book.title)
        self.author_edit.setText(self.book.author)
        self.publisher_edit.setText(self.book.publisher)
        self.volumes_spin.setValue(self.book.volumes)
        self.print_run_spin.setValue(self.book.print_run)
        self._update_total()

    def _save(self):
        # Валидация
        if not self.title_edit.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите название книги")
            return
        if not self.author_edit.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите ФИО автора")
            return

        if self.book:
            # Обновление существующей записи
            self.book.title = self.title_edit.text().strip()
            self.book.author = self.author_edit.text().strip()
            self.book.publisher = self.publisher_edit.text().strip()
            self.book.volumes = self.volumes_spin.value()
            self.book.print_run = self.print_run_spin.value()
            # total_volumes пересчитывается в свойстве Book
        else:
            # Добавление новой
            self.model.add_book(
                name=self.title_edit.text().strip(),
                author=self.author_edit.text().strip(),
                publisher=self.publisher_edit.text().strip(),
                circulation=self.print_run_spin.value(),
                number_of_volumes=self.volumes_spin.value()
            )
        self.accept()