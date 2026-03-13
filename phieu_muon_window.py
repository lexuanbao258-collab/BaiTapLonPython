from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton,
    QMessageBox, QLineEdit, QComboBox, QDateEdit, QTableWidget,
    QTableWidgetItem, QSpinBox, QHeaderView, QSplitter
)
from PyQt5.QtCore import QDate, Qt
from db import tao_ket_noi

from PyQt5.QtWidgets import QFileDialog
from pdf_utils import xuat_pdf_phieu_muon

class PhieuMuonWindow(QWidget):
    def __init__(self, nguoi_dung_id):
        super().__init__()
        self.nguoi_dung_id = nguoi_dung_id
        self.setWindowTitle("Phiếu mượn")
        self.setGeometry(200, 100, 1200, 700)
        self.ds_sach = []
        self.init_ui()
        self.tai_combo_nguoi_muon()
        self.tai_danh_sach_sach()
        self.tai_danh_sach_phieu_muon()

    def init_ui(self):
        layout = QVBoxLayout()
        lbl = QLabel("LẬP PHIẾU MƯỢN")
        lbl.setStyleSheet("font-size: 18px; font-weight: bold;")

        form_layout = QHBoxLayout()

        self.txt_ma_phieu_muon = QLineEdit()
        self.txt_ma_phieu_muon.setPlaceholderText("Mã phiếu mượn")

        self.cbo_nguoi_muon = QComboBox()
        self.date_ngay_muon = QDateEdit()
        self.date_ngay_muon.setCalendarPopup(True)
        self.date_ngay_muon.setDate(QDate.currentDate())

        self.date_ngay_hen_tra = QDateEdit()
        self.date_ngay_hen_tra.setCalendarPopup(True)
        self.date_ngay_hen_tra.setDate(QDate.currentDate().addDays(7))

        form_layout.addWidget(QLabel("Mã phiếu"))
        form_layout.addWidget(self.txt_ma_phieu_muon)
        form_layout.addWidget(QLabel("Người mượn"))
        form_layout.addWidget(self.cbo_nguoi_muon)
        form_layout.addWidget(QLabel("Ngày mượn"))
        form_layout.addWidget(self.date_ngay_muon)
        form_layout.addWidget(QLabel("Ngày hẹn trả"))
        form_layout.addWidget(self.date_ngay_hen_tra)

        middle_layout = QHBoxLayout()
        self.cbo_sach = QComboBox()
        self.spn_so_luong = QSpinBox()
        self.spn_so_luong.setRange(1, 1000)
        self.btn_them_sach = QPushButton("Thêm sách vào phiếu")
        middle_layout.addWidget(QLabel("Chọn sách"))
        middle_layout.addWidget(self.cbo_sach)
        middle_layout.addWidget(QLabel("Số lượng"))
        middle_layout.addWidget(self.spn_so_luong)
        middle_layout.addWidget(self.btn_them_sach)

        self.table_chi_tiet = QTableWidget()
        self.table_chi_tiet.setColumnCount(5)
        self.table_chi_tiet.setHorizontalHeaderLabels([
            "Sách ID", "Mã sách", "Tên sách", "Số lượng", "Số lượng còn"
        ])
        self.table_chi_tiet.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_chi_tiet.setColumnHidden(0, True)
        self.table_chi_tiet.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_chi_tiet.setEditTriggers(QTableWidget.NoEditTriggers)

        btn_ct_layout = QHBoxLayout()
        self.btn_xoa_dong = QPushButton("Xóa dòng đã chọn")
        self.btn_xuat_pdf = QPushButton("Xuất PDF")
        self.btn_luu = QPushButton("Lưu phiếu mượn")

        btn_ct_layout.addWidget(self.btn_xoa_dong)
        btn_ct_layout.addWidget(self.btn_xuat_pdf)
        btn_ct_layout.addStretch()
        btn_ct_layout.addWidget(self.btn_luu)


        self.table_ds_phieu = QTableWidget()
        self.table_ds_phieu.setColumnCount(6)
        self.table_ds_phieu.setHorizontalHeaderLabels([
            "ID", "Mã phiếu", "Người mượn", "Ngày mượn", "Ngày hẹn trả", "Trạng thái"
        ])
        self.table_ds_phieu.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_ds_phieu.setColumnHidden(0, True)
        self.table_ds_phieu.setEditTriggers(QTableWidget.NoEditTriggers)

        layout.addWidget(lbl)
        layout.addLayout(form_layout)
        layout.addLayout(middle_layout)
        layout.addWidget(QLabel("Chi tiết sách trong phiếu"))
        layout.addWidget(self.table_chi_tiet)
        layout.addLayout(btn_ct_layout)
        layout.addWidget(QLabel("Danh sách phiếu mượn"))
        layout.addWidget(self.table_ds_phieu)

        self.setLayout(layout)

        self.btn_them_sach.clicked.connect(self.them_sach_vao_phieu)
        self.btn_xoa_dong.clicked.connect(self.xoa_dong_chi_tiet)
        self.btn_luu.clicked.connect(self.luu_phieu_muon)

        self.btn_xuat_pdf.clicked.connect(self.xuat_pdf)


    def tai_combo_nguoi_muon(self):
        self.cbo_nguoi_muon.clear()
        conn = tao_ket_noi()
        cur = conn.cursor()
        cur.execute("SELECT id, ma_nguoi_muon, ho_ten FROM nguoi_muon ORDER BY ho_ten")
        for item in cur.fetchall():
            self.cbo_nguoi_muon.addItem(f"{item[1]} - {item[2]}", item[0])
        cur.close()
        conn.close()

    def tai_danh_sach_sach(self):
        self.cbo_sach.clear()
        self.ds_sach = []
        conn = tao_ket_noi()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, ma_sach, ten_sach, so_luong_con
            FROM sach
            WHERE dang_hoat_dong = TRUE
            ORDER BY ten_sach
        """)
        self.ds_sach = cur.fetchall()
        for item in self.ds_sach:
            self.cbo_sach.addItem(f"{item[1]} - {item[2]} (còn: {item[3]})", item[0])
        cur.close()
        conn.close()

    def tai_danh_sach_phieu_muon(self):
        try:
            conn = tao_ket_noi()
            cur = conn.cursor()
            cur.execute("""
                SELECT pm.id, pm.ma_phieu_muon, nm.ho_ten, pm.ngay_muon, pm.ngay_hen_tra, pm.trang_thai
                FROM phieu_muon pm
                JOIN nguoi_muon nm ON pm.nguoi_muon_id = nm.id
                ORDER BY pm.id DESC
            """)
            rows = cur.fetchall()
            self.table_ds_phieu.setRowCount(len(rows))
            for r, row in enumerate(rows):
                for c, value in enumerate(row):
                    self.table_ds_phieu.setItem(r, c, QTableWidgetItem("" if value is None else str(value)))
            cur.close()
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))

    def them_sach_vao_phieu(self):
        if self.cbo_sach.currentIndex() < 0:
            return

        sach_id = self.cbo_sach.currentData()
        so_luong = self.spn_so_luong.value()

        sach_chon = None
        for item in self.ds_sach:
            if item[0] == sach_id:
                sach_chon = item
                break

        if not sach_chon:
            return

        if so_luong > sach_chon[3]:
            QMessageBox.warning(self, "Thông báo", "Số lượng mượn vượt quá số lượng còn.")
            return

        for row in range(self.table_chi_tiet.rowCount()):
            if int(self.table_chi_tiet.item(row, 0).text()) == sach_id:
                QMessageBox.warning(self, "Thông báo", "Sách này đã có trong phiếu.")
                return

        row = self.table_chi_tiet.rowCount()
        self.table_chi_tiet.insertRow(row)
        self.table_chi_tiet.setItem(row, 0, QTableWidgetItem(str(sach_chon[0])))
        self.table_chi_tiet.setItem(row, 1, QTableWidgetItem(str(sach_chon[1])))
        self.table_chi_tiet.setItem(row, 2, QTableWidgetItem(str(sach_chon[2])))
        self.table_chi_tiet.setItem(row, 3, QTableWidgetItem(str(so_luong)))
        self.table_chi_tiet.setItem(row, 4, QTableWidgetItem(str(sach_chon[3])))

    def xoa_dong_chi_tiet(self):
        row = self.table_chi_tiet.currentRow()
        if row >= 0:
            self.table_chi_tiet.removeRow(row)

    def luu_phieu_muon(self):
        ma_phieu_muon = self.txt_ma_phieu_muon.text().strip()
        nguoi_muon_id = self.cbo_nguoi_muon.currentData()

        if not ma_phieu_muon:
            QMessageBox.warning(self, "Thông báo", "Vui lòng nhập mã phiếu mượn.")
            return

        if self.table_chi_tiet.rowCount() == 0:
            QMessageBox.warning(self, "Thông báo", "Vui lòng thêm ít nhất một cuốn sách.")
            return

        try:
            conn = tao_ket_noi()
            cur = conn.cursor()

            cur.execute("""
                INSERT INTO phieu_muon (
                    ma_phieu_muon, nguoi_muon_id, nguoi_lap_id,
                    ngay_muon, ngay_hen_tra, trang_thai
                )
                VALUES (%s, %s, %s, %s, %s, 'dang_muon')
                RETURNING id
            """, (
                ma_phieu_muon,
                nguoi_muon_id,
                self.nguoi_dung_id,
                self.date_ngay_muon.date().toString("yyyy-MM-dd"),
                self.date_ngay_hen_tra.date().toString("yyyy-MM-dd")
            ))
            phieu_muon_id = cur.fetchone()[0]

            for row in range(self.table_chi_tiet.rowCount()):
                sach_id = int(self.table_chi_tiet.item(row, 0).text())
                so_luong = int(self.table_chi_tiet.item(row, 3).text())

                cur.execute("SELECT so_luong_con FROM sach WHERE id = %s", (sach_id,))
                so_luong_con = cur.fetchone()[0]

                if so_luong > so_luong_con:
                    raise Exception(f"Sách ID {sach_id} không đủ số lượng.")

                cur.execute("""
                    INSERT INTO chi_tiet_phieu_muon (phieu_muon_id, sach_id, so_luong)
                    VALUES (%s, %s, %s)
                """, (phieu_muon_id, sach_id, so_luong))

                cur.execute("""
                    UPDATE sach
                    SET so_luong_con = so_luong_con - %s
                    WHERE id = %s
                """, (so_luong, sach_id))

            conn.commit()
            cur.close()
            conn.close()

            self.table_chi_tiet.setRowCount(0)
            self.txt_ma_phieu_muon.clear()
            self.tai_danh_sach_sach()
            self.tai_danh_sach_phieu_muon()

            QMessageBox.information(self, "Thành công", "Lưu phiếu mượn thành công.")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))

    def xuat_pdf(self):
        row = self.table_ds_phieu.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Thông báo", "Vui lòng chọn phiếu mượn cần xuất PDF.")
            return

        phieu_muon_id = int(self.table_ds_phieu.item(row, 0).text())

        duong_dan_file, _ = QFileDialog.getSaveFileName(
            self,
            "Lưu phiếu mượn PDF",
            "phieu_muon.pdf",
            "PDF Files (*.pdf)"
        )

        if not duong_dan_file:
            return

        try:
            conn = tao_ket_noi()
            cur = conn.cursor()

            cur.execute("""
                        SELECT pm.ma_phieu_muon, nm.ho_ten, pm.ngay_muon, pm.ngay_hen_tra, pm.trang_thai
                        FROM phieu_muon pm
                                 JOIN nguoi_muon nm ON pm.nguoi_muon_id = nm.id
                        WHERE pm.id = %s
                        """, (phieu_muon_id,))
            row_info = cur.fetchone()

            if not row_info:
                raise Exception("Không tìm thấy phiếu mượn.")

            thong_tin = {
                "ma_phieu_muon": row_info[0],
                "ho_ten": row_info[1],
                "ngay_muon": str(row_info[2]),
                "ngay_hen_tra": str(row_info[3]),
                "trang_thai": row_info[4]
            }

            cur.execute("""
                        SELECT s.ma_sach, s.ten_sach, ctm.so_luong
                        FROM chi_tiet_phieu_muon ctm
                                 JOIN sach s ON ctm.sach_id = s.id
                        WHERE ctm.phieu_muon_id = %s
                        ORDER BY ctm.id
                        """, (phieu_muon_id,))
            chi_tiet = cur.fetchall()

            cur.close()
            conn.close()

            xuat_pdf_phieu_muon(duong_dan_file, thong_tin, chi_tiet)
            QMessageBox.information(self, "Thành công", "Xuất PDF phiếu mượn thành công.")

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))