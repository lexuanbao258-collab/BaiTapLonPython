from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QPushButton, QMessageBox, QStackedWidget, QFrame, QSizePolicy
)
from PyQt5.QtCore import Qt

from sach_window import SachWindow
from nguoi_muon_window import NguoiMuonWindow
from the_loai_window import TheLoaiWindow
from nha_xuat_ban_window import NhaXuatBanWindow
from nguoi_dung_window import NguoiDungWindow
from phieu_muon_window import PhieuMuonWindow
from phieu_tra_window import PhieuTraWindow
from phieu_phat_window import PhieuPhatWindow
from thong_ke_window import ThongKeWindow


class TrangChuWidget(QWidget):
    def __init__(self, ho_ten, vai_tro):
        super().__init__()
        self.ho_ten = ho_ten
        self.vai_tro = vai_tro
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        title = QLabel("HỆ THỐNG QUẢN LÝ THƯ VIỆN")
        title.setObjectName("pageTitle")
        title.setAlignment(Qt.AlignCenter)

        sub = QLabel(f"Xin chào {self.ho_ten} | Vai trò: {self.vai_tro}")
        sub.setObjectName("pageSubtitle")
        sub.setAlignment(Qt.AlignCenter)

        card_row_1 = QHBoxLayout()
        card_row_1.setSpacing(20)

        card_row_2 = QHBoxLayout()
        card_row_2.setSpacing(20)

        card1 = self.tao_the("Quản lý sách", "Thêm, sửa, xóa và tìm kiếm sách trong thư viện.")
        card2 = self.tao_the("Người mượn", "Quản lý thông tin người mượn và tra cứu dữ liệu.")
        card3 = self.tao_the("Thể loại sách", "Quản lý danh mục thể loại để chuẩn hóa dữ liệu sách.")
        card4 = self.tao_the("Nhà xuất bản", "Quản lý nhà xuất bản phục vụ nhập liệu và thống kê.")

        card5 = self.tao_the("Quản lý tài khoản", "Quản lý tài khoản đăng nhập và phân quyền sử dụng hệ thống.")
        card6 = self.tao_the("Phiếu mượn", "Lập phiếu mượn, chọn sách và cập nhật số lượng còn.")
        card7 = self.tao_the("Phiếu trả", "Tiếp nhận trả sách, tính số ngày trễ và cập nhật kho.")
        card8 = self.tao_the("Phiếu phạt", "Quản lý các khoản phạt do trễ, hỏng hoặc mất sách.")
        card9 = self.tao_the("Thống kê", "Xem tổng quan dữ liệu và các chỉ số quan trọng của hệ thống.")

        card_row_1.addWidget(card1)
        card_row_1.addWidget(card2)
        card_row_1.addWidget(card3)
        card_row_1.addWidget(card4)

        card_row_2.addWidget(card5)
        card_row_2.addWidget(card6)
        card_row_2.addWidget(card7)
        card_row_2.addWidget(card8)
        card_row_2.addWidget(card9)

        layout.addStretch()
        layout.addWidget(title)
        layout.addWidget(sub)
        layout.addSpacing(15)
        layout.addLayout(card_row_1)
        layout.addLayout(card_row_2)
        layout.addStretch()

        self.setLayout(layout)

    def tao_the(self, tieu_de, noi_dung):
        card = QFrame()
        card.setObjectName("homeCard")
        card.setMinimumHeight(150)

        layout = QVBoxLayout()
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)

        lbl_title = QLabel(tieu_de)
        lbl_title.setObjectName("cardTitle")

        lbl_content = QLabel(noi_dung)
        lbl_content.setWordWrap(True)
        lbl_content.setObjectName("cardText")

        layout.addWidget(lbl_title)
        layout.addWidget(lbl_content)
        layout.addStretch()

        card.setLayout(layout)
        return card


class MainWindow(QMainWindow):
    def __init__(self, nguoi_dung_id, ho_ten, vai_tro):
        super().__init__()
        self.nguoi_dung_id = nguoi_dung_id
        self.ho_ten = ho_ten
        self.vai_tro = vai_tro

        self.setWindowTitle("Hệ thống quản lý thư viện")
        self.setGeometry(100, 50, 1400, 800)

        self.init_ui()
        self.ap_dung_style()

    def init_ui(self):
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.sidebar = self.tao_sidebar()
        self.content = self.tao_content()

        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.content)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def tao_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(260)

        layout = QVBoxLayout()
        layout.setContentsMargins(18, 20, 18, 20)
        layout.setSpacing(10)

        logo = QLabel("THƯ VIỆN")
        logo.setObjectName("logoLabel")
        logo.setAlignment(Qt.AlignCenter)

        user_info = QLabel(f"{self.ho_ten}\n{self.vai_tro}")
        user_info.setObjectName("userInfo")
        user_info.setAlignment(Qt.AlignCenter)

        self.btn_trang_chu = self.tao_nut_menu("Trang chủ")
        self.btn_sach = self.tao_nut_menu("Quản lý sách")
        self.btn_nguoi_muon = self.tao_nut_menu("Người mượn")
        self.btn_the_loai = self.tao_nut_menu("Thể loại sách")
        self.btn_nha_xuat_ban = self.tao_nut_menu("Nhà xuất bản")
        self.btn_nguoi_dung = self.tao_nut_menu("Quản lý tài khoản")
        self.btn_phieu_muon = self.tao_nut_menu("Phiếu mượn")
        self.btn_phieu_tra = self.tao_nut_menu("Phiếu trả")
        self.btn_phieu_phat = self.tao_nut_menu("Phiếu phạt")
        self.btn_thong_ke = self.tao_nut_menu("Thống kê")
        self.btn_dang_xuat = self.tao_nut_menu("Đăng xuất")

        self.btn_trang_chu.clicked.connect(lambda: self.chuyen_trang(0, "Trang chủ"))
        self.btn_sach.clicked.connect(lambda: self.chuyen_trang(1, "Quản lý sách"))
        self.btn_nguoi_muon.clicked.connect(lambda: self.chuyen_trang(2, "Người mượn"))
        self.btn_the_loai.clicked.connect(lambda: self.chuyen_trang(3, "Thể loại sách"))
        self.btn_nha_xuat_ban.clicked.connect(lambda: self.chuyen_trang(4, "Nhà xuất bản"))
        self.btn_nguoi_dung.clicked.connect(self.mo_quan_ly_tai_khoan)
        self.btn_phieu_muon.clicked.connect(lambda: self.chuyen_trang(6, "Phiếu mượn"))
        self.btn_phieu_tra.clicked.connect(lambda: self.chuyen_trang(7, "Phiếu trả"))
        self.btn_phieu_phat.clicked.connect(lambda: self.chuyen_trang(8, "Phiếu phạt"))
        self.btn_thong_ke.clicked.connect(lambda: self.chuyen_trang(9, "Thống kê"))
        self.btn_dang_xuat.clicked.connect(self.dang_xuat)

        layout.addWidget(logo)
        layout.addWidget(user_info)
        layout.addSpacing(12)

        layout.addWidget(self.btn_trang_chu)
        layout.addWidget(self.btn_sach)
        layout.addWidget(self.btn_nguoi_muon)
        layout.addWidget(self.btn_the_loai)
        layout.addWidget(self.btn_nha_xuat_ban)

        if self.vai_tro == "quan_tri":
            layout.addWidget(self.btn_nguoi_dung)

        layout.addWidget(self.btn_phieu_muon)
        layout.addWidget(self.btn_phieu_tra)
        layout.addWidget(self.btn_phieu_phat)
        layout.addWidget(self.btn_thong_ke)

        layout.addStretch()
        layout.addWidget(self.btn_dang_xuat)

        sidebar.setLayout(layout)
        return sidebar

    def tao_nut_menu(self, text):
        btn = QPushButton(text)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setMinimumHeight(44)
        btn.setObjectName("menuButton")
        return btn

    def tao_content(self):
        content = QFrame()
        content.setObjectName("contentArea")

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.header = self.tao_header()

        self.stack = QStackedWidget()
        self.stack.setObjectName("stackArea")

        self.trang_chu_widget = TrangChuWidget(self.ho_ten, self.vai_tro)
        self.sach_widget = SachWindow()
        self.nguoi_muon_widget = NguoiMuonWindow()
        self.the_loai_widget = TheLoaiWindow()
        self.nha_xuat_ban_widget = NhaXuatBanWindow()
        self.nguoi_dung_widget = NguoiDungWindow()
        self.phieu_muon_widget = PhieuMuonWindow(self.nguoi_dung_id)
        self.phieu_tra_widget = PhieuTraWindow(self.nguoi_dung_id)
        self.phieu_phat_widget = PhieuPhatWindow()
        self.thong_ke_widget = ThongKeWindow()

        self.stack.addWidget(self.trang_chu_widget)      # 0
        self.stack.addWidget(self.sach_widget)           # 1
        self.stack.addWidget(self.nguoi_muon_widget)     # 2
        self.stack.addWidget(self.the_loai_widget)       # 3
        self.stack.addWidget(self.nha_xuat_ban_widget)   # 4
        self.stack.addWidget(self.nguoi_dung_widget)     # 5
        self.stack.addWidget(self.phieu_muon_widget)     # 6
        self.stack.addWidget(self.phieu_tra_widget)      # 7
        self.stack.addWidget(self.phieu_phat_widget)     # 8
        self.stack.addWidget(self.thong_ke_widget)       # 9

        layout.addWidget(self.header)
        layout.addWidget(self.stack)

        content.setLayout(layout)
        return content

    def tao_header(self):
        header = QFrame()
        header.setObjectName("topHeader")
        header.setFixedHeight(70)

        layout = QHBoxLayout()
        layout.setContentsMargins(24, 10, 24, 10)

        self.lbl_tieu_de_trang = QLabel("Trang chủ")
        self.lbl_tieu_de_trang.setObjectName("headerTitle")

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        self.lbl_thong_tin = QLabel(f"Người dùng: {self.ho_ten}")
        self.lbl_thong_tin.setObjectName("headerUser")

        layout.addWidget(self.lbl_tieu_de_trang)
        layout.addWidget(spacer)
        layout.addWidget(self.lbl_thong_tin)

        header.setLayout(layout)
        return header

    def mo_quan_ly_tai_khoan(self):
        if self.vai_tro != "quan_tri":
            QMessageBox.warning(
                self,
                "Không có quyền",
                "Chỉ quản trị viên mới được truy cập chức năng này."
            )
            return
        self.chuyen_trang(5, "Quản lý tài khoản")

    def chuyen_trang(self, index, tieu_de):
        self.stack.setCurrentIndex(index)
        self.lbl_tieu_de_trang.setText(tieu_de)

        widget = self.stack.currentWidget()

        if hasattr(widget, "tai_du_lieu"):
            try:
                widget.tai_du_lieu()
            except Exception:
                pass

        if hasattr(widget, "lam_moi"):
            try:
                widget.lam_moi()
            except Exception:
                pass

        if hasattr(widget, "tai_combo_nguoi_muon"):
            try:
                widget.tai_combo_nguoi_muon()
            except Exception:
                pass

        if hasattr(widget, "tai_danh_sach_sach"):
            try:
                widget.tai_danh_sach_sach()
            except Exception:
                pass

        if hasattr(widget, "tai_danh_sach_phieu_muon"):
            try:
                widget.tai_danh_sach_phieu_muon()
            except Exception:
                pass

        if hasattr(widget, "tai_combo_phieu_muon"):
            try:
                widget.tai_combo_phieu_muon()
            except Exception:
                pass

        if hasattr(widget, "tai_danh_sach_phieu_tra"):
            try:
                widget.tai_danh_sach_phieu_tra()
            except Exception:
                pass

        if hasattr(widget, "tai_danh_sach_phieu_phat"):
            try:
                widget.tai_danh_sach_phieu_phat()
            except Exception:
                pass

    def dang_xuat(self):
        tra_loi = QMessageBox.question(
            self,
            "Xác nhận",
            "Bạn có chắc muốn đăng xuất không?"
        )
        if tra_loi == QMessageBox.Yes:
            self.close()

    def ap_dung_style(self):
        self.setStyleSheet("""
            QMainWindow {
                background: #f4f7fb;
            }

            #sidebar {
                background: #172554;
                border-right: 1px solid #1e3a8a;
            }

            #logoLabel {
                color: white;
                font-size: 24px;
                font-weight: bold;
                padding: 12px;
                background: #1d4ed8;
                border-radius: 12px;
            }

            #userInfo {
                color: #dbeafe;
                font-size: 13px;
                padding: 8px 0 14px 0;
            }

            #menuButton {
                text-align: left;
                padding: 12px 14px;
                font-size: 14px;
                color: white;
                background: transparent;
                border: none;
                border-radius: 10px;
            }

            #menuButton:hover {
                background: #1e40af;
            }

            #contentArea {
                background: #f4f7fb;
            }

            #topHeader {
                background: white;
                border-bottom: 1px solid #dbe3ef;
            }

            #headerTitle {
                font-size: 22px;
                font-weight: bold;
                color: #0f172a;
            }

            #headerUser {
                font-size: 13px;
                color: #475569;
            }

            #pageTitle {
                font-size: 34px;
                font-weight: bold;
                color: #0f172a;
            }

            #pageSubtitle {
                font-size: 16px;
                color: #475569;
            }

            #homeCard {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 18px;
            }

            #cardTitle {
                font-size: 18px;
                font-weight: bold;
                color: #1e293b;
            }

            #cardText {
                font-size: 13px;
                color: #64748b;
            }

            QLabel {
                color: #0f172a;
            }

            QPushButton {
                background: #2563eb;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 14px;
                font-size: 13px;
            }

            QPushButton:hover {
                background: #1d4ed8;
            }

            QLineEdit, QComboBox, QSpinBox, QDateEdit {
                background: white;
                border: 1px solid #cbd5e1;
                border-radius: 8px;
                padding: 8px;
                min-height: 18px;
            }

            QTableWidget {
                background: white;
                border: 1px solid #dbe3ef;
                border-radius: 10px;
                gridline-color: #e2e8f0;
                font-size: 13px;
            }

            QHeaderView::section {
                background: #eaf1fb;
                color: #0f172a;
                padding: 8px;
                border: none;
                border-bottom: 1px solid #dbe3ef;
                font-weight: bold;
            }
        """)