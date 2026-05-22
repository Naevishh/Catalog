from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QSpinBox, QPushButton, QTableWidget,
                             QTableWidgetItem, QComboBox, QGroupBox, QFormLayout,
                             QWidget, QHeaderView)


class SearchDialog(QDialog):
    """
    VIEW (Диалог поиска)
    Отвечает за:
    1. Отрисовку условий поиска и таблицы результатов
    2. Сбор критериев из интерфейса
    3. Постраничный вывод результатов (требование лабы)
    """

    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.controller = controller
        self.setWindowTitle("Поиск книг")
        self.resize(900, 650)

        self.items_per_page = 10
        self.current_page = 0
        self.search_results = []

        self._init_ui()
        self._connect_signals()
        self.vol_max.setValue(10000)

    def _init_ui(self):
        layout = QVBoxLayout(self)

        search_group = QGroupBox("Условия поиска")
        form = QFormLayout()

        self.author_edit = QLineEdit()
        self.author_edit.setPlaceholderText("Часть ФИО автора")

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
        vol_widget = QWidget(self)
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
        search_group.setLayout(form)
        layout.addWidget(search_group)

        btn_layout = QHBoxLayout()
        self.search_btn = QPushButton("🔍 Найти")
        self.reset_btn = QPushButton("🗑 Сбросить")
        btn_layout.addWidget(self.search_btn)
        btn_layout.addWidget(self.reset_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Название", "ФИО автора", "Издательство",
            "Число томов", "Тираж", "Итого томов"
        ])
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

        nav = QHBoxLayout()
        self.btn_first = QPushButton("◀◀")
        self.btn_prev = QPushButton("◀")
        self.btn_next = QPushButton("▶")
        self.btn_last = QPushButton("▶▶")

        self.btn_first.setEnabled(self.current_page > 0)
        self.btn_prev.setEnabled(self.current_page > 0)
        self.btn_next.setEnabled(self.current_page < self.total_pages - 1)
        self.btn_last.setEnabled(self.current_page < self.total_pages - 1)

        self.spin_page_size = QSpinBox()
        self.spin_page_size.setRange(5, 50)
        self.spin_page_size.setValue(self.items_per_page)
        self.spin_page_size.setFixedWidth(60)

        self.lbl_info = QLabel()

        for btn in [self.btn_first, self.btn_prev, self.btn_next, self.btn_last]:
            btn.setFixedWidth(45)

        nav.addWidget(self.btn_first)
        nav.addWidget(self.btn_prev)

        nav.addSpacing(15)
        nav.addWidget(self.lbl_info)
        nav.addStretch()
        nav.addWidget(self.btn_next)
        nav.addWidget(self.btn_last)
        layout.addLayout(nav)

    def _connect_signals(self):
        self.search_btn.clicked.connect(self._perform_search)
        self.reset_btn.clicked.connect(self._reset_filters)

        self.btn_first.clicked.connect(lambda: self._go_to_page(0))
        self.btn_prev.clicked.connect(lambda: self._go_to_page(self.current_page - 1))
        self.btn_next.clicked.connect(lambda: self._go_to_page(self.current_page + 1))
        self.btn_last.clicked.connect(lambda: self._go_to_page(self.total_pages - 1))

        self.spin_page_size.valueChanged.connect(self._on_page_size_changed)

    def _collect_criteria(self) -> dict:
        """Сбор данных из полей ввода в формат, понятный модели."""
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

    def _perform_search(self):
        """Выполняет поиск, делегируя задачу контроллеру."""
        criteria = self._collect_criteria()

        if self.controller:
            self.search_results = self.controller.perform_search(criteria)
        else:
            self.search_results = []

        self.current_page = 0
        self._update_table()

    def _reset_filters(self):
        """Очистка полей и таблицы."""
        self.author_edit.clear()
        self.publisher_edit.clear()
        self.title_edit.clear()
        self.vol_min.setValue(0)
        self.vol_max.setValue(10000)
        self.circ_op.setCurrentIndex(0)
        self.circ_val.setValue(0)
        self.total_op.setCurrentIndex(0)
        self.total_val.setValue(0)

        self.search_results = []
        self.current_page = 0
        self._update_table()

    @property
    def total_pages(self):
        return max(1, (len(self.search_results) + self.items_per_page - 1) // self.items_per_page)

    def _update_table(self):
        """Отрисовка текущей страницы результатов."""
        start = self.current_page * self.items_per_page
        end = start + self.items_per_page
        page_items = self.search_results[start:end]

        self.table.setRowCount(len(page_items))
        for row, book in enumerate(page_items):
            self.table.setItem(row, 0, QTableWidgetItem(book.name))
            self.table.setItem(row, 1, QTableWidgetItem(book.author))
            self.table.setItem(row, 2, QTableWidgetItem(book.publisher))
            self.table.setItem(row, 3, QTableWidgetItem(str(book.volumes)))
            self.table.setItem(row, 4, QTableWidgetItem(str(book.circulation)))
            self.table.setItem(row, 5, QTableWidgetItem(str(book.total_volumes)))

        total = len(self.search_results)
        self.lbl_info.setText(
            f"Стр. {self.current_page + 1}/{self.total_pages} • Найдено: {total}"
        )

        self.btn_first.setEnabled(self.current_page > 0)
        self.btn_prev.setEnabled(self.current_page > 0)
        self.btn_next.setEnabled(self.current_page < self.total_pages - 1)
        self.btn_last.setEnabled(self.current_page < self.total_pages - 1)

    def _go_to_page(self, page: int):
        if 0 <= page < self.total_pages:
            self.current_page = page
            self._update_table()

    def _on_page_size_changed(self, value: int):
        self.items_per_page = value
        self.current_page = 0
        self._update_table()
