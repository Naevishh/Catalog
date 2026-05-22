from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QSpinBox, QPushButton, QTableWidget,
                             QTableWidgetItem, QComboBox, QGroupBox, QFormLayout,
                             QWidget, QMessageBox, QHeaderView)


class DeleteDialog(QDialog):
    """
    VIEW (Диалог удаления)
    """

    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.controller = controller
        self.deleted_count = 0
        self.preview_results = []

        self.setWindowTitle("Удаление записей по условию")
        self.resize(850, 550)

        self._init_ui()
        self._connect_signals()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        cond_group = QGroupBox("Условия удаления")
        form = QFormLayout()

        self.author_edit = QLineEdit()
        self.author_edit.setPlaceholderText("ФИО автора (часть или полностью)")

        self.publisher_edit = QLineEdit()
        self.publisher_edit.setPlaceholderText("Издательство")

        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Название книги")

        self.vol_min = QSpinBox()
        self.vol_min.setRange(1, 10000)
        self.vol_max = QSpinBox()
        self.vol_max.setRange(1, 10000)
        vol_layout = QHBoxLayout()
        vol_layout.addWidget(self.vol_min)
        vol_layout.addWidget(QLabel("—"))
        vol_layout.addWidget(self.vol_max)
        vol_widget = QWidget()
        vol_widget.setLayout(vol_layout)

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
        form.addRow("Издательство:", self.publisher_edit)
        form.addRow("Название книги:", self.title_edit)
        form.addRow("Число томов (диапазон):", vol_widget)
        form.addRow("Тираж (больше/меньше):", circ_widget)
        form.addRow("Итого томов (больше/меньше):", total_widget)
        cond_group.setLayout(form)
        layout.addWidget(cond_group)

        btn_layout = QHBoxLayout()
        self.preview_btn = QPushButton("👁 Предпросмотр")
        self.delete_btn = QPushButton("🗑 Удалить")
        self.delete_btn.setStyleSheet("background-color: #e74c3c; color: white; font-weight: bold;")
        self.cancel_btn = QPushButton("❌ Отмена")

        btn_layout.addWidget(self.preview_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self.lbl_preview_info = QLabel("Нажмите «Предпросмотр», чтобы увидеть записи для удаления")
        layout.addWidget(self.lbl_preview_info)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Название", "ФИО автора", "Издательство",
            "Томов", "Тираж", "Итого томов"
        ])
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

    def _connect_signals(self):
        self.preview_btn.clicked.connect(self._preview)
        self.delete_btn.clicked.connect(self._execute_delete)
        self.cancel_btn.clicked.connect(self.reject)

    def _collect_criteria(self) -> dict:
        """Сбор условий"""
        author = self.author_edit.text().strip() or None
        publisher = self.publisher_edit.text().strip() or None
        title = self.title_edit.text().strip() or None

        v_min = self.vol_min.value() if self.vol_min.value() > 0 else None
        v_max = self.vol_max.value() if self.vol_max.value() < 10000 else None
        volumes_range = (v_min, v_max) if (v_min is not None or v_max is not None) else None

        circ_op = self.circ_op.currentText()
        circ_val = self.circ_val.value()
        circulation_limit = (circ_op, circ_val) if circ_op and circ_val > 0 else None

        total_op = self.total_op.currentText()
        total_val = self.total_val.value()
        total_volumes_limit = (total_op, total_val) if total_op and total_val > 0 else None

        return {
            'name': title,
            'author': author,
            'publisher': publisher,
            'volumes_range': volumes_range,
            'circulation_limit': circulation_limit,
            'total_volumes_limit': total_volumes_limit
        }

    def _preview(self):
        """Предпросмотр: делегирует поиск контроллеру"""
        criteria = self._collect_criteria()

        if all(v is None for v in criteria.values()):
            QMessageBox.warning(self, "Предпросмотр", "Укажите хотя бы одно условие для поиска.")
            return

        if self.controller:
            self.preview_results = self.controller.perform_search(criteria)
        else:
            self.preview_results = []

        self._render_preview()

    def _render_preview(self):
        """Отрисовка таблицы предпросмотра"""
        self.table.setRowCount(len(self.preview_results))
        for row, book in enumerate(self.preview_results):
            self.table.setItem(row, 0, QTableWidgetItem(book.name))
            self.table.setItem(row, 1, QTableWidgetItem(book.author))
            self.table.setItem(row, 2, QTableWidgetItem(book.publisher))
            self.table.setItem(row, 3, QTableWidgetItem(str(book.volumes)))
            self.table.setItem(row, 4, QTableWidgetItem(str(book.circulation)))
            self.table.setItem(row, 5, QTableWidgetItem(str(book.total_volumes)))

        if self.preview_results:
            self.lbl_preview_info.setText(f"🔍 Найдено записей для удаления: {len(self.preview_results)}")
        else:
            self.lbl_preview_info.setText("⚠ Записи, соответствующие условиям, не найдены")

    def _execute_delete(self):
        """Подтверждение и выполнение удаления через контроллер"""
        if not self.preview_results:
            QMessageBox.warning(self, "Удаление", "Сначала выполните предпросмотр, чтобы выбрать записи.")
            return

        reply = QMessageBox.question(
            self, "Подтверждение удаления",
            f"Вы действительно хотите удалить {len(self.preview_results)} записей?\n"
            f"Это действие нельзя отменить.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            criteria = self._collect_criteria()
            if self.controller:
                self.deleted_count = self.controller.perform_delete(criteria)
            else:
                self.deleted_count = 0

            self.accept()
