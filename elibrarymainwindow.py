import BookAskWindow
import ReaderAskWindow
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


class ELibraryMainWindow(Ui_MainWindow):
    def __init__(self):
        self.elib_dbc = ElibDBConnector(host='localhost',
                                        user='root',
                                        password='root',
                                        database='elibrary')

    def retranslateUi(self, MainWindow):
        super().retranslateUi(MainWindow)

        self.SearchButton.clicked.connect(self._search)
        self.DeleteButton.clicked.connect(self._delete)
        self.AddButton.clicked.connect(self._add_window)

        self.IdEdit.textEdited.connect(self._id_edit_changed)

        self.BooksTable.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.ReadersTable.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.GivenTable.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        self.update_table('books')
        self.update_table('readers')
        self.update_table('checked_out_books')

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
            id = self.BooksTable.item(row, 0).text()
            self.elib_dbc.delete_book_or_reader('books', id)
            self.update_table('books')
        elif self.ResultsTab.currentIndex() == 1:
            row = self.ReadersTable.currentRow()
            id = self.ReadersTable.item(row, 0).text()
            self.elib_dbc.delete_book_or_reader('readers', id)
            self.update_table('readers')
        elif self.ResultsTab.currentIndex() == 2:
            row = self.GivenTable.currentRow()
            book_id = self.GivenTable.item(row, 0).text()
            library_card = self.GivenTable.item(row, 1).text()
            self.elib_dbc.delete_checked_book(book_id, library_card)
            self.update_table('checked_out_books')
        else:
            raise ValueError

    def _add_window(self):
        if self.ResultsTab.currentIndex() == 0:
            self.AddbookWindow = QtWidgets.QMainWindow()
            ui = ELibraryAddBookWindow(self, self.elib_dbc)
            ui.setupUi(self.AddbookWindow)
            self.AddbookWindow.show()
        elif self.ResultsTab.currentIndex() == 1:
            self.AddreaderWindow = QtWidgets.QMainWindow()
            ui = ELibraryAddReaderWindow(self, self.elib_dbc)
            ui.setupUi(self.AddreaderWindow)
            self.AddreaderWindow.show()
        elif self.ResultsTab.currentIndex() == 2:
            print("Выданные книги")

    def update_table(self, table_name):
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


class ELibraryAddReaderWindow(ReaderAskWindow.Ui_AddbookWindow):
    def __init__(self, elib, elib_dbc):
        self.window = None
        self.elib_dbc = elib_dbc
        self.elib = elib

    def retranslateUi(self, AddReaderWindow):
        super().retranslateUi(AddReaderWindow)
        self.window = AddReaderWindow

        def cancel():
            self.window.hide()

        def insert():
            surname = self.SecondNameEdit.text()
            name = self.NameEdit.text()
            patronymic = self.FathernameEdit.text()
            address = self.AdresEdit.text()
            self.elib_dbc.add_reader(surname=surname,
                                     name=name,
                                     patronymic=patronymic,
                                     address=address)
            self.elib.update_table('readers')

        self.CancelButton.clicked.connect(cancel)
        self.InsertButton.clicked.connect(insert)


class ELibraryAddBookWindow(BookAskWindow.Ui_AddbookWindow):
    def __init__(self, elib, elib_dbc):
        self.window = None
        self.elib_dbc = elib_dbc
        self.elib = elib

    def retranslateUi(self, AddbookWindow):
        super().retranslateUi(AddbookWindow)
        self.window = AddbookWindow

        def cancel():
            self.window.hide()

        def insert():
            author = self.AuthorEdit.text()
            title = self.BooknameEdit.text()
            year_of_publishing = self.YearEdit.text()
            num_of_copies = self.AmountEdit.text()
            self.elib_dbc.add_book(author=author,
                                   title=title,
                                   year_of_publishing=year_of_publishing,
                                   num_of_copies=num_of_copies)
            self.elib.update_table('books')

        self.CancelButton.clicked.connect(cancel)
        self.InsertButton.clicked.connect(insert)
        # self.window = AddbookWindow


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    elib = ELibraryMainWindow()
    elib.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
