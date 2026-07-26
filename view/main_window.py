from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QCloseEvent
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QPushButton, QLabel, QToolBar,
    QMessageBox, QFileDialog
)
from PyQt6.QtWidgets import QSizePolicy


class MainWindow(QMainWindow):
    """
    VIEW (Представление)
    Отвечает за отрисовку интерфейса и реакцию на действия пользователя.
    """

    request_add = pyqtSignal()
    request_search = pyqtSignal()
    request_delete = pyqtSignal()
    request_save = pyqtSignal()
    request_load = pyqtSignal()
    request_save_db = pyqtSignal(str)
    request_load_db = pyqtSignal(str)
    page_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.controller = None
        self.items_per_page = 10
        self.current_page = 0
        self.total_pages = 1
        self.total_count = 0

        self._init_ui()
        self._connect_ui_signals()

    def set_controller(self, controller):
        """Внедрение контроллера. Вызывается из main.py после создания объектов."""
        self.controller = controller

    def _init_ui(self):
        self.setWindowTitle("Каталог книг (Вариант 15)")
        self.resize(1000, 650)

        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("Файл")
        file_menu.addAction("Сохранить в XML...", self._on_save)
        file_menu.addAction("Загрузить из XML...", self._on_load)
        file_menu.addAction("Сохранить в базу данных...", self._on_save_db)
        file_menu.addAction("Загрузить из базы данных...", self._on_load_db)
        file_menu.addSeparator()
        file_menu.addAction("Выход", self.close)

        actions_menu = menu_bar.addMenu("Действия")
        actions_menu.addAction("Добавить книгу...", self._on_add)
        actions_menu.addAction("Поиск...", self._on_search)
        actions_menu.addAction("Удалить по условию...", self._on_delete)

        toolbar = QToolBar("Инструменты")
        self.addToolBar(toolbar)
        toolbar.addAction("➕ Добавить", self._on_add)
        toolbar.addAction("🔍 Поиск", self._on_search)
        toolbar.addAction("🗑 Удалить", self._on_delete)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Название книги", "ФИО автора", "Издательство",
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

        self.lbl_info = QLabel("Стр. 0/0 • Всего: 0")
        self.lbl_info.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lbl_info.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        for btn in [self.btn_first, self.btn_prev, self.btn_next, self.btn_last]:
            btn.setFixedWidth(50)

        nav.addStretch()
        nav.addWidget(self.btn_first)
        nav.addWidget(self.btn_prev)

        nav.addWidget(self.lbl_info)
        nav.addWidget(self.btn_next)
        nav.addWidget(self.btn_last)
        nav.addStretch()

        layout.addLayout(nav)

    def _connect_ui_signals(self):
        self.btn_first.clicked.connect(lambda: self._go_to_page(0))
        self.btn_prev.clicked.connect(lambda: self._go_to_page(self.current_page - 1))
        self.btn_next.clicked.connect(lambda: self._go_to_page(self.current_page + 1))
        self.btn_last.clicked.connect(lambda: self._go_to_page(self.total_pages - 1))

    def _go_to_page(self, page: int):
        if 0 <= page < self.total_pages:
            self.current_page = page
            self.page_changed.emit(page)

    def _on_add(self):
        self.request_add.emit()

    def _on_search(self):
        self.request_search.emit()

    def _on_delete(self):
        self.request_delete.emit()

    def _on_save(self):
        self.request_save.emit()

    def _on_load(self):
        self.request_load.emit()

    def _on_save_db(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Сохранить каталог", "data", "SQLite Files (*.db)")
        if filename: self.request_save_db.emit(filename)

    def _on_load_db(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Загрузить каталог", "data", "SQLite Files (*.db)")
        if filename: self.request_load_db.emit(filename)

    def update_table(self, books: list, page: int, page_size: int, total_count: int):
        """Controller вызывает этот метод, чтобы отрисовать данные."""
        self.table.setRowCount(len(books))
        for row, book in enumerate(books):
            self.table.setItem(row, 0, QTableWidgetItem(book.name))
            self.table.setItem(row, 1, QTableWidgetItem(book.author))
            self.table.setItem(row, 2, QTableWidgetItem(book.publisher))
            self.table.setItem(row, 3, QTableWidgetItem(str(book.volumes)))
            self.table.setItem(row, 4, QTableWidgetItem(str(book.circulation)))
            self.table.setItem(row, 5, QTableWidgetItem(str(book.total_volumes)))

        self.current_page = page
        self.items_per_page = page_size
        self.total_count = total_count
        self.total_pages = (total_count + page_size - 1) // page_size if total_count > 0 else 1

        self.lbl_info.setText(
            f"Стр. {self.current_page + 1}/{self.total_pages} • "
            f"Всего: {self.total_count} • Показано: {len(books)}"
        )

        self.btn_first.setEnabled(self.current_page > 0)
        self.btn_prev.setEnabled(self.current_page > 0)
        self.btn_next.setEnabled(self.current_page < self.total_pages - 1)
        self.btn_last.setEnabled(self.current_page < self.total_pages - 1)

    def show_info(self, title: str, message: str):
        QMessageBox.information(self, title, message)

    def show_error(self, title: str, message: str):
        QMessageBox.critical(self, title, message)

    def ask_confirmation(self, title: str, message: str) -> bool:
        return QMessageBox.question(
            self, title, message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        ) == QMessageBox.StandardButton.Yes

    def closeEvent(self, event: QCloseEvent):
        """
        Перехватывает событие закрытия окна.
        Вызывается при нажатии на крестик, Alt+F4 или self.close().
        """
        # Опционально: спрашиваем подтверждение перед выходом
        if self.controller:
            self.controller.cleanup()

        # Разрешаем закрытие окна
        event.accept()
