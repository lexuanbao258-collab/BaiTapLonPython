from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton,
    QMessageBox, QLineEdit, QComboBox, QDateEdit, QTableWidget,
    QTableWidgetItem, QSpinBox, QHeaderView, QFileDialog
)
from PyQt5.QtCore import QDate
from db import tao_ket_noi
from pdf_utils import xuat_pdf_phieu_tra


class PhieuTraWindow(QWidget):
    def __init__(self, nguoi_dung_id):
        super().__init__()
        self.nguoi_dung_id = nguoi_dung_id
        self.setWindowTitle("Phiếu trả")
        self.setGeometry(190, 90, 1250, 720)
        self.ds_chi_tiet = []

        self.init_ui()
        self.tai_combo_phieu_muon()
        self.tai_danh_sach_phieu_tra()
        self.cap_nhat_ma_phieu_tra_moi()

    def init_ui(self):
        layout = QVBoxLayout()

        lbl = QLabel("LẬP PHIẾU TRẢ")
        lbl.setStyleSheet("font-size: 18px; font-weight: bold;")

        top_layout = QHBoxLayout()

        self.txt_ma_phieu_tra = QLineEdit()
        self.txt_ma_phieu_tra.setPlaceholderText("Mã phiếu trả")
        self.txt_ma_phieu_tra.setReadOnly(True)

        self.cbo_phieu_muon = QComboBox()
        self.cbo_phieu_muon.currentIndexChanged.connect(self.hien_chi_tiet_phieu_muon)

        self.date_ngay_tra = QDateEdit()
        self.date_ngay_tra.setCalendarPopup(True)
        self.date_ngay_tra.setDate(QDate.currentDate())

        top_layout.addWidget(QLabel("Mã phiếu trả"))
        top_layout.addWidget(self.txt_ma_phieu_tra)
        top_layout.addWidget(QLabel("Phiếu mượn"))
        top_layout.addWidget(self.cbo_phieu_muon)
        top_layout.addWidget(QLabel("Ngày trả"))
        top_layout.addWidget(self.date_ngay_tra)

        self.table_chi_tiet = QTableWidget()
        self.table_chi_tiet.setColumnCount(8)
        self.table_chi_tiet.setHorizontalHeaderLabels([
            "CTPM ID", "Sách ID", "Tên sách", "Đã mượn",
            "Số lượng trả", "Số lượng hỏng", "Số lượng mất", "Ghi chú"
        ])
        self.table_chi_tiet.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        btn_layout = QHBoxLayout()
        self.btn_xuat_pdf = QPushButton("Xuất PDF")
        self.btn_luu = QPushButton("Lưu phiếu trả")

        btn_layout.addWidget(self.btn_xuat_pdf)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_luu)

        self.btn_xuat_pdf.clicked.connect(self.xuat_pdf)
        self.btn_luu.clicked.connect(self.luu_phieu_tra)

        self.table_ds = QTableWidget()
        self.table_ds.setColumnCount(6)
        self.table_ds.setHorizontalHeaderLabels([
            "ID", "Mã phiếu trả", "Mã phiếu mượn", "Ngày trả", "Số ngày trễ", "Ghi chú"
        ])
        self.table_ds.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_ds.setColumnHidden(0, True)

        layout.addWidget(lbl)
        layout.addLayout(top_layout)
        layout.addWidget(QLabel("Chi tiết trả"))
        layout.addWidget(self.table_chi_tiet)
        layout.addLayout(btn_layout)
        layout.addWidget(QLabel("Danh sách phiếu trả"))
        layout.addWidget(self.table_ds)

        self.setLayout(layout)

    def tao_ma_phieu_tra_moi(self, conn):
        with conn.cursor() as cur:
            cur.execute("""
                SELECT COALESCE(MAX(CAST(SUBSTRING(ma_phieu_tra FROM 3) AS INTEGER)), 0)
                FROM phieu_tra
                WHERE ma_phieu_tra ~ '^PT[0-9]+$'
            """)
            so_cuoi = cur.fetchone()[0]
        return f"PT{so_cuoi + 1:03d}"

    def tao_ma_phieu_phat_moi(self, conn):
        with conn.cursor() as cur:
            cur.execute("""
                SELECT COALESCE(MAX(CAST(SUBSTRING(ma_phieu_phat FROM 3) AS INTEGER)), 0)
                FROM phieu_phat
                WHERE ma_phieu_phat ~ '^PP[0-9]+$'
            """)
            so_cuoi = cur.fetchone()[0]
        return f"PP{so_cuoi + 1:03d}"

    def cap_nhat_ma_phieu_tra_moi(self):
        conn = None
        try:
            conn = tao_ket_noi()
            ma_moi = self.tao_ma_phieu_tra_moi(conn)
            self.txt_ma_phieu_tra.setText(ma_moi)
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không tạo được mã phiếu trả mới:\n{str(e)}")
        finally:
            if conn:
                conn.close()

    def tai_combo_phieu_muon(self):
        conn = None
        try:
            self.cbo_phieu_muon.clear()

            conn = tao_ket_noi()
            cur = conn.cursor()
            cur.execute("""
                SELECT pm.id, pm.ma_phieu_muon, nm.ho_ten
                FROM phieu_muon pm
                JOIN nguoi_muon nm ON pm.nguoi_muon_id = nm.id
                LEFT JOIN phieu_tra pt ON pt.phieu_muon_id = pm.id
                WHERE pm.trang_thai = 'dang_muon'
                  AND pt.id IS NULL
                ORDER BY pm.id DESC
            """)
            rows = cur.fetchall()

            for row in rows:
                self.cbo_phieu_muon.addItem(f"{row[1]} - {row[2]}", row[0])

            cur.close()
            self.hien_chi_tiet_phieu_muon()
            self.cap_nhat_ma_phieu_tra_moi()

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))
        finally:
            if conn:
                conn.close()

    def hien_chi_tiet_phieu_muon(self):
        self.ds_chi_tiet = []
        self.table_chi_tiet.setRowCount(0)

        phieu_muon_id = self.cbo_phieu_muon.currentData()
        if not phieu_muon_id:
            return

        conn = None
        try:
            conn = tao_ket_noi()
            cur = conn.cursor()
            cur.execute("""
                SELECT ctm.id, ctm.sach_id, s.ten_sach, ctm.so_luong
                FROM chi_tiet_phieu_muon ctm
                JOIN sach s ON ctm.sach_id = s.id
                WHERE ctm.phieu_muon_id = %s
                ORDER BY ctm.id
            """, (phieu_muon_id,))
            self.ds_chi_tiet = cur.fetchall()
            cur.close()

            self.table_chi_tiet.setRowCount(len(self.ds_chi_tiet))
            for row, item in enumerate(self.ds_chi_tiet):
                self.table_chi_tiet.setItem(row, 0, QTableWidgetItem(str(item[0])))
                self.table_chi_tiet.setItem(row, 1, QTableWidgetItem(str(item[1])))
                self.table_chi_tiet.setItem(row, 2, QTableWidgetItem(str(item[2])))
                self.table_chi_tiet.setItem(row, 3, QTableWidgetItem(str(item[3])))

                spn_tra = QSpinBox()
                spn_tra.setRange(0, item[3])
                spn_tra.setValue(item[3])

                spn_hong = QSpinBox()
                spn_hong.setRange(0, item[3])

                spn_mat = QSpinBox()
                spn_mat.setRange(0, item[3])

                txt_ghi_chu = QLineEdit()

                self.table_chi_tiet.setCellWidget(row, 4, spn_tra)
                self.table_chi_tiet.setCellWidget(row, 5, spn_hong)
                self.table_chi_tiet.setCellWidget(row, 6, spn_mat)
                self.table_chi_tiet.setCellWidget(row, 7, txt_ghi_chu)

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))
        finally:
            if conn:
                conn.close()

    def tai_danh_sach_phieu_tra(self):
        conn = None
        try:
            conn = tao_ket_noi()
            cur = conn.cursor()
            cur.execute("""
                SELECT pt.id, pt.ma_phieu_tra, pm.ma_phieu_muon, pt.ngay_tra, pt.so_ngay_tre, pt.ghi_chu
                FROM phieu_tra pt
                JOIN phieu_muon pm ON pt.phieu_muon_id = pm.id
                ORDER BY pt.id DESC
            """)
            rows = cur.fetchall()

            self.table_ds.setRowCount(len(rows))
            for r, row in enumerate(rows):
                for c, value in enumerate(row):
                    self.table_ds.setItem(r, c, QTableWidgetItem("" if value is None else str(value)))

            cur.close()

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))
        finally:
            if conn:
                conn.close()

    def luu_phieu_tra(self):
        ma_phieu_tra = self.txt_ma_phieu_tra.text().strip()
        phieu_muon_id = self.cbo_phieu_muon.currentData()

        if not ma_phieu_tra or not phieu_muon_id:
            QMessageBox.warning(self, "Thông báo", "Vui lòng chọn phiếu mượn để lập phiếu trả.")
            return

        conn = None
        cur = None

        try:
            conn = tao_ket_noi()
            cur = conn.cursor()

            # Chặn trùng mã phiếu trả
            cur.execute("""
                SELECT 1
                FROM phieu_tra
                WHERE ma_phieu_tra = %s
            """, (ma_phieu_tra,))
            if cur.fetchone():
                raise Exception(f"Mã phiếu trả {ma_phieu_tra} đã tồn tại.")

            # Chặn trả lại phiếu đã có phiếu trả
            cur.execute("""
                SELECT 1
                FROM phieu_tra
                WHERE phieu_muon_id = %s
            """, (phieu_muon_id,))
            if cur.fetchone():
                raise Exception("Phiếu mượn này đã được lập phiếu trả.")

            cur.execute("""
                SELECT pm.ngay_hen_tra, pm.nguoi_muon_id
                FROM phieu_muon pm
                WHERE pm.id = %s
            """, (phieu_muon_id,))
            pm = cur.fetchone()

            if not pm:
                raise Exception("Không tìm thấy phiếu mượn.")

            ngay_tra = self.date_ngay_tra.date().toString("yyyy-MM-dd")
            d_ngay_tra = datetime.strptime(ngay_tra, "%Y-%m-%d").date()
            so_ngay_tre = max((d_ngay_tra - pm[0]).days, 0)

            cur.execute("""
                INSERT INTO phieu_tra (
                    ma_phieu_tra, phieu_muon_id, nguoi_xu_ly_id,
                    ngay_tra, so_ngay_tre, ghi_chu
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                ma_phieu_tra,
                phieu_muon_id,
                self.nguoi_dung_id,
                ngay_tra,
                so_ngay_tre,
                f"Trả sách - trễ {so_ngay_tre} ngày" if so_ngay_tre > 0 else "Trả sách"
            ))
            phieu_tra_id = cur.fetchone()[0]

            tong_tien_phat = 0
            ds_phat = []
            sach_id_dau_tien = None
            co_du_lieu_xu_ly = False

            for row in range(self.table_chi_tiet.rowCount()):
                chi_tiet_phieu_muon_id = int(self.table_chi_tiet.item(row, 0).text())
                sach_id = int(self.table_chi_tiet.item(row, 1).text())
                so_luong_muon = int(self.table_chi_tiet.item(row, 3).text())

                so_luong_tra = self.table_chi_tiet.cellWidget(row, 4).value()
                so_luong_hong = self.table_chi_tiet.cellWidget(row, 5).value()
                so_luong_mat = self.table_chi_tiet.cellWidget(row, 6).value()
                ghi_chu = self.table_chi_tiet.cellWidget(row, 7).text().strip()

                tong_xu_ly = so_luong_tra + so_luong_hong + so_luong_mat

                if tong_xu_ly != so_luong_muon:
                    raise Exception(
                        f"Dòng {row + 1}: Tổng số lượng trả + hỏng + mất phải bằng số lượng mượn."
                    )

                if tong_xu_ly > 0:
                    co_du_lieu_xu_ly = True
                    if sach_id_dau_tien is None:
                        sach_id_dau_tien = sach_id

                cur.execute("""
                    INSERT INTO chi_tiet_phieu_tra (
                        phieu_tra_id, chi_tiet_phieu_muon_id,
                        so_luong_tra, so_luong_hong, so_luong_mat, ghi_chu_tinh_trang
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    phieu_tra_id,
                    chi_tiet_phieu_muon_id,
                    so_luong_tra,
                    so_luong_hong,
                    so_luong_mat,
                    ghi_chu
                ))

                if so_luong_tra > 0:
                    cur.execute("""
                        UPDATE sach
                        SET so_luong_con = so_luong_con + %s
                        WHERE id = %s
                    """, (so_luong_tra, sach_id))

                if so_luong_hong > 0:
                    tien_hong = so_luong_hong * 45000
                    tong_tien_phat += tien_hong
                    ds_phat.append((
                        sach_id,
                        "lam_hong",
                        so_luong_hong,
                        45000,
                        tien_hong,
                        ghi_chu if ghi_chu else "Sách bị hỏng"
                    ))

                if so_luong_mat > 0:
                    tien_mat = so_luong_mat * 80000
                    tong_tien_phat += tien_mat
                    ds_phat.append((
                        sach_id,
                        "lam_mat",
                        so_luong_mat,
                        80000,
                        tien_mat,
                        ghi_chu if ghi_chu else "Sách bị mất"
                    ))

            if not co_du_lieu_xu_ly:
                raise Exception("Không có dữ liệu chi tiết để lưu phiếu trả.")

            # Phạt trả trễ: tính 1 dòng tổng
            if so_ngay_tre > 0 and sach_id_dau_tien is not None:
                tien_tre = so_ngay_tre * 5000
                tong_tien_phat += tien_tre
                ds_phat.append((
                    sach_id_dau_tien,
                    "tra_tre",
                    so_ngay_tre,
                    5000,
                    tien_tre,
                    f"Trễ {so_ngay_tre} ngày"
                ))

            cur.execute("""
                UPDATE phieu_muon
                SET trang_thai = 'da_tra'
                WHERE id = %s
            """, (phieu_muon_id,))

            if tong_tien_phat > 0:
                ma_phieu_phat = self.tao_ma_phieu_phat_moi(conn)

                cur.execute("""
                    INSERT INTO phieu_phat (
                        ma_phieu_phat, nguoi_muon_id, phieu_muon_id, phieu_tra_id,
                        tong_tien, trang_thai_thanh_toan, nguoi_lap_id
                    )
                    VALUES (%s, %s, %s, %s, %s, 'chua_thanh_toan', %s)
                    RETURNING id
                """, (
                    ma_phieu_phat,
                    pm[1],
                    phieu_muon_id,
                    phieu_tra_id,
                    tong_tien_phat,
                    self.nguoi_dung_id
                ))
                phieu_phat_id = cur.fetchone()[0]

                for item in ds_phat:
                    cur.execute("""
                        INSERT INTO chi_tiet_phieu_phat (
                            phieu_phat_id, sach_id, ly_do, so_luong,
                            don_gia_phat, thanh_tien, ghi_chu
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (phieu_phat_id, *item))

            conn.commit()

            QMessageBox.information(self, "Thành công", "Lưu phiếu trả thành công.")

            self.tai_combo_phieu_muon()
            self.tai_danh_sach_phieu_tra()
            self.cap_nhat_ma_phieu_tra_moi()
            self.date_ngay_tra.setDate(QDate.currentDate())

        except Exception as e:
            if conn:
                conn.rollback()
            QMessageBox.critical(self, "Lỗi", str(e))
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    def xuat_pdf(self):
        row = self.table_ds.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Thông báo", "Vui lòng chọn phiếu trả cần xuất PDF.")
            return

        phieu_tra_id = int(self.table_ds.item(row, 0).text())

        duong_dan_file, _ = QFileDialog.getSaveFileName(
            self,
            "Lưu phiếu trả PDF",
            "phieu_tra.pdf",
            "PDF Files (*.pdf)"
        )

        if not duong_dan_file:
            return

        conn = None
        try:
            conn = tao_ket_noi()
            cur = conn.cursor()

            cur.execute("""
                SELECT pt.ma_phieu_tra, pm.ma_phieu_muon, nm.ho_ten, pt.ngay_tra, pt.so_ngay_tre
                FROM phieu_tra pt
                JOIN phieu_muon pm ON pt.phieu_muon_id = pm.id
                JOIN nguoi_muon nm ON pm.nguoi_muon_id = nm.id
                WHERE pt.id = %s
            """, (phieu_tra_id,))
            row_info = cur.fetchone()

            if not row_info:
                raise Exception("Không tìm thấy phiếu trả.")

            thong_tin = {
                "ma_phieu_tra": row_info[0],
                "ma_phieu_muon": row_info[1],
                "ho_ten": row_info[2],
                "ngay_tra": str(row_info[3]),
                "so_ngay_tre": row_info[4]
            }

            cur.execute("""
                SELECT s.ten_sach,
                       ctpt.so_luong_tra,
                       ctpt.so_luong_hong,
                       ctpt.so_luong_mat,
                       ctpt.ghi_chu_tinh_trang
                FROM chi_tiet_phieu_tra ctpt
                JOIN chi_tiet_phieu_muon ctpm ON ctpt.chi_tiet_phieu_muon_id = ctpm.id
                JOIN sach s ON ctpm.sach_id = s.id
                WHERE ctpt.phieu_tra_id = %s
                ORDER BY ctpt.id
            """, (phieu_tra_id,))
            chi_tiet = cur.fetchall()

            cur.close()
            xuat_pdf_phieu_tra(duong_dan_file, thong_tin, chi_tiet)
            QMessageBox.information(self, "Thành công", "Xuất PDF phiếu trả thành công.")

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))
        finally:
            if conn:
                conn.close()



