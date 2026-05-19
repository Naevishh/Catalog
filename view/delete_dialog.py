# views/delete_dialog.py
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QSpinBox, QPushButton, QTableWidget,
                             QTableWidgetItem, QComboBox, QGroupBox, QFormLayout,
                             QMessageBox, QWidget)
from PyQt6.QtCore import Qt
from model.catalog_manager import CatalogManager


class DeleteDialog(QDialog):
    def __init__(self, model: CatalogManager, parent=None):
        super().__init__(parent)
        self.model = model
        self.setWindowTitle("Удаление записей")
        self.setMinimumSize(700, 450)
        self.deleted_count = 0  # Для отображения в главном окне

        self._init_ui()
        self._connect_signals()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        # === Условия удаления (аналогично поиску) ===
        cond_group = QGroupBox("Условия удаления")
        form = QFormLayout()

        self.author_edit = QLineEdit()
        self.author_edit.setPlaceholderText("Часть ФИО автора")

        self.publisher_edit = QLineEdit()
        self.publisher_edit.setPlaceholderText("Название издательства")

        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Название книги")

        # Диапазон томов
        self.volumes_min = QSpinBox()
        self.volumes_min.setRange(0, 10000)
        self.volumes_max = QSpinBox()
        self.volumes_max.setRange(0, 10000)
        vol_layout = QHBoxLayout()
        vol_layout.addWidget(self.volumes_min)
        vol_layout.addWidget(QLabel("—"))
        vol_layout.addWidget(self.volumes_max)
        vol_widget = QWidget()
        vol_widget.setLayout(vol_layout)

        # Тираж
        self.circ_op = QComboBox()
        self.circ_op.addItems(["", ">", "<"])
        self.circ_val = QSpinBox()
        self.circ_val.setRange(0, 1000000)
        circ_layout = QHBoxLayout()
        circ_layout.addWidget(self.circ_op)
        circ_layout.addWidget(self.circ_val)
        circ_widget = QWidget()
        circ_layout.setContentsMargins(0, 0, 0, 0)
        circ_widget.setLayout(circ_layout)

        # Итого томов
        self.total_op = QComboBox()
        self.total_op.addItems(["", ">", "<"])
        self.total_val = QSpinBox()
        self.total_val.setRange(0, 10000000)
        total_layout = QHBoxLayout()
        total_layout.addWidget(self.total_op)
        total_layout.addWidget(self.total_val)
        total_widget = QWidget()
        total_layout.setContentsMargins(0, 0, 0, 0)
        total_widget.setLayout(total_layout)

        form.addRow("ФИО автора:", self.author_edit)
        form.addRow("Издательство + автор:", self.publisher_edit)
        form.addRow("Название книги:", self.title_edit)
        form.addRow("Число томов:", vol_widget)
        form.addRow("Тираж:", circ_widget)
        form.addRow("Итого томов:", total_widget)
        cond_group.setLayout(form)
        layout.addWidget(cond_group)

        # Кнопки: предпросмотр / удалить / отмена
        btn_layout = QHBoxLayout()
        self.preview_btn = QPushButton("👁 Предпросмотр")
        self.delete_btn = QPushButton("🗑 Удалить")
        self.cancel_btn = QPushButton("Отмена")
        self.delete_btn.setStyleSheet("background-color: #f44336; color: white;")

        btn_layout.addWidget(self.preview_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        # Таблица предпросмотра
        self.preview_label = QLabel("Нажмите «Предпросмотр», чтобы увидеть записи для удаления")
        layout.addWidget(self.preview_label)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Название", "Автор", "Издательство",
            "Томов", "Тираж", "Итого"
        ])
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)

    def _connect_signals(self):
        self.preview_btn.clicked.connect(self._preview_delete)
        self.delete_btn.clicked.connect(self._confirm_and_delete)
        self.cancel_btn.clicked.connect(self.reject)

    def _collect_criteria(self):
        author = self.author_edit.text().strip() or None
        publisher = self.publisher_edit.text().strip() or None
        title = self.title_edit.text().strip() or None

        v_min = self.volumes_min.value() if self.volumes_min.value() > 0 else None
        v_max = self.volumes_max.value() if self.volumes_max.value() < 10000 else None
        volumes_range = (v_min, v_max) if (v_min or v_max) else None

        circ_op = self.circ_op.currentText()
        circ_val = self.circ_val.value()
        circulation_limit = (circ_op, circ_val) if circ_op and circ_val > 0 else None

        total_op = self.total_op.currentText()
        total_val = self.total_val.value()
        total_limit = (total_op, total_val) if total_op and total_val > 0 else None

        return {
            'name': title,
            'author': author,
            'publisher': publisher,
            'volumes_range': volumes_range,
            'circulation_limit': circulation_limit,
            'total_volumes_limit': total_limit
        }

    def _preview_delete(self):
        criteria = self._collect_criteria()
        results = self.model.find_book(**criteria)

        if not results:
            QMessageBox.information(self, "Предпросмотр", "Записи не найдены по заданным условиям")
            self.table.setRowCount(0)
            self.preview_label.setText("Ничего не найдено")
            return

        self.table.setRowCount(len(results))
        for row, book in enumerate(results):
            self.table.setItem(row, 0, QTableWidgetItem(book.title))
            self.table.setItem(row, 1, QTableWidgetItem(book.author))
            self.table.setItem(row, 2, QTableWidgetItem(book.publisher))
            self.table.setItem(row, 3, QTableWidgetItem(str(book.volumes)))
            self.table.setItem(row, 4, QTableWidgetItem(str(book.print_run)))
            self.table.setItem(row, 5, QTableWidgetItem(str(book.total_volumes)))

        self.preview_label.setText(f"Найдено записей для удаления: {len(results)}")

    def _confirm_and_delete(self):
        criteria = self._collect_criteria()
        results = self.model.find_book(**criteria)

        if not results:
            QMessageBox.warning(self, "Удаление", "Нет записей для удаления")
            return

        # Подтверждение
        reply = QMessageBox.question(
            self, "Подтверждение",
            f"Удалить {len(results)} записей?\nЭто действие нельзя отменить.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.deleted_count = self.model.delete_by_criteria(**criteria)
            QMessageBox.information(
                self, "Готово",
                f"Удалено записей: {self.deleted_count}" if self.deleted_count > 0
                else "Записи не найдены"
            )
            self.accept()