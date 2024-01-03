import sys
import pymysql
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QPushButton, QLabel,
    QLineEdit, QDialog, QMessageBox, QListWidget, QListWidgetItem, 
    QFormLayout, QWidget, QAction, QGridLayout
) 
from datetime import datetime

class AdminLoginDialog(QDialog):
    def __init__(self, parent=None):
        super(AdminLoginDialog, self).__init__(parent)
        self.setWindowTitle('Admin Login')
        self.setGeometry(200, 200, 300, 150)

        layout = QVBoxLayout()

        label_username = QLabel('Username:')
        self.input_username = QLineEdit(self)
        layout.addWidget(label_username)
        layout.addWidget(self.input_username)

        label_password = QLabel('Password:')
        self.input_password = QLineEdit(self)
        self.input_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(label_password)
        layout.addWidget(self.input_password)

        button_login = QPushButton('Login', self)
        button_login.clicked.connect(self.on_login_click)
        layout.addWidget(button_login)

        self.setLayout(layout)

    def on_login_click(self):
        username = self.input_username.text()
        password = self.input_password.text()

        if username == 'admin' and password == 'admin123':
            self.accept()
        else:
            QMessageBox.warning(self, 'Login Failed', 'Invalid username or password.')


class FilmInputDialog(QDialog):
    def __init__(self, film_list, db_connection, parent=None):
        super(FilmInputDialog, self).__init__(parent)
        self.film_list = film_list
        self.db_connection = db_connection

        self.setWindowTitle('Input Film')
        self.setGeometry(200, 200, 300, 150)

        layout = QFormLayout()

        self.input_judul = QLineEdit(self)
        layout.addRow('Judul Film:', self.input_judul)

        self.input_genre = QLineEdit(self)
        layout.addRow('Genre Film:', self.input_genre)

        self.input_jam_tayang = QLineEdit(self)
        layout.addRow('Jam Tayang:', self.input_jam_tayang)

        self.input_seats = QLineEdit(self)
        layout.addRow('Seat:', self.input_seats)

        button_input = QPushButton('Input', self)
        button_input.clicked.connect(self.on_input_click)
        layout.addRow(button_input)

        self.setLayout(layout)

    def on_input_click(self):
        judul = self.input_judul.text()
        genre = self.input_genre.text()
        jam_tayang = self.input_jam_tayang.text()
        seats = self.input_seats.text()

        try:
            if 0 < int(seats) <= 40:
                with self.db_connection.cursor() as cursor:
                    sql = "INSERT INTO film (judul, genre, jam_tayang, seats) VALUES (%s, %s, %s, %s)"
                    cursor.execute(sql, (judul, genre, jam_tayang, seats))
                    self.db_connection.commit()

                    film_data = f'Judul: {judul}, Genre: {genre}, Jam Tayang: {jam_tayang}, Seats: {seats}'
                    item = QListWidgetItem(film_data)
                    self.film_list.addItem(item)
                    self.film_list.sortItems()

                    QMessageBox.information(self, 'Input Film', 'Film berhasil diinput.')
            else:
                QMessageBox.warning(self, 'Error', 'Jumlah seats tidak valid. Harap masukkan nilai antara 1 dan 40.')

        except ValueError:
            QMessageBox.warning(self, 'Error', 'Masukkan nilai seats yang valid.')

        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Gagal menyimpan data film: {str(e)}')

class EditFilmDialog(QDialog):
    def __init__(self, film_list, selected_item, db_connection, parent=None):
        super(EditFilmDialog, self).__init__(parent)
        self.film_list = film_list
        self.selected_item = selected_item
        self.db_connection = db_connection

        self.setWindowTitle('Edit Film')
        self.setGeometry(200, 200, 300, 150)

        layout = QFormLayout()

        self.input_judul = QLineEdit(self)
        self.input_judul.setText(selected_item.text().split(',')[0].split(': ')[1])  # Ambil judul film dari item terpilih
        layout.addRow('Judul Film:', self.input_judul)

        self.input_genre = QLineEdit(self)
        self.input_genre.setText(selected_item.text().split(',')[1].split(': ')[1])  # Ambil genre film dari item terpilih
        layout.addRow('Genre Film:', self.input_genre)

        self.input_jam_tayang = QLineEdit(self)
        self.input_jam_tayang.setText(selected_item.text().split(',')[2].split(': ')[1])  # Ambil jam tayang film dari item terpilih
        layout.addRow('Jam Tayang:', self.input_jam_tayang)

        self.input_seats = QLineEdit(self)
        self.input_seats.setText(selected_item.text().split(',')[3].split(': ')[1]) # Ambil seats film dari item terpilih
        layout.addRow('Seat:', self.input_seats)

        button_save = QPushButton('Simpan', self)
        button_save.clicked.connect(self.on_save_click)
        layout.addRow(button_save)

        self.setLayout(layout)

    def on_save_click(self):
        judul = self.input_judul.text()
        genre = self.input_genre.text()
        jam_tayang = self.input_jam_tayang.text()
        seats = self.input_seats.text()

        # Remove the existing item from the list widget
        row = self.film_list.row(self.selected_item)
        self.film_list.takeItem(row)

        # Add a new item with the updated film data
        film_data = f'Judul : {judul}, Genre : {genre}, Jam Tayang : {jam_tayang}, Seats : {seats}'
        item = QListWidgetItem(film_data)
        self.film_list.insertItem(row, item)
        self.film_list.sortItems()

        # Update film data in the database
        try:
            with self.db_connection.cursor() as cursor:
                # SQL query to update data in the 'film' table (adjust the table name if needed)
                sql_update_film = "UPDATE film SET judul=%s, genre=%s, jam_tayang=%s, seats=%s WHERE judul=%s"
                film_values = (judul, genre, jam_tayang, seats, self.selected_item.text().split(',')[0].split(': ')[1])
                cursor.execute(sql_update_film, film_values)

            self.db_connection.commit()
            QMessageBox.information(self, 'Success', 'Film data updated successfully.')

        except pymysql.Error as e:
            self.show_database_error(e)

        self.accept()

    def show_database_error(self, error):
        QMessageBox.warning(self, 'Database Error', f'Database error: {error}')

class AdminInterface(QMainWindow):
    def __init__(self, db_connection=None):
        super(AdminInterface, self).__init__()

        self.setWindowTitle('Admin Interface')
        self.setGeometry(300, 300, 400, 200)

        menubar = self.menuBar()
        film_menu = menubar.addMenu('Film')

        input_film_action = QAction('Input Film', self)
        input_film_action.triggered.connect(self.input_film)
        film_menu.addAction(input_film_action)

        self.film_list = QListWidget(self)

        layout = QVBoxLayout()
        layout.addWidget(self.film_list)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        button_edit_film = QPushButton('Edit Film', self)
        button_edit_film.clicked.connect(self.on_edit_film_click)
        layout.addWidget(button_edit_film)

        button_keluar = QPushButton('Keluar', self)
        button_keluar.clicked.connect(self.on_keluar_click)
        layout.addWidget(button_keluar)

        button_hapus_film = QPushButton('Hapus Film', self)
        button_hapus_film.clicked.connect(self.on_hapus_film_click)
        layout.addWidget(button_hapus_film)

        self.db_connection = db_connection
        self.load_data_from_database()

    def load_data_from_database(self):
        try:
            with self.db_connection.cursor() as cursor:
                sql = "SELECT * FROM film"
                cursor.execute(sql)
                films = cursor.fetchall()

                for film in films:
                    item_text = f"Judul: {film['judul']}, Genre: {film['genre']}, Jam Tayang: {film['jam_tayang']}, Seat: {film['seats']}"
                    item = QListWidgetItem(item_text)
                    self.film_list.addItem(item)

        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Failed to load film data from database: {str(e)}')

    def on_edit_film_click(self):
        selected_item = self.film_list.currentItem()
        if selected_item:
            edit_dialog = EditFilmDialog(self.film_list, selected_item, self.db_connection)
            edit_dialog.exec_()

    def on_keluar_click(self):
        # Implementasi fungsi keluar ke layar sebelumnya di sini
        # Misalnya, bisa menggunakan self.close() atau self.hide()
        self.close()  # Ini akan menutup jendela AdminInterfac

    def input_film(self):
        film_input_dialog = FilmInputDialog(self.film_list, self.db_connection, self)
        film_input_dialog.exec_()
        # Save film data to file after input
       
    def on_hapus_film_click(self):
        selected_item = self.film_list.currentItem()
        if selected_item:
            judul_film = selected_item.text().split(',')[0].split(': ')[1]
            self.hapus_film_dari_database(judul_film)
            self.film_list.takeItem(self.film_list.row(selected_item))

    def hapus_film_dari_database(self, judul_film):
        try:
            with self.db_connection.cursor() as cursor:
                sql = "DELETE FROM film WHERE judul = %s"
                cursor.execute(sql, (judul_film,))
                self.db_connection.commit()
                QMessageBox.information(self, 'Hapus Film', 'Film berhasil dihapus dari database.')
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Gagal menghapus film dari database: {str(e)}')

    def show_search_film_dialog(self):
        search_film_dialog = SearchFilmDialog(self.film_list, self)
        search_film_dialog.exec_()

class SearchFilmDialog(QDialog):
    def __init__(self, film_list, db_connection=None, parent=None):
        super(SearchFilmDialog, self).__init__(parent)
        self.film_list = film_list
        self.db_connection = db_connection

        self.setWindowTitle('Cari Film')
        self.setGeometry(200, 200, 300, 150)

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        self.film_list_widget = QListWidget(self)
        self.film_list_widget.itemClicked.connect(self.show_selected_film)
        layout.addWidget(self.film_list_widget)

        self.search_bar = QLineEdit(self)
        layout.addWidget(self.search_bar)

        button_search = QPushButton('Cari', self)
        button_search.clicked.connect(self.load_film_from_database)
        layout.addWidget(button_search)

        self.load_film_from_database()
        self.setLayout(layout)

    def load_film_from_database(self):
        self.film_list_widget.clear()
        title = self.search_bar.text().strip()

        try:
            with self.db_connection.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = "SELECT * FROM film WHERE LOWER(judul) LIKE LOWER(%s)"
                cursor.execute(sql, ('%' + title + '%',))
                films = cursor.fetchall()

                for film in films:
                    item_text = f"Judul:{film['judul']}"
                    item = QListWidgetItem(item_text)
                    self.film_list_widget.addItem(item)

        except Exception as e:
            print(f"Exception in load_film_from_database: {e}")
            self.show_database_error(e)


    def search_in_database(self, title):
        try:
            with self.db_connection.cursor() as cursor:
                sql = "SELECT * FROM film WHERE judul LIKE %s"
                cursor.execute(sql, ('%' + title + '%',))
                result = cursor.fetchone()

                print("Query executed:", sql)
                print("Query parameters:", (title,))
                print("Result from database:", result)

                return result

        except pymysql.Error as e:
            self.show_database_error(e)
            return None

    def show_selected_film(self, item):
        try:
            split_result = item.text().split(":")
            if len(split_result) >= 2:
                title = split_result[1].strip()
                film_data = self.search_in_database(title)

                if film_data:
                    result_window = BookingSeatDialog(item, film_data, self.db_connection)
                    result_window.exec_()
                else:
                    QMessageBox.warning(self, 'Film Tidak Ditemukan', 'Maaf, film tidak ditemukan. Silakan coba lagi.')
            else:
                QMessageBox.warning(self, 'Error', 'Format item tidak valid. Silakan pilih item film yang valid.')
        except IndexError:
            QMessageBox.warning(self, 'Error', 'Format item tidak valid. Silakan pilih item film yang valid.')

class BookingSeatDialog(QDialog):
    def __init__(self, selected_item, film_data, db_connection):
        super().__init__()
        self.selected_item = selected_item
        self.film_data = film_data
        self.db_connection = db_connection
        self.selected_seats = set()

        self.setWindowTitle('Booking Kursi')
        self.setGeometry(200, 200, 400, 300)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        central_widget = QWidget(self)
        layout.addWidget(central_widget)  # Add central_widget to the layout

        vbox = QVBoxLayout()  # Use QVBoxLayout for the central widget

        # Use a loop to create seat buttons
        times = ["09:00 AM", "10:00 AM", "12:00 PM", "03:00 PM"]
        for time in times:
            seat_button = QPushButton(time)
            seat_button.clicked.connect(self.show_seat_selection)
            vbox.addWidget(seat_button)

        central_widget.setLayout(vbox)  # Set the layout for central_widget

        self.setLayout(layout)
        self.setWindowTitle('Hasil Pencarian')

    def show_seat_selection(self):
        seat_selection_dialog = QDialog(self)
        seat_selection_dialog.setWindowTitle("Pilih Kursi")

        layout = QVBoxLayout()

        grid_layout = QGridLayout()

        for row in range(5):
            for col in range(8):
                seat_button = QPushButton(f"Seat {row * 8 + col + 1}")

                # Check if the seat is already booked and update the button color accordingly
                if seat_button.text() in self.selected_seats:
                    seat_button.setStyleSheet("background-color: red;")
                    seat_button.setEnabled(False)  # Disable the button if the seat is already booked
                else:
                    seat_button.setStyleSheet("background-color: green;")
                    seat_button.setEnabled(True)  # Enable the button if the seat is available

                seat_button.clicked.connect(self.toggle_seat)

                # Create a placeholder widget to hold the button in the grid
                placeholder_widget = QWidget()
                placeholder_widget.setSizePolicy(seat_button.sizePolicy())
                placeholder_widget.setObjectName(seat_button.objectName())
                placeholder_layout = QVBoxLayout(placeholder_widget)
                placeholder_layout.addWidget(seat_button)

                grid_layout.addWidget(placeholder_widget, row, col)

        layout.addLayout(grid_layout)

        confirm_button = QPushButton("Next")
        confirm_button.clicked.connect(seat_selection_dialog.accept)
        layout.addWidget(confirm_button)

        seat_selection_dialog.setLayout(layout)

        result = seat_selection_dialog.exec_()
        if result == QDialog.Accepted:
            self.show_price_page()

    def toggle_seat(self):
        button = self.sender()
        current_color = button.palette().button().color().name()

        if current_color == "red":
            if len(self.selected_seats) < int(self.film_data['seats']):
                # Button is green and available, book the seat
                button.setStyleSheet("background-color: green;")  # Change to red to indicate selected
                self.selected_seats.add(button.text())
            else:
                QMessageBox.warning(self, 'Warning', 'All seats are already booked.', QMessageBox.Ok)
        else:
            # Button is red, unbook the seat
            button.setStyleSheet("background-color: red;")
            if button.text() in self.selected_seats:
                self.selected_seats.remove(button.text())

    def show_price_page(self):
        result_dialog = ResultDialog(self.film_data, self.selected_seats, self.db_connection)
        result = result_dialog.exec_()

        if result == QDialog.Accepted:
            # Perform additional actions if needed after the result dialog is accepted
            self.show_seat_selection()  # Call the show_seat_selection method again to go back to the seat selection

class ResultDialog(QDialog):
    def __init__(self, film_data, selected_seats, db_connection):
        super().__init__()
        self.db_connection = db_connection
        self.film_data = film_data
        self.selected_seats = set()        
        self.selected_seats = selected_seats

        self.setWindowTitle('Struct Pembayaran')
        self.setGeometry(200, 200, 300, 150)

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        title_label = QLabel(f"Judul: {self.film_data['judul']}")
        layout.addWidget(title_label)

        time_label = QLabel(f"Jam Tayang: {self.film_data['jam_tayang']}")
        layout.addWidget(time_label)

        seats_label = QLabel()
        layout.addWidget(seats_label)
        self.update_seats_label(seats_label)

        price_label = QLabel("Harga: Rp 50,000")  # Adjust as needed
        layout.addWidget(price_label)

        ok_button = QPushButton("Oke")
        ok_button.clicked.connect(self.purchase_ticket)  # Connect to self.accept
        layout.addWidget(ok_button)

        self.setLayout(layout)

    def update_seats_label(self, label):
        available_seats = int(self.film_data['seats'])
        if available_seats > 0:
            label.setText(f"Seats: {available_seats} (Available)")
            label.setStyleSheet("color: green; font-weight: bold;")
        else:
            label.setText("Seats: Sold Out")
            label.setStyleSheet("color: red; font-weight: bold;")

    def purchase_ticket(self):
        try:
            with self.db_connection.cursor() as cursor:
                # Check available seats
                sql_check_seats = "SELECT seats FROM film WHERE judul = %s"
                cursor.execute(sql_check_seats, (self.film_data['judul'],))
                result = cursor.fetchone()

                if result and int(result['seats']) > 0:
                    # Update available seats
                    sql_update_seats = "UPDATE film SET seats = seats - 1 WHERE judul = %s"
                    cursor.execute(sql_update_seats, (self.film_data['judul'],))

                    # Insert purchase data into the 'purchases' table (example table name)
                    sql_insert_purchase = """
                        INSERT INTO purchases (judul, genre, jam_tayang, purchased_at)
                        VALUES (%s, %s, %s, %s)
                    """
                    purchase_data = (
                        self.film_data['judul'],
                        self.film_data['genre'],
                        self.film_data['jam_tayang'],
                        datetime.now(),
                    )
                    cursor.execute(sql_insert_purchase, purchase_data)

                    self.db_connection.commit()
                    QMessageBox.information(self, 'Success', f'Ticket purchased for {self.film_data["judul"]}.')
                else:
                    QMessageBox.warning(self, 'Warning', 'No available seats for the selected time.')

        except pymysql.Error as e:
            self.show_database_error(e)

     
    def show_database_error(self, error):
        QMessageBox.warning(self, 'Database Error', f'Database error: {error}')

class PemesananTiketBioskop(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Pemesanan Tiket Bioskop')
        self.setGeometry(100, 100, 400, 200)

        self.customer_name = ''
        self.customer_email = ''
        self.film_list = QListWidget(self)
        
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        label_name = QLabel("Name:")
        self.input_name = QLineEdit()
        layout.addWidget(label_name)
        layout.addWidget(self.input_name)

        label_email = QLabel("Email:")
        self.input_email = QLineEdit()
        layout.addWidget(label_email)
        layout.addWidget(self.input_email)

        login_button = QPushButton("Masuk")
        login_button.clicked.connect(self.on_masuk_click)
        layout.addWidget(login_button)
        
        button_keluar = QPushButton('Keluar', self)
        button_keluar.clicked.connect(self.close)
        layout.addWidget(button_keluar)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        menubar = self.menuBar()
        admin_menu = menubar.addMenu('Admin')

        admin_login_action = QAction('Admin Login', self)
        admin_login_action.triggered.connect(self.show_admin_login_dialog)
        admin_menu.addAction(admin_login_action)

        self.admin_interface = None  

        self.db_connection = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            database='tiket_bioskop',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )  
    
    def show_admin_login_dialog(self):
        admin_login_dialog = AdminLoginDialog(self)
        if admin_login_dialog.exec_() == QDialog.Accepted:
            self.admin_interface = AdminInterface(self.db_connection)
            self.admin_interface.show()

    def on_masuk_click(self):
        self.customer_name = self.input_name.text()
        self.customer_email = self.input_email.text()

        if self.customer_name and self.customer_email:
            message = f"Selamat datang, {self.customer_name}!\n" \
                      f"Email: {self.customer_email}"
            QMessageBox.information(self, 'Informasi', message)
            self.show_search_film_dialog()
        else:
            QMessageBox.warning(self, 'Peringatan', 'Mohon isi nama dan email terlebih dahulu.')

    def show_search_film_dialog(self):
        search_film_dialog = SearchFilmDialog(self.film_list, self.db_connection, self)
        search_film_dialog.exec_()

    def closeEvent(self, event):
        if hasattr(self, 'db_connection') and self.db_connection:
            self.db_connection.close()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PemesananTiketBioskop()
    window.show()
    sys.exit(app.exec_())