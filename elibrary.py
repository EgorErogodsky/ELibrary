from Bibla2 import *
from elib_db_connector import *


def fill_table(table, data):
    table.setRowCount(len(data))
    for m, row in enumerate(data):
        for n, elem in enumerate(row):
            item = QtWidgets.QTableWidgetItem()
            item.setData(QtCore.Qt.EditRole, elem)
            table.setItem(m, n, item)
    table.resizeColumnsToContents()
    table.resizeRowsToContents()


class ELibrary(Ui_MainWindow):
    def __init__(self):
        self.elib_dbc = ElibDBConnector(host='localhost',
                                        user='root',
                                        password='root',
                                        database='elibrary')

    def retranslateUi(self, MainWindow):
        super().retranslateUi(MainWindow)

        self.SearchButton.clicked.connect(self._search)
        self.DeleteButton.clicked.connect(self._delete)
        self.AddButton.clicked.connect(self._add)

        self.IdEdit.textEdited.connect(self._id_edit_changed)

        self._update_table('books')
        self._update_table('readers')
        self._update_table('checked_out_books')

    def _id_edit_changed(self):
        if id := self.IdEdit.text() != "":
            self.AuthorEdit.setDisabled(True)
            self.AuthorCheckBox.setDisabled(True)
            self.BooknameEdit.setDisabled(True)
            self.BookNameCheckbox.setDisabled(True)
            self.YearEdit.setDisabled(True)
            self.YearcomboBox.setDisabled(True)
        else:
            self.AuthorEdit.setDisabled(False)
            self.AuthorCheckBox.setDisabled(False)
            self.BooknameEdit.setDisabled(False)
            self.BookNameCheckbox.setDisabled(False)
            self.YearEdit.setDisabled(False)
            self.YearcomboBox.setDisabled(False)

    def _search(self):
        if id := self.IdEdit.text() != "":
            search_res = self.elib_dbc.search_book_by_id(id)

        author = self.AuthorEdit.text()
        author_strict = self.AuthorCheckBox.isChecked()
        name = self.BooknameEdit.text()
        name_strict = self.BookNameCheckbox.isChecked()
        year_of_publishing = self.YearEdit.text()
        year_sign = self.YearcomboBox.currentText()
        search_res = self.elib_dbc.flexible_books_search(author=author,
                                                         title=name,
                                                         year_of_publishing=year_of_publishing,
                                                         author_accurate=author_strict,
                                                         title_accurate=name_strict,
                                                         year_sign=year_sign)
        fill_table(self.BooksTable, search_res)

    def _delete(self):
        if self.ResultsTab.currentIndex() == 0:
            row = self.BooksTable.currentRow()
            id = self.BooksTable.itemAt(row, 0).text()
            self.elib_dbc.delete_book_or_reader('books', id)
            self._update_table('books')
        elif self.ResultsTab.currentIndex() == 1:
            row = self.ReadersTable.currentRow()
            id = self.ReadersTable.itemAt(row, 0).text()
            self.elib_dbc.delete_book_or_reader('readers', id)
            self._update_table('readers')
        elif self.ResultsTab.currentIndex() == 2:
            row = self.GivenTable.currentRow()
            book_id = self.GivenTable.itemAt(row, 0).text()
            library_card = self.GivenTable.itemAt(row, 1).text()
            self.elib_dbc.delete_checked_book(book_id, library_card)
            self._update_table('checked_out_books')
        else:
            raise ValueError

    def _add(self):
        # TODO: добавление
        # rowPosition = self.ReadersTable.rowCount()
        # self.ReadersTable.insertRow(rowPosition)
        if self.ResultsTab.currentIndex() == 0:
            print("Книги")
        if self.ResultsTab.currentIndex() == 1:
            print("Читатели")
        if self.ResultsTab.currentIndex() == 2:
            print("Выданные книги")

    def _update_table(self, table_name):
        if table_name == 'books':
            table = self.BooksTable
        elif table_name == 'readers':
            table = self.ReadersTable
        elif table_name == 'checked_out_books':
            table = self.GivenTable
        else:
            raise ValueError('Неверное имя таблицы!')
        data = self.elib_dbc.get_table_data(table_name)
        fill_table(table, data)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    elib = ELibrary()
    elib.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
