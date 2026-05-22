from typing import Dict, List

from model.catalog_manager import CatalogManager
from view.add_dialog import EditDialog
from view.delete_dialog import DeleteDialog
from view.main_window import MainWindow
from view.search_dialog import SearchDialog


class CatalogController:
    """
    CONTROLLER (Контроллер)
    Связывает View и Model. Обрабатывает сигналы интерфейса, управляет диалогами,
    вызывает бизнес-логику и обновляет представление.
    """

    def __init__(self, model: CatalogManager, view: MainWindow):
        self.model = model
        self.view = view

        self.view.set_controller(self)

        self._connect_signals()

        self._refresh_main_view()

    def _connect_signals(self):
        self.view.request_add.connect(self._handle_add)
        self.view.request_search.connect(self._handle_search)
        self.view.request_delete.connect(self._handle_delete)
        self.view.request_save.connect(self._handle_save)
        self.view.request_load.connect(self._handle_load)
        self.view.page_changed.connect(self._handle_page_change)

    def _handle_page_change(self, page: int):
        """Смена страницы или размера страницы в главном окне"""
        self._refresh_main_view(page)

    def _refresh_main_view(self, page: int = None):
        """Обновление таблицы главного окна с учётом пагинации"""
        if page is None:
            page = self.view.current_page

        total_count = len(self.model.books)
        page_size = self.view.items_per_page
        total_pages = max(1, (total_count + page_size - 1) // page_size)

        if page >= total_pages:
            page = total_pages - 1
            self.view.current_page = page

        start = page * page_size
        end = start + page_size
        page_books = self.model.books[start:end]

        self.view.update_table(page_books, page, page_size, total_count)

    def _handle_add(self):
        """Открытие диалога добавления/редактирования"""
        dlg = EditDialog(parent=self.view)
        if dlg.exec() and dlg.result_data:
            try:
                self.model.add_book(**dlg.result_data)
                self.view.show_info("Добавление", "Книга успешно добавлена в каталог.")
                self._refresh_main_view(0)
            except Exception as e:
                self.view.show_error("Ошибка добавления", str(e))

    def _handle_search(self):
        """Открытие диалога поиска"""
        dlg = SearchDialog(parent=self.view, controller=self)
        dlg.exec()

    def _handle_delete(self):
        """Открытие диалога удаления"""
        dlg = DeleteDialog(parent=self.view, controller=self)
        if dlg.exec():
            count = dlg.deleted_count
            if count > 0:
                self.view.show_info("Удаление", f"Успешно удалено записей: {count}")
                self._refresh_main_view(0)
            else:
                self.view.show_info("Удаление", "Записи не найдены или не были удалены.")

    def _handle_save(self):
        """Сохранение в XML (DOM-парсер вызывается внутри Model)"""
        try:
            self.model.save_to_xml()
            self.view.show_info("Сохранение", "Каталог успешно сохранён в XML.")
        except Exception as e:
            self.view.show_error("Ошибка сохранения", str(e))

    def _handle_load(self):
        """Загрузка из XML (SAX-парсер вызывается внутри Model)"""
        try:
            self.model.load_from_xml()
            self.view.show_info("Загрузка", "Каталог успешно загружен из XML.")
            self._refresh_main_view(0)
        except Exception as e:
            self.view.show_error("Ошибка загрузки", str(e))

    def perform_search(self, criteria: Dict) -> List:
        """Вызывается из SearchDialog. Делегирует поиск модели."""
        return self.model.find_book(**criteria)

    def perform_delete(self, criteria: Dict) -> int:
        """Вызывается из DeleteDialog. Делегирует удаление модели."""
        return self.model.delete_by_criteria(**criteria)
