from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QGridLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QPushButton, QMessageBox
)
from db import tao_ket_noi


class ThongKeWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Thống kê")
        self.setGeometry(260, 140, 1000, 600)
        self.init_ui()
        self.tai_du_lieu()

    def init_ui(self):
        layout = QVBoxLayout()

        lbl = QLabel("THỐNG KÊ HỆ THỐNG")
        lbl.setStyleSheet("font-size: 18px; font-weight: bold;")

        self.lbl_tong_sach = QLabel("Tổng số đầu sách: 0")
        self.lbl_tong_sach_dang_muon = QLabel("Tổng số sách đang mượn: 0")
        self.lbl_so_phieu_qua_han = QLabel("Số phiếu quá hạn: 0")
        self.lbl_tong_tien_phat = QLabel("Tổng tiền phạt chưa thanh toán: 0")

        self.btn_tai_lai = QPushButton("Tải lại")
        self.btn_tai_lai.clicked.connect(self.tai_du_lieu)

        self.table_top_sach = QTableWidget()
        self.table_top_sach.setColumnCount(2)
        self.table_top_sach.setHorizontalHeaderLabels(["Tên sách", "Tổng lượt mượn"])
        self.table_top_sach.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(lbl)
        layout.addWidget(self.btn_tai_lai)
        layout.addWidget(self.lbl_tong_sach)
        layout.addWidget(self.lbl_tong_sach_dang_muon)
        layout.addWidget(self.lbl_so_phieu_qua_han)
        layout.addWidget(self.lbl_tong_tien_phat)
        layout.addWidget(QLabel("Top sách được mượn nhiều"))
        layout.addWidget(self.table_top_sach)

        self.setLayout(layout)

    def tai_du_lieu(self):
        try:
            conn = tao_ket_noi()
            cur = conn.cursor()

            cur.execute("SELECT COUNT(*) FROM sach")
            tong_sach = cur.fetchone()[0]

            cur.execute("""
                SELECT COALESCE(SUM(ctm.so_luong), 0)
                FROM chi_tiet_phieu_muon ctm
                JOIN phieu_muon pm ON ctm.phieu_muon_id = pm.id
                WHERE pm.trang_thai = 'dang_muon'
            """)
            tong_sach_dang_muon = cur.fetchone()[0]

            cur.execute("""
                SELECT COUNT(*)
                FROM phieu_muon
                WHERE trang_thai = 'dang_muon'
                  AND ngay_hen_tra < CURRENT_DATE
            """)
            so_phieu_qua_han = cur.fetchone()[0]

            cur.execute("""
                SELECT COALESCE(SUM(tong_tien), 0)
                FROM phieu_phat
                WHERE trang_thai_thanh_toan = 'chua_thanh_toan'
            """)
            tong_tien_phat = cur.fetchone()[0]

            cur.execute("""
                SELECT s.ten_sach, COALESCE(SUM(ctm.so_luong), 0) AS tong_luot_muon
                FROM sach s
                LEFT JOIN chi_tiet_phieu_muon ctm ON s.id = ctm.sach_id
                GROUP BY s.id, s.ten_sach
                ORDER BY tong_luot_muon DESC, s.ten_sach
                LIMIT 10
            """)
            rows = cur.fetchall()

            self.lbl_tong_sach.setText(f"Tổng số đầu sách: {tong_sach}")
            self.lbl_tong_sach_dang_muon.setText(f"Tổng số sách đang mượn: {tong_sach_dang_muon}")
            self.lbl_so_phieu_qua_han.setText(f"Số phiếu quá hạn: {so_phieu_qua_han}")
            self.lbl_tong_tien_phat.setText(f"Tổng tiền phạt chưa thanh toán: {tong_tien_phat}")

            self.table_top_sach.setRowCount(len(rows))
            for r, row in enumerate(rows):
                self.table_top_sach.setItem(r, 0, QTableWidgetItem(str(row[0])))
                self.table_top_sach.setItem(r, 1, QTableWidgetItem(str(row[1])))

            cur.close()
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))