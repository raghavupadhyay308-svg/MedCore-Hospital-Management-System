"""
main.py
MedCore Hospital Management System \u2014 application entry point.

Run with:  python3 main.py
"""
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

from db import Database
from styles import APP_QSS
from ui.login import LoginWindow
from ui.admin_dashboard import AdminDashboard
from ui.doctor_dashboard import DoctorDashboard
from ui.patient_portal import PatientPortal


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MedCore \u2014 Hospital Management System")
        self.resize(1180, 760)
        self.db = Database()
        self._show_login()

    def _show_login(self):
        login = LoginWindow(self.db)
        login.login_success.connect(self._on_login_success)
        self.setCentralWidget(login)
        self.setStyleSheet("")  # login screen draws its own gradient background
        self.resize(1180, 760)

    def _on_login_success(self, role, row):
        self.setStyleSheet(APP_QSS)
        if role == "admin":
            dash = AdminDashboard(self.db, on_logout=self._show_login)
        elif role == "doctor":
            dash = DoctorDashboard(self.db, row, on_logout=self._show_login)
        elif role == "patient":
            dash = PatientPortal(self.db, row, on_logout=self._show_login)
        else:
            return
        self.setCentralWidget(dash)
        self.showMaximized()

    def closeEvent(self, event):
        try:
            self.db.close()
        except Exception:
            pass
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("MedCore HMS")
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
