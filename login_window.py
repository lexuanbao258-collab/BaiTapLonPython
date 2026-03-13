from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QMessageBox, QFrame
)
from PyQt5.QtCore import Qt
from db import tao_ket_noi
from main_window import MainWindow

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.main_window = None
        self.setWindowTitle("Đăng nhập hệ thống")
        self.setFixedSize(500, 360)
        self.init_ui()
        self.ap_dung_style()

    def init_ui(self):
        outer_layout = QVBoxLayout()
        outer_layout.setContentsMargins(28, 28, 28, 28)

        card = QFrame()
        card.setObjectName("loginCard")

        layout = QVBoxLayout()
        layout.setContentsMargins(36, 34, 36, 34)
        layout.setSpacing(0)

        self.lbl_tieu_de = QLabel("ĐĂNG NHẬP HỆ THỐNG")
        self.lbl_tieu_de.setObjectName("titleLabel")
        self.lbl_tieu_de.setAlignment(Qt.AlignCenter)

        self.lbl_sub = QLabel("Hệ thống quản lý thư viện")
        self.lbl_sub.setObjectName("subLabel")
        self.lbl_sub.setAlignment(Qt.AlignCenter)

        self.txt_ten_dang_nhap = QLineEdit()
        self.txt_ten_dang_nhap.setPlaceholderText("Tên đăng nhập")
        self.txt_ten_dang_nhap.setFixedHeight(46)

        self.txt_mat_khau = QLineEdit()
        self.txt_mat_khau.setPlaceholderText("Mật khẩu")
        self.txt_mat_khau.setEchoMode(QLineEdit.Password)
        self.txt_mat_khau.setFixedHeight(46)

        self.btn_dang_nhap = QPushButton("Đăng nhập")
        self.btn_dang_nhap.setFixedHeight(48)
        self.btn_dang_nhap.clicked.connect(self.dang_nhap)

        layout.addSpacing(6)
        layout.addWidget(self.lbl_tieu_de)
        layout.addSpacing(10)
        layout.addWidget(self.lbl_sub)
        layout.addSpacing(30)
        layout.addWidget(self.txt_ten_dang_nhap)
        layout.addSpacing(14)
        layout.addWidget(self.txt_mat_khau)
        layout.addSpacing(22)
        layout.addWidget(self.btn_dang_nhap)

        card.setLayout(layout)
        outer_layout.addWidget(card)
        self.setLayout(outer_layout)

    def dang_nhap(self):
        ten_dang_nhap = self.txt_ten_dang_nhap.text().strip()
        mat_khau = self.txt_mat_khau.text().strip()

        if not ten_dang_nhap or not mat_khau:
            QMessageBox.warning(self, "Thông báo", "Vui lòng nhập đầy đủ thông tin.")
            return

        try:
            conn = tao_ket_noi()
            cur = conn.cursor()

            cur.execute("""
                SELECT id, ho_ten, vai_tro
                FROM nguoi_dung
                WHERE ten_dang_nhap = %s
                  AND mat_khau_ma_hoa = %s
                  AND dang_hoat_dong = TRUE
            """, (ten_dang_nhap, mat_khau))

            nguoi_dung = cur.fetchone()

            cur.close()
            conn.close()

            if nguoi_dung:
                nguoi_dung_id = nguoi_dung[0]
                ho_ten = nguoi_dung[1]
                vai_tro = nguoi_dung[2]

                self.main_window = MainWindow(nguoi_dung_id, ho_ten, vai_tro)
                self.main_window.showMaximized()
                self.close()
            else:
                QMessageBox.critical(self, "Lỗi", "Sai tên đăng nhập hoặc mật khẩu.")

        except Exception as e:
            QMessageBox.critical(self, "Lỗi kết nối", str(e))

    def ap_dung_style(self):
        self.setStyleSheet("""
            QWidget {
                background: #eef4ff;
                font-family: "Segoe UI";
            }

            #loginCard {
                background: white;
                border: 1px solid #dbeafe;
                border-radius: 20px;
            }

            #titleLabel {
                color: #0f172a;
                font-size: 28px;
                font-weight: 700;
                background: transparent;
            }

            #subLabel {
                color: #64748b;
                font-size: 14px;
                background: transparent;
            }

            QLineEdit {
                background: white;
                border: 1px solid #cbd5e1;
                border-radius: 12px;
                padding-left: 14px;
                padding-right: 14px;
                font-size: 14px;
                color: #0f172a;
            }

            QLineEdit:focus {
                border: 1px solid #2563eb;
            }

            QPushButton {
                background: #2563eb;
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 15px;
                font-weight: 600;
            }

            QPushButton:hover {
                background: #1d4ed8;
            }

            QPushButton:pressed {
                background: #1e40af;
            }
        """)