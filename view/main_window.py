# views/main_window.py (ваш код с доработками)
import sys

from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHBoxLayout, QPushButton, \
    QLabel, QMenuBar, QToolBar, QApplication, QHeaderView
from PyQt6.QtCore import Qt
from model.book import Book
from model.catalog_manager import CatalogManager
from model.xml_handler import XMLHandler

from view.search_dialog import SearchDialog
from view.delete_dialog import DeleteDialog
from view.edit_dialog import EditDialog


class MainWindow(QMainWindow):
    def __init__(self, model: CatalogManager):
        super().__init__()
        self.model = model  # ← ссылка на модель
        self.items_per_page = 10
        self.current_page = 0

        self._init_ui()
        self._connect_signals()
        self.model.add_observer(self)  # подписка на изменения

    def _init_ui(self):
        self.setWindowTitle("Каталог книг")
        self.resize(900, 500)

        # Меню
        menu = self.menuBar()
        file_menu = menu.addMenu("Файл")
        file_menu.addAction("Сохранить как XML...", self.save_xml)
        file_menu.addAction("Загрузить из XML...", self.load_xml)
        file_menu.addSeparator()
        file_menu.addAction("Выход", self.close)

        edit_menu = menu.addMenu("Действия")
        edit_menu.addAction("Добавить книгу...", self.open_edit_dialog)
        edit_menu.addAction("Поиск...", self.open_search_dialog)
        edit_menu.addAction("Удалить...", self.open_delete_dialog)

        # Панель инструментов (дублирование команд меню)
        toolbar = QToolBar("Инструменты")
        self.addToolBar(toolbar)
        toolbar.addAction("Добавить", self.open_edit_dialog)
        toolbar.addAction("Поиск", self.open_search_dialog)
        toolbar.addAction("Удалить", self.open_delete_dialog)

        # Центральная область с таблицей
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
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

        # Навигация по страницам
        nav = QHBoxLayout()
        self.btn_first = QPushButton("◀◀")
        self.btn_prev = QPushButton("◀")
        self.btn_next = QPushButton("▶")
        self.btn_last = QPushButton("▶▶")
        self.lbl_info = QLabel()

        for btn in [self.btn_first, self.btn_prev, self.btn_next, self.btn_last]:
            btn.setFixedWidth(60)
        nav.addWidget(self.btn_first)
        nav.addWidget(self.btn_prev)
        nav.addWidget(self.lbl_info)
        nav.addWidget(self.btn_next)
        nav.addWidget(self.btn_last)
        layout.addLayout(nav)

    def _connect_signals(self):
        self.btn_first.clicked.connect(lambda: self.go_to_page(0))
        self.btn_prev.clicked.connect(self.prev_page)
        self.btn_next.clicked.connect(self.next_page)
        self.btn_last.clicked.connect(lambda: self.go_to_page(self.total_pages - 1))

    def model_changed(self):
        self.current_page = 0  # Сброс на первую страницу
        self.update_table()

    # === Диалоги ===
    def open_edit_dialog(self):
        dlg = EditDialog(self.model, parent=self)
        if dlg.exec():
            self.refresh_view()  # обновить таблицу после добавления

    def open_search_dialog(self):
        dlg = SearchDialog(self.model, parent=self)
        dlg.exec()  # поиск отображается внутри диалога, главное окно не меняется

    def open_delete_dialog(self):
        dlg = DeleteDialog(self.model, parent=self)
        if dlg.exec():  # если пользователь подтвердил удаление
            self.refresh_view()
            # Показать сообщение о результате
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(self, "Удаление",
                                    f"Удалено записей: {dlg.deleted_count}" if dlg.deleted_count > 0
                                    else "Записи не найдены")

    # === Работа с таблицей ===
    @property
    def total_pages(self):
        return (len(self.model.books) + self.items_per_page - 1) // self.items_per_page or 1

    def refresh_view(self):
        self.current_page = 0  # сброс на первую страницу при изменении данных
        self.update_table()

    def update_table(self):
        start = self.current_page * self.items_per_page
        end = start + self.items_per_page
        page_books = self.model.books[start:end]

        self.table.setRowCount(len(page_books))
        for row, book in enumerate(page_books):
            self.table.setItem(row, 0, QTableWidgetItem(book.name))
            self.table.setItem(row, 1, QTableWidgetItem(book.author))
            self.table.setItem(row, 2, QTableWidgetItem(book.publisher))
            self.table.setItem(row, 3, QTableWidgetItem(str(book.volumes)))
            self.table.setItem(row, 4, QTableWidgetItem(str(book.circulation)))
            self.table.setItem(row, 5, QTableWidgetItem(str(book.total_volumes)))  # вычисляемое

        total = len(self.model.books)
        self.lbl_info.setText(f"Стр. {self.current_page + 1}/{self.total_pages} • Всего: {total}")

        # Блокировка кнопок
        self.btn_first.setEnabled(self.current_page > 0)
        self.btn_prev.setEnabled(self.current_page > 0)
        self.btn_next.setEnabled(self.current_page < self.total_pages - 1)
        self.btn_last.setEnabled(self.current_page < self.total_pages - 1)

    def go_to_page(self, page: int):
        if 0 <= page < self.total_pages:
            self.current_page = page
            self.update_table()

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.update_table()

    def next_page(self):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.update_table()

    # === XML: сохранение (DOM) / загрузка (SAX) ===
    def save_xml(self):
        self.model.save_to_xml()  # реализуйте в model.py

    def load_xml(self):
        self.model.load_from_xml()  # реализуйте в model.py
        self.refresh_view()


if __name__ == "__main__":

    xmlh=XMLHandler()
    c=CatalogManager(xmlh)
    app = QApplication(sys.argv)
    window = MainWindow(c)
    window.show()
    sys.exit(app.exec())