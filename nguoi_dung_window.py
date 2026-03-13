from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QMessageBox, QDialog, QFormLayout,
    QLineEdit, QComboBox, QCheckBox, QHeaderView
)
from db import tao_ket_noi


class NguoiDungDialog(QDialog):
    def __init__(self, parent=None, du_lieu=None):
        super().__init__(parent)
        self.du_lieu = du_lieu
        self.setWindowTitle("Thông tin tài khoản")
        self.setFixedSize(420, 280)
        self.init_ui()

        if self.du_lieu:
            self.do_du_lieu_len_form()

    def init_ui(self):
        layout = QFormLayout()

        self.txt_ten_dang_nhap = QLineEdit()
        self.txt_mat_khau = QLineEdit()
        self.txt_ho_ten = QLineEdit()

        self.cbo_vai_tro = QComboBox()
        self.cbo_vai_tro.addItem("Quản trị", "quan_tri")
        self.cbo_vai_tro.addItem("Thủ thư", "thu_thu")

        self.chk_dang_hoat_dong = QCheckBox("Đang hoạt động")
        self.chk_dang_hoat_dong.setChecked(True)

        self.btn_luu = QPushButton("Lưu")
        self.btn_huy = QPushButton("Hủy")

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn_luu)
        btn_layout.addWidget(self.btn_huy)

        layout.addRow("Tên đăng nhập", self.txt_ten_dang_nhap)
        layout.addRow("Mật khẩu", self.txt_mat_khau)
        layout.addRow("Họ tên", self.txt_ho_ten)
        layout.addRow("Vai trò", self.cbo_vai_tro)
        layout.addRow("", self.chk_dang_hoat_dong)
        layout.addRow(btn_layout)

        self.setLayout(layout)

        self.btn_luu.clicked.connect(self.accept)
        self.btn_huy.clicked.connect(self.reject)

    def do_du_lieu_len_form(self):
        self.txt_ten_dang_nhap.setText(self.du_lieu["ten_dang_nhap"])
        self.txt_mat_khau.setText(self.du_lieu["mat_khau_ma_hoa"])
        self.txt_ho_ten.setText(self.du_lieu["ho_ten"])

        index = self.cbo_vai_tro.findData(self.du_lieu["vai_tro"])
        if index >= 0:
            self.cbo_vai_tro.setCurrentIndex(index)

        self.chk_dang_hoat_dong.setChecked(self.du_lieu["dang_hoat_dong"])

    def lay_du_lieu(self):
        return {
            "ten_dang_nhap": self.txt_ten_dang_nhap.text().strip(),
            "mat_khau_ma_hoa": self.txt_mat_khau.text().strip(),
            "ho_ten": self.txt_ho_ten.text().strip(),
            "vai_tro": self.cbo_vai_tro.currentData(),
            "dang_hoat_dong": self.chk_dang_hoat_dong.isChecked()
        }


class NguoiDungWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quản lý tài khoản")
        self.init_ui()
        self.tai_du_lieu()

    def init_ui(self):
        layout = QVBoxLayout()

        lbl = QLabel("DANH SÁCH TÀI KHOẢN")
        lbl.setStyleSheet("font-size: 18px; font-weight: bold;")

        top_layout = QHBoxLayout()
        self.txt_tim_kiem = QLineEdit()
        self.txt_tim_kiem.setPlaceholderText("Tìm theo tên đăng nhập / họ tên")
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
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Tên đăng nhập", "Họ tên", "Vai trò", "Hoạt động", "Ngày tạo"
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
        self.btn_them.clicked.connect(self.them_nguoi_dung)
        self.btn_sua.clicked.connect(self.sua_nguoi_dung)
        self.btn_xoa.clicked.connect(self.xoa_nguoi_dung)

    def lay_id_duoc_chon(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        return int(self.table.item(row, 0).text())

    def tai_du_lieu(self, tu_khoa=""):
        try:
            conn = tao_ket_noi()
            cur = conn.cursor()

            sql = """
                SELECT id, ten_dang_nhap, ho_ten, vai_tro, dang_hoat_dong, ngay_tao
                FROM nguoi_dung
            """
            params = []

            if tu_khoa:
                sql += """
                    WHERE LOWER(ten_dang_nhap) LIKE LOWER(%s)
                       OR LOWER(ho_ten) LIKE LOWER(%s)
                """
                keyword = f"%{tu_khoa}%"
                params = [keyword, keyword]

            sql += " ORDER BY id DESC"

            cur.execute(sql, params)
            rows = cur.fetchall()

            self.table.setRowCount(len(rows))
            for r, row in enumerate(rows):
                for c, value in enumerate(row):
                    self.table.setItem(r, c, QTableWidgetItem("" if value is None else str(value)))

            cur.close()
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))

    def tim_kiem(self):
        self.tai_du_lieu(self.txt_tim_kiem.text().strip())

    def lam_moi(self):
        self.txt_tim_kiem.clear()
        self.tai_du_lieu()

    def them_nguoi_dung(self):
        dialog = NguoiDungDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.lay_du_lieu()

            if not data["ten_dang_nhap"] or not data["mat_khau_ma_hoa"] or not data["ho_ten"]:
                QMessageBox.warning(self, "Thông báo", "Vui lòng nhập đầy đủ thông tin.")
                return

            try:
                conn = tao_ket_noi()
                cur = conn.cursor()

                cur.execute("""
                    INSERT INTO nguoi_dung (
                        ten_dang_nhap, mat_khau_ma_hoa, ho_ten, vai_tro, dang_hoat_dong
                    )
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    data["ten_dang_nhap"],
                    data["mat_khau_ma_hoa"],
                    data["ho_ten"],
                    data["vai_tro"],
                    data["dang_hoat_dong"]
                ))

                conn.commit()
                cur.close()
                conn.close()

                self.tai_du_lieu()
                QMessageBox.information(self, "Thành công", "Thêm tài khoản thành công.")
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", str(e))

    def sua_nguoi_dung(self):
        item_id = self.lay_id_duoc_chon()
        if not item_id:
            QMessageBox.warning(self, "Thông báo", "Vui lòng chọn tài khoản cần sửa.")
            return

        try:
            conn = tao_ket_noi()
            cur = conn.cursor()
            cur.execute("""
                SELECT id, ten_dang_nhap, mat_khau_ma_hoa, ho_ten, vai_tro, dang_hoat_dong
                FROM nguoi_dung
                WHERE id = %s
            """, (item_id,))
            row = cur.fetchone()
            cur.close()
            conn.close()

            if not row:
                QMessageBox.warning(self, "Thông báo", "Không tìm thấy tài khoản.")
                return

            du_lieu = {
                "id": row[0],
                "ten_dang_nhap": row[1],
                "mat_khau_ma_hoa": row[2],
                "ho_ten": row[3],
                "vai_tro": row[4],
                "dang_hoat_dong": row[5]
            }

            dialog = NguoiDungDialog(self, du_lieu)

            if dialog.exec_() == QDialog.Accepted:
                data = dialog.lay_du_lieu()

                if not data["ten_dang_nhap"] or not data["mat_khau_ma_hoa"] or not data["ho_ten"]:
                    QMessageBox.warning(self, "Thông báo", "Vui lòng nhập đầy đủ thông tin.")
                    return

                conn = tao_ket_noi()
                cur = conn.cursor()
                cur.execute("""
                    UPDATE nguoi_dung
                    SET ten_dang_nhap = %s,
                        mat_khau_ma_hoa = %s,
                        ho_ten = %s,
                        vai_tro = %s,
                        dang_hoat_dong = %s
                    WHERE id = %s
                """, (
                    data["ten_dang_nhap"],
                    data["mat_khau_ma_hoa"],
                    data["ho_ten"],
                    data["vai_tro"],
                    data["dang_hoat_dong"],
                    item_id
                ))
                conn.commit()
                cur.close()
                conn.close()

                self.tai_du_lieu()
                QMessageBox.information(self, "Thành công", "Cập nhật tài khoản thành công.")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))

    def xoa_nguoi_dung(self):
        item_id = self.lay_id_duoc_chon()
        if not item_id:
            QMessageBox.warning(self, "Thông báo", "Vui lòng chọn tài khoản cần xóa.")
            return

        tra_loi = QMessageBox.question(self, "Xác nhận", "Bạn có chắc muốn xóa tài khoản này không?")
        if tra_loi != QMessageBox.Yes:
            return

        try:
            conn = tao_ket_noi()
            cur = conn.cursor()
            cur.execute("DELETE FROM nguoi_dung WHERE id = %s", (item_id,))
            conn.commit()
            cur.close()
            conn.close()

            self.tai_du_lieu()
            QMessageBox.information(self, "Thành công", "Xóa tài khoản thành công.")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể xóa tài khoản.\n{e}")