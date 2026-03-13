from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QMessageBox, QDialog, QFormLayout,
    QLineEdit, QHeaderView
)
from db import tao_ket_noi


class NguoiMuonDialog(QDialog):
    def __init__(self, parent=None, du_lieu=None):
        super().__init__(parent)
        self.du_lieu = du_lieu
        self.setWindowTitle("Thông tin người mượn")
        self.setFixedSize(420, 260)
        self.init_ui()
        if self.du_lieu:
            self.do_du_lieu_len_form()

    def init_ui(self):
        layout = QFormLayout()

        self.txt_ma_nguoi_muon = QLineEdit()
        self.txt_ho_ten = QLineEdit()
        self.txt_so_dien_thoai = QLineEdit()
        self.txt_email = QLineEdit()
        self.txt_dia_chi = QLineEdit()

        self.btn_luu = QPushButton("Lưu")
        self.btn_huy = QPushButton("Hủy")

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn_luu)
        btn_layout.addWidget(self.btn_huy)

        layout.addRow("Mã người mượn", self.txt_ma_nguoi_muon)
        layout.addRow("Họ tên", self.txt_ho_ten)
        layout.addRow("Số điện thoại", self.txt_so_dien_thoai)
        layout.addRow("Email", self.txt_email)
        layout.addRow("Địa chỉ", self.txt_dia_chi)
        layout.addRow(btn_layout)

        self.setLayout(layout)

        self.btn_luu.clicked.connect(self.accept)
        self.btn_huy.clicked.connect(self.reject)

    def do_du_lieu_len_form(self):
        self.txt_ma_nguoi_muon.setText(self.du_lieu["ma_nguoi_muon"])
        self.txt_ho_ten.setText(self.du_lieu["ho_ten"])
        self.txt_so_dien_thoai.setText(self.du_lieu["so_dien_thoai"] or "")
        self.txt_email.setText(self.du_lieu["email"] or "")
        self.txt_dia_chi.setText(self.du_lieu["dia_chi"] or "")

    def lay_du_lieu(self):
        return {
            "ma_nguoi_muon": self.txt_ma_nguoi_muon.text().strip(),
            "ho_ten": self.txt_ho_ten.text().strip(),
            "so_dien_thoai": self.txt_so_dien_thoai.text().strip(),
            "email": self.txt_email.text().strip(),
            "dia_chi": self.txt_dia_chi.text().strip()
        }


class NguoiMuonWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quản lý người mượn")
        self.setGeometry(240, 140, 1000, 560)
        self.init_ui()
        self.tai_du_lieu()

    def init_ui(self):
        layout = QVBoxLayout()

        lbl = QLabel("DANH SÁCH NGƯỜI MƯỢN")
        lbl.setStyleSheet("font-size: 18px; font-weight: bold;")

        top_layout = QHBoxLayout()
        self.txt_tim_kiem = QLineEdit()
        self.txt_tim_kiem.setPlaceholderText("Tìm theo mã người mượn / họ tên / số điện thoại")
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
            "ID", "Mã người mượn", "Họ tên", "Số điện thoại", "Email", "Địa chỉ"
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
        self.btn_lam_moi.clicked.connect(self.tai_du_lieu)
        self.btn_them.clicked.connect(self.them_nguoi_muon)
        self.btn_sua.clicked.connect(self.sua_nguoi_muon)
        self.btn_xoa.clicked.connect(self.xoa_nguoi_muon)

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
                SELECT id, ma_nguoi_muon, ho_ten, so_dien_thoai, email, dia_chi
                FROM nguoi_muon
            """
            params = []
            if tu_khoa:
                sql += """
                    WHERE LOWER(ma_nguoi_muon) LIKE LOWER(%s)
                       OR LOWER(ho_ten) LIKE LOWER(%s)
                       OR LOWER(COALESCE(so_dien_thoai, '')) LIKE LOWER(%s)
                """
                keyword = f"%{tu_khoa}%"
                params = [keyword, keyword, keyword]

            sql += " ORDER BY id DESC"
            cur.execute(sql, params)
            ds = cur.fetchall()

            self.table.setRowCount(len(ds))
            for row, item in enumerate(ds):
                for col, value in enumerate(item):
                    self.table.setItem(row, col, QTableWidgetItem("" if value is None else str(value)))

            cur.close()
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))

    def tim_kiem(self):
        self.tai_du_lieu(self.txt_tim_kiem.text().strip())

    def them_nguoi_muon(self):
        dialog = NguoiMuonDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.lay_du_lieu()

            if not data["ma_nguoi_muon"] or not data["ho_ten"]:
                QMessageBox.warning(self, "Thông báo", "Vui lòng nhập mã người mượn và họ tên.")
                return

            try:
                conn = tao_ket_noi()
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO nguoi_muon (ma_nguoi_muon, ho_ten, so_dien_thoai, email, dia_chi)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    data["ma_nguoi_muon"], data["ho_ten"],
                    data["so_dien_thoai"] or None,
                    data["email"] or None,
                    data["dia_chi"] or None
                ))
                conn.commit()
                cur.close()
                conn.close()
                self.tai_du_lieu()
                QMessageBox.information(self, "Thành công", "Thêm người mượn thành công.")
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", str(e))

    def sua_nguoi_muon(self):
        item_id = self.lay_id_duoc_chon()
        if not item_id:
            QMessageBox.warning(self, "Thông báo", "Vui lòng chọn người mượn cần sửa.")
            return

        try:
            conn = tao_ket_noi()
            cur = conn.cursor()
            cur.execute("""
                SELECT id, ma_nguoi_muon, ho_ten, so_dien_thoai, email, dia_chi
                FROM nguoi_muon
                WHERE id = %s
            """, (item_id,))
            row = cur.fetchone()
            cur.close()
            conn.close()

            if not row:
                QMessageBox.warning(self, "Thông báo", "Không tìm thấy dữ liệu.")
                return

            du_lieu = {
                "id": row[0],
                "ma_nguoi_muon": row[1],
                "ho_ten": row[2],
                "so_dien_thoai": row[3],
                "email": row[4],
                "dia_chi": row[5]
            }

            dialog = NguoiMuonDialog(self, du_lieu)
            if dialog.exec_() == QDialog.Accepted:
                data = dialog.lay_du_lieu()
                if not data["ma_nguoi_muon"] or not data["ho_ten"]:
                    QMessageBox.warning(self, "Thông báo", "Vui lòng nhập mã người mượn và họ tên.")
                    return

                conn = tao_ket_noi()
                cur = conn.cursor()
                cur.execute("""
                    UPDATE nguoi_muon
                    SET ma_nguoi_muon = %s,
                        ho_ten = %s,
                        so_dien_thoai = %s,
                        email = %s,
                        dia_chi = %s
                    WHERE id = %s
                """, (
                    data["ma_nguoi_muon"], data["ho_ten"],
                    data["so_dien_thoai"] or None,
                    data["email"] or None,
                    data["dia_chi"] or None,
                    item_id
                ))
                conn.commit()
                cur.close()
                conn.close()
                self.tai_du_lieu()
                QMessageBox.information(self, "Thành công", "Cập nhật người mượn thành công.")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))

    def xoa_nguoi_muon(self):
        item_id = self.lay_id_duoc_chon()
        if not item_id:
            QMessageBox.warning(self, "Thông báo", "Vui lòng chọn người mượn cần xóa.")
            return

        tra_loi = QMessageBox.question(self, "Xác nhận", "Bạn có chắc muốn xóa người mượn này không?")
        if tra_loi != QMessageBox.Yes:
            return

        try:
            conn = tao_ket_noi()
            cur = conn.cursor()
            cur.execute("DELETE FROM nguoi_muon WHERE id = %s", (item_id,))
            conn.commit()
            cur.close()
            conn.close()
            self.tai_du_lieu()
            QMessageBox.information(self, "Thành công", "Xóa người mượn thành công.")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể xóa người mượn.\n{e}")