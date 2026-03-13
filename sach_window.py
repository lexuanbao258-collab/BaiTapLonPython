from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QMessageBox, QDialog, QFormLayout,
    QLineEdit, QSpinBox, QComboBox, QHeaderView
)
from db import tao_ket_noi


class SachDialog(QDialog):
    def __init__(self, parent=None, du_lieu=None):
        super().__init__(parent)
        self.du_lieu = du_lieu
        self.setWindowTitle("Thông tin sách")
        self.setFixedSize(460, 430)
        self.ds_the_loai = []
        self.ds_nxb = []
        self.init_ui()
        self.load_combo()
        if self.du_lieu:
            self.do_du_lieu_len_form()

    def init_ui(self):
        layout = QFormLayout()

        self.txt_ma_sach = QLineEdit()
        self.txt_ten_sach = QLineEdit()
        self.txt_tac_gia = QLineEdit()

        self.cbo_the_loai = QComboBox()
        self.cbo_the_loai.addItem("-- Chọn thể loại --", None)

        self.cbo_nxb = QComboBox()
        self.cbo_nxb.addItem("-- Chọn nhà xuất bản --", None)

        self.txt_nam_xuat_ban = QLineEdit()
        self.txt_vi_tri_ke = QLineEdit()

        self.spn_tong_so_luong = QSpinBox()
        self.spn_tong_so_luong.setRange(0, 100000)

        self.btn_luu = QPushButton("Lưu")
        self.btn_huy = QPushButton("Hủy")

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn_luu)
        btn_layout.addWidget(self.btn_huy)

        layout.addRow("Mã sách", self.txt_ma_sach)
        layout.addRow("Tên sách", self.txt_ten_sach)
        layout.addRow("Tác giả", self.txt_tac_gia)
        layout.addRow("Thể loại", self.cbo_the_loai)
        layout.addRow("Nhà xuất bản", self.cbo_nxb)
        layout.addRow("Năm xuất bản", self.txt_nam_xuat_ban)
        layout.addRow("Vị trí kệ", self.txt_vi_tri_ke)
        layout.addRow("Tổng số lượng", self.spn_tong_so_luong)
        layout.addRow(btn_layout)

        self.setLayout(layout)

        self.btn_luu.clicked.connect(self.accept)
        self.btn_huy.clicked.connect(self.reject)

    def load_combo(self):
        self.cbo_the_loai.clear()
        self.cbo_the_loai.addItem("-- Chọn thể loại --", None)

        self.cbo_nxb.clear()
        self.cbo_nxb.addItem("-- Chọn nhà xuất bản --", None)

        conn = tao_ket_noi()
        cur = conn.cursor()

        cur.execute("SELECT id, ten_the_loai FROM the_loai ORDER BY ten_the_loai")
        self.ds_the_loai = cur.fetchall()
        for item in self.ds_the_loai:
            self.cbo_the_loai.addItem(item[1], item[0])

        cur.execute("SELECT id, ten_nha_xuat_ban FROM nha_xuat_ban ORDER BY ten_nha_xuat_ban")
        self.ds_nxb = cur.fetchall()
        for item in self.ds_nxb:
            self.cbo_nxb.addItem(item[1], item[0])

        cur.close()
        conn.close()

    def do_du_lieu_len_form(self):
        self.txt_ma_sach.setText(self.du_lieu["ma_sach"])
        self.txt_ten_sach.setText(self.du_lieu["ten_sach"])
        self.txt_tac_gia.setText(self.du_lieu["tac_gia"] or "")
        self.txt_nam_xuat_ban.setText("" if self.du_lieu["nam_xuat_ban"] is None else str(self.du_lieu["nam_xuat_ban"]))
        self.txt_vi_tri_ke.setText(self.du_lieu["vi_tri_ke"] or "")
        self.spn_tong_so_luong.setValue(self.du_lieu["tong_so_luong"])

        index_tl = self.cbo_the_loai.findData(self.du_lieu["the_loai_id"])
        if index_tl >= 0:
            self.cbo_the_loai.setCurrentIndex(index_tl)

        index_nxb = self.cbo_nxb.findData(self.du_lieu["nha_xuat_ban_id"])
        if index_nxb >= 0:
            self.cbo_nxb.setCurrentIndex(index_nxb)

    def lay_du_lieu(self):
        nam_xuat_ban = self.txt_nam_xuat_ban.text().strip()

        return {
            "ma_sach": self.txt_ma_sach.text().strip(),
            "ten_sach": self.txt_ten_sach.text().strip(),
            "tac_gia": self.txt_tac_gia.text().strip(),
            "the_loai_id": self.cbo_the_loai.currentData(),
            "nha_xuat_ban_id": self.cbo_nxb.currentData(),
            "nam_xuat_ban": int(nam_xuat_ban) if nam_xuat_ban else None,
            "vi_tri_ke": self.txt_vi_tri_ke.text().strip(),
            "tong_so_luong": self.spn_tong_so_luong.value()
        }


class SachWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quản lý sách")
        self.init_ui()
        self.tai_du_lieu()

    def init_ui(self):
        layout = QVBoxLayout()

        lbl = QLabel("DANH SÁCH SÁCH")
        lbl.setStyleSheet("font-size: 18px; font-weight: bold;")

        top_layout = QHBoxLayout()
        self.txt_tim_kiem = QLineEdit()
        self.txt_tim_kiem.setPlaceholderText("Tìm theo mã sách / tên sách / tác giả")
        self.btn_tim_kiem = QPushButton("Tìm kiếm")
        self.btn_lam_moi = QPushButton("Làm mới")

        top_layout.addWidget(self.txt_tim_kiem)
        top_layout.addWidget(self.btn_tim_kiem)
        top_layout.addWidget(self.btn_lam_moi)

        btn_layout = QHBoxLayout()
        self.btn_them = QPushButton("Thêm")
        self.btn_sua = QPushButton("Sửa")
        self.btn_xoa = QPushButton("Xóa")

        btn_layout.addWidget(self.btn_them)
        btn_layout.addWidget(self.btn_sua)
        btn_layout.addWidget(self.btn_xoa)

        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "ID",
            "Mã sách",
            "Tên sách",
            "Tác giả",
            "Thể loại",
            "Nhà xuất bản",
            "Năm XB",
            "Vị trí kệ",
            "Tổng số lượng",
            "Số lượng còn"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setColumnHidden(0, True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        layout.addWidget(lbl)
        layout.addLayout(top_layout)
        layout.addLayout(btn_layout)
        layout.addWidget(self.table)

        self.setLayout(layout)

        self.btn_tim_kiem.clicked.connect(self.tim_kiem)
        self.btn_lam_moi.clicked.connect(self.lam_moi)
        self.btn_them.clicked.connect(self.them_sach)
        self.btn_sua.clicked.connect(self.sua_sach)
        self.btn_xoa.clicked.connect(self.xoa_sach)

    def lay_sach_duoc_chon(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        return int(self.table.item(row, 0).text())

    def tai_du_lieu(self, tu_khoa=""):
        try:
            conn = tao_ket_noi()
            cur = conn.cursor()

            sql = """
                SELECT s.id, s.ma_sach, s.ten_sach, s.tac_gia,
                       tl.ten_the_loai, nxb.ten_nha_xuat_ban,
                       s.nam_xuat_ban, s.vi_tri_ke,
                       s.tong_so_luong, s.so_luong_con
                FROM sach s
                LEFT JOIN the_loai tl ON s.the_loai_id = tl.id
                LEFT JOIN nha_xuat_ban nxb ON s.nha_xuat_ban_id = nxb.id
            """
            params = []

            if tu_khoa:
                sql += """
                    WHERE LOWER(s.ma_sach) LIKE LOWER(%s)
                       OR LOWER(s.ten_sach) LIKE LOWER(%s)
                       OR LOWER(s.tac_gia) LIKE LOWER(%s)
                """
                keyword = f"%{tu_khoa}%"
                params = [keyword, keyword, keyword]

            sql += " ORDER BY s.id DESC"

            cur.execute(sql, params)
            ds_sach = cur.fetchall()

            self.table.setRowCount(len(ds_sach))
            for row, sach in enumerate(ds_sach):
                for col, value in enumerate(sach):
                    self.table.setItem(row, col, QTableWidgetItem("" if value is None else str(value)))

            cur.close()
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))

    def tim_kiem(self):
        self.tai_du_lieu(self.txt_tim_kiem.text().strip())

    def lam_moi(self):
        self.txt_tim_kiem.clear()
        self.tai_du_lieu()

    def them_sach(self):
        dialog = SachDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.lay_du_lieu()

            if not data["ma_sach"] or not data["ten_sach"] or not data["tac_gia"]:
                QMessageBox.warning(self, "Thông báo", "Vui lòng nhập mã sách, tên sách và tác giả.")
                return

            try:
                conn = tao_ket_noi()
                cur = conn.cursor()

                cur.execute("""
                    INSERT INTO sach (
                        ma_sach, ten_sach, tac_gia, the_loai_id, nha_xuat_ban_id,
                        nam_xuat_ban, vi_tri_ke, tong_so_luong, so_luong_con
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    data["ma_sach"],
                    data["ten_sach"],
                    data["tac_gia"],
                    data["the_loai_id"],
                    data["nha_xuat_ban_id"],
                    data["nam_xuat_ban"],
                    data["vi_tri_ke"] or None,
                    data["tong_so_luong"],
                    data["tong_so_luong"]
                ))

                conn.commit()
                cur.close()
                conn.close()

                self.tai_du_lieu()
                QMessageBox.information(self, "Thành công", "Thêm sách thành công.")
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", str(e))

    def sua_sach(self):
        sach_id = self.lay_sach_duoc_chon()
        if not sach_id:
            QMessageBox.warning(self, "Thông báo", "Vui lòng chọn sách cần sửa.")
            return

        try:
            conn = tao_ket_noi()
            cur = conn.cursor()
            cur.execute("""
                SELECT id, ma_sach, ten_sach, tac_gia, the_loai_id, nha_xuat_ban_id,
                       nam_xuat_ban, vi_tri_ke, tong_so_luong, so_luong_con
                FROM sach
                WHERE id = %s
            """, (sach_id,))
            row = cur.fetchone()
            cur.close()
            conn.close()

            if not row:
                QMessageBox.warning(self, "Thông báo", "Không tìm thấy sách.")
                return

            du_lieu = {
                "id": row[0],
                "ma_sach": row[1],
                "ten_sach": row[2],
                "tac_gia": row[3],
                "the_loai_id": row[4],
                "nha_xuat_ban_id": row[5],
                "nam_xuat_ban": row[6],
                "vi_tri_ke": row[7],
                "tong_so_luong": row[8],
                "so_luong_con": row[9]
            }

            dialog = SachDialog(self, du_lieu)

            if dialog.exec_() == QDialog.Accepted:
                data = dialog.lay_du_lieu()

                if not data["ma_sach"] or not data["ten_sach"] or not data["tac_gia"]:
                    QMessageBox.warning(self, "Thông báo", "Vui lòng nhập mã sách, tên sách và tác giả.")
                    return

                da_muon = du_lieu["tong_so_luong"] - du_lieu["so_luong_con"]
                if data["tong_so_luong"] < da_muon:
                    QMessageBox.warning(
                        self,
                        "Thông báo",
                        f"Tổng số lượng mới không được nhỏ hơn số sách đang mượn ({da_muon})."
                    )
                    return

                so_luong_con_moi = data["tong_so_luong"] - da_muon

                conn = tao_ket_noi()
                cur = conn.cursor()
                cur.execute("""
                    UPDATE sach
                    SET ma_sach = %s,
                        ten_sach = %s,
                        tac_gia = %s,
                        the_loai_id = %s,
                        nha_xuat_ban_id = %s,
                        nam_xuat_ban = %s,
                        vi_tri_ke = %s,
                        tong_so_luong = %s,
                        so_luong_con = %s
                    WHERE id = %s
                """, (
                    data["ma_sach"],
                    data["ten_sach"],
                    data["tac_gia"],
                    data["the_loai_id"],
                    data["nha_xuat_ban_id"],
                    data["nam_xuat_ban"],
                    data["vi_tri_ke"] or None,
                    data["tong_so_luong"],
                    so_luong_con_moi,
                    sach_id
                ))
                conn.commit()
                cur.close()
                conn.close()

                self.tai_du_lieu()
                QMessageBox.information(self, "Thành công", "Cập nhật sách thành công.")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))

    def xoa_sach(self):
        sach_id = self.lay_sach_duoc_chon()
        if not sach_id:
            QMessageBox.warning(self, "Thông báo", "Vui lòng chọn sách cần xóa.")
            return

        tra_loi = QMessageBox.question(self, "Xác nhận", "Bạn có chắc muốn xóa sách này không?")
        if tra_loi != QMessageBox.Yes:
            return

        try:
            conn = tao_ket_noi()
            cur = conn.cursor()
            cur.execute("DELETE FROM sach WHERE id = %s", (sach_id,))
            conn.commit()
            cur.close()
            conn.close()

            self.tai_du_lieu()
            QMessageBox.information(self, "Thành công", "Xóa sách thành công.")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể xóa sách.\n{e}")