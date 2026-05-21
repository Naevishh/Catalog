# views/edit_dialog.py
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QSpinBox, QPushButton, QFormLayout,
                             QMessageBox, QGroupBox)


class EditDialog(QDialog):
    """
    VIEW (Диалог ввода данных)
    Отвечает ТОЛЬКО за:
    1. Отрисовку полей ввода и кнопок
    2. Валидацию введённых данных
    3. Автовычисление зависимых полей (Итого томов)
    4. Возврат данных в Controller через атрибут result_data
    НЕ ИМПОРТИРУЕТ и НЕ ВЫЗЫВАЕТ Model.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.result_data = None  # ← Заполняется при успешном сохранении
        self.setWindowTitle("Добавление книги")
        self.setMinimumWidth(450)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        group = QGroupBox("Параметры книги")
        form = QFormLayout()

        # Поля ввода (строки)
        self.title_edit = QLineEdit()
        self.author_edit = QLineEdit()
        self.publisher_edit = QLineEdit()

        # Поля ввода (целые числа, по ТЗ)
        self.volumes_spin = QSpinBox()
        self.volumes_spin.setRange(1, 10000)
        self.volumes_spin.setValue(1)

        self.circulation_spin = QSpinBox()  # тираж
        self.circulation_spin.setRange(1, 1000000)
        self.circulation_spin.setValue(100)

        # Вычисляемое поле (Вариант 15: "итого томов не вводится руками")
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

        # Автоматический пересчёт "Итого томов"
        self.volumes_spin.valueChanged.connect(self._update_total)
        self.circulation_spin.valueChanged.connect(self._update_total)

        # Кнопки
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("💾 Сохранить")
        cancel_btn = QPushButton("❌ Отмена")
        save_btn.clicked.connect(self._save)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        self._update_total()  # Инициализация начального значения

    def _update_total(self):
        """Пересчёт вычисляемого поля: Число томов × Тираж"""
        total = self.volumes_spin.value() * self.circulation_spin.value()
        self.total_label.setText(str(total))

    def _save(self):
        """Валидация UI и подготовка данных для Controller"""
        title = self.title_edit.text().strip()
        author = self.author_edit.text().strip()
        publisher = self.publisher_edit.text().strip()

        if not title:
            QMessageBox.warning(self, "Ошибка валидации", "Введите название книги")
            self.title_edit.setFocus()
            return
        if not author:
            QMessageBox.warning(self, "Ошибка валидации", "Введите ФИО автора")
            self.author_edit.setFocus()
            return

        # Формируем словарь. Ключи совпадают с сигнатурой model.add_book(**kwargs)
        self.result_data = {
            'name': title,
            'author': author,
            'publisher': publisher,
            'circulation': self.circulation_spin.value(),
            'number_of_volumes': self.volumes_spin.value()
        }

        self.accept()  # Закрываем диалог с кодом QDialog.Accepted