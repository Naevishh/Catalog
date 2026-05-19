# views/search_dialog.py
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QSpinBox, QPushButton, QTableWidget,
                             QTableWidgetItem, QComboBox, QGroupBox, QFormLayout,
                             QCheckBox, QWidget, QSizePolicy)
from PyQt6.QtCore import Qt
from model.catalog_manager import CatalogManager


class SearchDialog(QDialog):
    def __init__(self, model: CatalogManager, parent=None):
        super().__init__(parent)
        self.model = model
        self.setWindowTitle("Поиск книг")
        self.setMinimumSize(800, 500)

        self.items_per_page = 10
        self.current_page = 0
        self.search_results = []

        self._init_ui()
        self._connect_signals()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        # === Панель условий поиска ===
        search_group = QGroupBox("Условия поиска")
        form = QFormLayout()

        self.author_edit = QLineEdit()
        self.author_edit.setPlaceholderText("Часть ФИО автора")

        self.publisher_edit = QLineEdit()
        self.publisher_edit.setPlaceholderText("Название издательства")

        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Название книги")

        # Число томов: диапазон
        self.volumes_min = QSpinBox()
        self.volumes_min.setRange(0, 10000)
        self.volumes_max = QSpinBox()
        self.volumes_max.setRange(0, 10000)
        volumes_layout = QHBoxLayout()
        volumes_layout.addWidget(self.volumes_min)
        volumes_layout.addWidget(QLabel("—"))
        volumes_layout.addWidget(self.volumes_max)
        volumes_widget = QWidget()
        volumes_widget.setLayout(volumes_layout)

        # Тираж: сравнение
        self.circulation_op = QComboBox()
        self.circulation_op.addItems(["", ">", "<"])
        self.circulation_val = QSpinBox()
        self.circulation_val.setRange(0, 1000000)
        circulation_layout = QHBoxLayout()
        circulation_layout.addWidget(self.circulation_op)
        circulation_layout.addWidget(self.circulation_val)
        circulation_widget = QWidget()
        circulation_layout.setContentsMargins(0, 0, 0, 0)
        circulation_widget.setLayout(circulation_layout)

        # Итого томов: сравнение
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
        form.addRow("Число томов (диапазон):", volumes_widget)
        form.addRow("Тираж:", circulation_widget)
        form.addRow("Итого томов:", total_widget)

        search_group.setLayout(form)
        layout.addWidget(search_group)

        # Кнопки поиска/сброса
        btn_layout = QHBoxLayout()
        self.search_btn = QPushButton("🔍 Найти")
        self.reset_btn = QPushButton("🗑 Сбросить")
        btn_layout.addWidget(self.search_btn)
        btn_layout.addWidget(self.reset_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # === Таблица результатов ===
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Название", "Автор", "Издательство",
            "Томов", "Тираж", "Итого"
        ])
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)

        # === Пагинация ===
        nav = QHBoxLayout()
        self.btn_first = QPushButton("◀◀")
        self.btn_prev = QPushButton("◀")
        self.btn_next = QPushButton("▶")
        self.btn_last = QPushButton("▶▶")
        self.lbl_info = QLabel()

        for btn in [self.btn_first, self.btn_prev, self.btn_next, self.btn_last]:
            btn.setFixedWidth(50)

        nav.addWidget(self.btn_first)
        nav.addWidget(self.btn_prev)
        nav.addWidget(self.lbl_info)
        nav.addWidget(self.btn_next)
        nav.addWidget(self.btn_last)
        nav.addStretch()
        layout.addLayout(nav)

    def _connect_signals(self):
        self.search_btn.clicked.connect(self._perform_search)
        self.reset_btn.clicked.connect(self._reset_filters)
        self.btn_first.clicked.connect(lambda: self._go_to_page(0))
        self.btn_prev.clicked.connect(self._prev_page)
        self.btn_next.clicked.connect(self._next_page)
        self.btn_last.clicked.connect(lambda: self._go_to_page(self.total_pages - 1))

    def _perform_search(self):
        # Сбор критериев
        author = self.author_edit.text().strip() or None
        publisher = self.publisher_edit.text().strip() or None
        title = self.title_edit.text().strip() or None

        # Диапазон томов
        v_min = self.volumes_min.value() if self.volumes_min.value() > 0 else None
        v_max = self.volumes_max.value() if self.volumes_max.value() < 10000 else None
        volumes_range = (v_min, v_max) if (v_min or v_max) else None

        # Тираж: оператор + значение
        circ_op = self.circulation_op.currentText()
        circ_val = self.circulation_val.value()
        circulation_limit = (circ_op, circ_val) if circ_op and circ_val > 0 else None

        # Итого томов
        total_op = self.total_op.currentText()
        total_val = self.total_val.value()
        total_limit = (total_op, total_val) if total_op and total_val > 0 else None

        # Вызов поиска в модели
        self.search_results = self.model.find_book(
            name=title,
            author=author,
            publisher=publisher,
            volumes_range=volumes_range,
            circulation_limit=circulation_limit,
            total_volumes_limit=total_limit
        )

        self.current_page = 0
        self._update_table()

    def _reset_filters(self):
        self.author_edit.clear()
        self.publisher_edit.clear()
        self.title_edit.clear()
        self.volumes_min.setValue(0)
        self.volumes_max.setValue(10000)
        self.circulation_op.setCurrentIndex(0)
        self.circulation_val.setValue(0)
        self.total_op.setCurrentIndex(0)
        self.total_val.setValue(0)
        self.search_results = []
        self._update_table()

    @property
    def total_pages(self):
        return (len(self.search_results) + self.items_per_page - 1) // self.items_per_page or 1

    def _update_table(self):
        start = self.current_page * self.items_per_page
        end = start + self.items_per_page
        page_items = self.search_results[start:end]

        self.table.setRowCount(len(page_items))
        for row, book in enumerate(page_items):
            self.table.setItem(row, 0, QTableWidgetItem(book.title))
            self.table.setItem(row, 1, QTableWidgetItem(book.author))
            self.table.setItem(row, 2, QTableWidgetItem(book.publisher))
            self.table.setItem(row, 3, QTableWidgetItem(str(book.volumes)))
            self.table.setItem(row, 4, QTableWidgetItem(str(book.print_run)))
            self.table.setItem(row, 5, QTableWidgetItem(str(book.total_volumes)))

        total = len(self.search_results)
        self.lbl_info.setText(f"Стр. {self.current_page + 1}/{self.total_pages} • Найдено: {total}")

        # Блокировка кнопок
        self.btn_first.setEnabled(self.current_page > 0)
        self.btn_prev.setEnabled(self.current_page > 0)
        self.btn_next.setEnabled(self.current_page < self.total_pages - 1)
        self.btn_last.setEnabled(self.current_page < self.total_pages - 1)

    def _go_to_page(self, page: int):
        if 0 <= page < self.total_pages:
            self.current_page = page
            self._update_table()

    def _prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self._update_table()

    def _next_page(self):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self._update_table()