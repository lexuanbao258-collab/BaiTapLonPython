from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QMessageBox, QDialog, QFormLayout,
    QLineEdit, QHeaderView
)
from db import tao_ket_noi


class TheLoaiDialog(QDialog):
    def __init__(self, parent=None, du_lieu=None):
        super().__init__(parent)
        self.du_lieu = du_lieu
        self.setWindowTitle("Thông tin thể loại")
        self.setFixedSize(400, 160)
        self.init_ui()
        if self.du_lieu:
            self.txt_ten_the_loai.setText(self.du_lieu["ten_the_loai"])

    def init_ui(self):
        layout = QFormLayout()

        self.txt_ten_the_loai = QLineEdit()

        self.btn_luu = QPushButton("Lưu")
        self.btn_huy = QPushButton("Hủy")

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn_luu)
        btn_layout.addWidget(self.btn_huy)

        layout.addRow("Tên thể loại", self.txt_ten_the_loai)
        layout.addRow(btn_layout)

        self.setLayout(layout)

        self.btn_luu.clicked.connect(self.accept)
        self.btn_huy.clicked.connect(self.reject)

    def lay_du_lieu(self):
        return {
            "ten_the_loai": self.txt_ten_the_loai.text().strip()
        }


class TheLoaiWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quản lý thể loại")
        self.init_ui()
        self.tai_du_lieu()

    def init_ui(self):
        layout = QVBoxLayout()

        lbl = QLabel("DANH SÁCH THỂ LOẠI SÁCH")
        lbl.setStyleSheet("font-size: 18px; font-weight: bold;")

        top_layout = QHBoxLayout()
        self.txt_tim_kiem = QLineEdit()
        self.txt_tim_kiem.setPlaceholderText("Tìm theo tên thể loại")
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
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["ID", "Tên thể loại"])
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
        self.btn_them.clicked.connect(self.them_the_loai)
        self.btn_sua.clicked.connect(self.sua_the_loai)
        self.btn_xoa.clicked.connect(self.xoa_the_loai)

    def lay_id_duoc_chon(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        return int(self.table.item(row, 0).text())

    def tai_du_lieu(self, tu_khoa=""):
        try:
            conn = tao_ket_noi()
            cur = conn.cursor()

            sql = "SELECT id, ten_the_loai FROM the_loai"
            params = []
            if tu_khoa:
                sql += " WHERE LOWER(ten_the_loai) LIKE LOWER(%s)"
                params = [f"%{tu_khoa}%"]
            sql += " ORDER BY ten_the_loai"

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

    def them_the_loai(self):
        dialog = TheLoaiDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.lay_du_lieu()

            if not data["ten_the_loai"]:
                QMessageBox.warning(self, "Thông báo", "Vui lòng nhập tên thể loại.")
                return

            try:
                conn = tao_ket_noi()
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO the_loai (ten_the_loai)
                    VALUES (%s)
                """, (data["ten_the_loai"],))
                conn.commit()
                cur.close()
                conn.close()
                self.tai_du_lieu()
                QMessageBox.information(self, "Thành công", "Thêm thể loại thành công.")
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", str(e))

    def sua_the_loai(self):
        item_id = self.lay_id_duoc_chon()
        if not item_id:
            QMessageBox.warning(self, "Thông báo", "Vui lòng chọn thể loại cần sửa.")
            return

        try:
            conn = tao_ket_noi()
            cur = conn.cursor()
            cur.execute("SELECT id, ten_the_loai FROM the_loai WHERE id = %s", (item_id,))
            row = cur.fetchone()
            cur.close()
            conn.close()

            if not row:
                QMessageBox.warning(self, "Thông báo", "Không tìm thấy thể loại.")
                return

            du_lieu = {"id": row[0], "ten_the_loai": row[1]}
            dialog = TheLoaiDialog(self, du_lieu)

            if dialog.exec_() == QDialog.Accepted:
                data = dialog.lay_du_lieu()

                if not data["ten_the_loai"]:
                    QMessageBox.warning(self, "Thông báo", "Vui lòng nhập tên thể loại.")
                    return

                conn = tao_ket_noi()
                cur = conn.cursor()
                cur.execute("""
                    UPDATE the_loai
                    SET ten_the_loai = %s
                    WHERE id = %s
                """, (data["ten_the_loai"], item_id))
                conn.commit()
                cur.close()
                conn.close()

                self.tai_du_lieu()
                QMessageBox.information(self, "Thành công", "Cập nhật thể loại thành công.")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))

    def xoa_the_loai(self):
        item_id = self.lay_id_duoc_chon()
        if not item_id:
            QMessageBox.warning(self, "Thông báo", "Vui lòng chọn thể loại cần xóa.")
            return

        tra_loi = QMessageBox.question(self, "Xác nhận", "Bạn có chắc muốn xóa thể loại này không?")
        if tra_loi != QMessageBox.Yes:
            return

        try:
            conn = tao_ket_noi()
            cur = conn.cursor()
            cur.execute("DELETE FROM the_loai WHERE id = %s", (item_id,))
            conn.commit()
            cur.close()
            conn.close()
            self.tai_du_lieu()
            QMessageBox.information(self, "Thành công", "Xóa thể loại thành công.")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể xóa thể loại.\n{e}")