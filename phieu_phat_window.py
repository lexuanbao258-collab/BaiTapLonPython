from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton,
    QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView
)
from db import tao_ket_noi

from PyQt5.QtWidgets import QFileDialog
from pdf_utils import xuat_pdf_phieu_phat

class PhieuPhatWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Phiếu phạt")
        self.setGeometry(220, 120, 1150, 650)
        self.init_ui()
        self.tai_danh_sach_phieu_phat()

    def init_ui(self):
        layout = QVBoxLayout()

        lbl = QLabel("DANH SÁCH PHIẾU PHẠT")
        lbl.setStyleSheet("font-size: 18px; font-weight: bold;")

        btn_layout = QHBoxLayout()
        self.btn_tai_lai = QPushButton("Tải lại")
        self.btn_xem_chi_tiet = QPushButton("Xem chi tiết")
        self.btn_xuat_pdf = QPushButton("Xuất PDF")
        self.btn_thanh_toan = QPushButton("Đánh dấu đã thanh toán")

        btn_layout.addWidget(self.btn_tai_lai)
        btn_layout.addWidget(self.btn_xem_chi_tiet)
        btn_layout.addWidget(self.btn_xuat_pdf)
        btn_layout.addWidget(self.btn_thanh_toan)

        self.btn_xuat_pdf.clicked.connect(self.xuat_pdf)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Mã phiếu phạt", "Người mượn", "Mã phiếu mượn",
            "Tổng tiền", "Trạng thái thanh toán", "Ngày tạo"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setColumnHidden(0, True)

        self.table_ct = QTableWidget()
        self.table_ct.setColumnCount(6)
        self.table_ct.setHorizontalHeaderLabels([
            "Sách ID", "Lý do", "Số lượng", "Đơn giá phạt", "Thành tiền", "Ghi chú"
        ])
        self.table_ct.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(lbl)
        layout.addLayout(btn_layout)
        layout.addWidget(self.table)
        layout.addWidget(QLabel("Chi tiết phiếu phạt"))
        layout.addWidget(self.table_ct)

        self.setLayout(layout)

        self.btn_tai_lai.clicked.connect(self.tai_danh_sach_phieu_phat)
        self.btn_xem_chi_tiet.clicked.connect(self.xem_chi_tiet)
        self.btn_thanh_toan.clicked.connect(self.danh_dau_da_thanh_toan)

    def lay_id_duoc_chon(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        return int(self.table.item(row, 0).text())

    def tai_danh_sach_phieu_phat(self):
        try:
            conn = tao_ket_noi()
            cur = conn.cursor()
            cur.execute("""
                SELECT pp.id, pp.ma_phieu_phat, nm.ho_ten, pm.ma_phieu_muon,
                       pp.tong_tien, pp.trang_thai_thanh_toan, pp.ngay_tao
                FROM phieu_phat pp
                JOIN nguoi_muon nm ON pp.nguoi_muon_id = nm.id
                JOIN phieu_muon pm ON pp.phieu_muon_id = pm.id
                ORDER BY pp.id DESC
            """)
            rows = cur.fetchall()
            self.table.setRowCount(len(rows))
            for r, row in enumerate(rows):
                for c, value in enumerate(row):
                    self.table.setItem(r, c, QTableWidgetItem("" if value is None else str(value)))
            cur.close()
            conn.close()
            self.table_ct.setRowCount(0)
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))

    def xem_chi_tiet(self):
        phieu_phat_id = self.lay_id_duoc_chon()
        if not phieu_phat_id:
            QMessageBox.warning(self, "Thông báo", "Vui lòng chọn phiếu phạt.")
            return

        try:
            conn = tao_ket_noi()
            cur = conn.cursor()
            cur.execute("""
                SELECT sach_id, ly_do, so_luong, don_gia_phat, thanh_tien, ghi_chu
                FROM chi_tiet_phieu_phat
                WHERE phieu_phat_id = %s
                ORDER BY id
            """, (phieu_phat_id,))
            rows = cur.fetchall()
            self.table_ct.setRowCount(len(rows))
            for r, row in enumerate(rows):
                for c, value in enumerate(row):
                    self.table_ct.setItem(r, c, QTableWidgetItem("" if value is None else str(value)))
            cur.close()
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))

    def danh_dau_da_thanh_toan(self):
        phieu_phat_id = self.lay_id_duoc_chon()
        if not phieu_phat_id:
            QMessageBox.warning(self, "Thông báo", "Vui lòng chọn phiếu phạt.")
            return

        try:
            conn = tao_ket_noi()
            cur = conn.cursor()
            cur.execute("""
                UPDATE phieu_phat
                SET trang_thai_thanh_toan = 'da_thanh_toan',
                    ngay_thanh_toan = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (phieu_phat_id,))
            conn.commit()
            cur.close()
            conn.close()
            self.tai_danh_sach_phieu_phat()
            QMessageBox.information(self, "Thành công", "Cập nhật trạng thái thanh toán thành công.")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))

    def xuat_pdf(self):
        phieu_phat_id = self.lay_id_duoc_chon()
        if not phieu_phat_id:
            QMessageBox.warning(self, "Thông báo", "Vui lòng chọn phiếu phạt cần xuất PDF.")
            return

        duong_dan_file, _ = QFileDialog.getSaveFileName(
            self,
            "Lưu phiếu phạt PDF",
            "phieu_phat.pdf",
            "PDF Files (*.pdf)"
        )

        if not duong_dan_file:
            return

        try:
            conn = tao_ket_noi()
            cur = conn.cursor()

            cur.execute("""
                        SELECT pp.ma_phieu_phat,
                               nm.ho_ten,
                               pm.ma_phieu_muon,
                               pp.tong_tien,
                               pp.trang_thai_thanh_toan
                        FROM phieu_phat pp
                                 JOIN nguoi_muon nm ON pp.nguoi_muon_id = nm.id
                                 JOIN phieu_muon pm ON pp.phieu_muon_id = pm.id
                        WHERE pp.id = %s
                        """, (phieu_phat_id,))
            row_info = cur.fetchone()

            if not row_info:
                raise Exception("Không tìm thấy phiếu phạt.")

            thong_tin = {
                "ma_phieu_phat": row_info[0],
                "ho_ten": row_info[1],
                "ma_phieu_muon": row_info[2],
                "tong_tien": int(row_info[3]),
                "trang_thai_thanh_toan": row_info[4]
            }

            cur.execute("""
                        SELECT ly_do, so_luong, don_gia_phat, thanh_tien, ghi_chu
                        FROM chi_tiet_phieu_phat
                        WHERE phieu_phat_id = %s
                        ORDER BY id
                        """, (phieu_phat_id,))
            chi_tiet = cur.fetchall()

            cur.close()
            conn.close()

            xuat_pdf_phieu_phat(duong_dan_file, thong_tin, chi_tiet)
            QMessageBox.information(self, "Thành công", "Xuất PDF phiếu phạt thành công.")

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))