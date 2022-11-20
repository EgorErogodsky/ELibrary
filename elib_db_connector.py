import mysql.connector


class ElibDBConnector:
    def __init__(self, host, user, password, database):
        self._elib_db = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

        self._elib_db.autocommit = True
        self._cursor = self._elib_db.cursor(buffered=True)

    def add_book(self, author, title, year_of_publishing, num_of_copies):
        add_book = ("INSERT INTO books "
                    "VALUES ((SELECT MAX(book_id) + 1 FROM (SELECT * FROM books) AS books_tmp),"
                    " %(author)s, %(title)s, %(year_of_publishing)s, %(num_of_copies)s)")
        self._cursor.execute(add_book,
                             {'author': author,
                              'title': title,
                              'year_of_publishing': str(year_of_publishing),
                              'num_of_copies': str(num_of_copies)})

    def delete_book_or_reader(self, table, id):
        if table == 'books':
            col = 'book_id'
        elif table == 'readers':
            col = 'library_card'
        else:
            raise ValueError

        delete_rows = ("DELETE FROM {table} "
                       "WHERE {col} = {id};"
                       "DELETE FROM checked_out_books "
                       "WHERE {col} = {id}").format(table=table,
                                                    col=col,
                                                    id=id)
        self._cursor.execute(delete_rows)

    def delete_checked_book(self, book_id, library_card):
        delete_row = ("DELETE FROM checked_out_books "
                      "WHERE book_id = {book_id} "
                      "AND library_card = {library_card}").format(book_id=book_id,
                                                                  library_card=library_card)

    def search_book_by_id(self, id):
        search = ("SELECT * FROM books "
                  "WHERE book_id = %s")
        self._cursor.execute(search, (str(id),))
        return self._cursor.fetchall()

    def flexible_books_search(self,
                              author="",
                              title="",
                              year_of_publishing="",
                              author_accurate=False,
                              title_accurate=False,
                              year_sign="="):
        drop = ("DROP TABLE "
                "IF EXISTS flexible_search")
        self._cursor.execute(drop)

        tab = ("CREATE TABLE flexible_search AS "
               "SELECT * from books")
        self._cursor.execute(tab)

        if author != "":
            tab = ("DELETE FROM flexible_search "
                   "WHERE NOT author ")
            if author_accurate:
                tab += "= %s"
                self._cursor.execute(tab, (author,))
            else:
                tab += "LIKE %s"
                self._cursor.execute(tab, ('%' + author + '%',))

        if title != "":
            tab = ("DELETE FROM flexible_search "
                   "WHERE NOT title ")
            if title_accurate:
                tab += "= %s"
                self._cursor.execute(tab, (title,))
            else:
                tab += "LIKE %s"
                self._cursor.execute(tab, ('%' + title + '%',))

        if year_of_publishing != "":
            tab = ("DELETE FROM flexible_search "
                   "WHERE NOT year_of_publishing " + year_sign + "%s")
            self._cursor.execute(tab, (year_of_publishing,))

        tab = "SELECT * FROM flexible_search"
        self._cursor.execute(tab)

        res = self._cursor.fetchall()

        drop = ("DROP TABLE "
                "IF EXISTS flexible_search")
        self._cursor.execute(drop)

        return res

    def get_table_data(self, table_name):
        table = "SELECT * FROM {table_name}".format(table_name=table_name)
        self._cursor.execute(table)
        return self._cursor.fetchall()
