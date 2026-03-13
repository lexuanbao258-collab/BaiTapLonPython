import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table,
    TableStyle
)


def dang_ky_font_viet():
    danh_sach_font = [
        ("Arial", "C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/arialbd.ttf"),
        ("Tahoma", "C:/Windows/Fonts/tahoma.ttf", "C:/Windows/Fonts/tahomabd.ttf"),
        ("DejaVuSans", "C:/Windows/Fonts/DejaVuSans.ttf", "C:/Windows/Fonts/DejaVuSans-Bold.ttf"),
    ]

    for ten_font, font_thuong, font_dam in danh_sach_font:
        if os.path.exists(font_thuong):
            pdfmetrics.registerFont(TTFont(ten_font, font_thuong))
            if os.path.exists(font_dam):
                pdfmetrics.registerFont(TTFont(f"{ten_font}-Bold", font_dam))
                return ten_font, f"{ten_font}-Bold"
            return ten_font, ten_font

    return "Helvetica", "Helvetica-Bold"


FONT_NAME, FONT_BOLD = dang_ky_font_viet()


def tao_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="TieuDePhieu",
        fontName=FONT_BOLD,
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0f172a"),
        alignment=1,
        spaceAfter=12
    ))

    styles.add(ParagraphStyle(
        name="NoiDungPhieu",
        fontName=FONT_NAME,
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#1e293b")
    ))

    styles.add(ParagraphStyle(
        name="NoiDungDam",
        fontName=FONT_BOLD,
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#0f172a")
    ))

    return styles


def tao_bang(data, col_widths=None):
    bang = Table(data, colWidths=col_widths, repeatRows=1)
    bang.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dbeafe")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ("FONTNAME", (0, 0), (-1, 0), FONT_BOLD),
        ("FONTNAME", (0, 1), (-1, -1), FONT_NAME),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("LEADING", (0, 0), (-1, -1), 14),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("BACKGROUND", (0, 1), (-1, -1), colors.white),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    return bang


def xuat_pdf_phieu_muon(duong_dan_file, thong_tin, chi_tiet):
    styles = tao_styles()
    doc = SimpleDocTemplate(
        duong_dan_file,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm
    )

    story = []
    story.append(Paragraph("PHIẾU MƯỢN SÁCH", styles["TieuDePhieu"]))
    story.append(Spacer(1, 6))

    story.append(Paragraph(f"<b>Mã phiếu:</b> {thong_tin['ma_phieu_muon']}", styles["NoiDungPhieu"]))
    story.append(Paragraph(f"<b>Người mượn:</b> {thong_tin['ho_ten']}", styles["NoiDungPhieu"]))
    story.append(Paragraph(f"<b>Ngày mượn:</b> {thong_tin['ngay_muon']}", styles["NoiDungPhieu"]))
    story.append(Paragraph(f"<b>Ngày hẹn trả:</b> {thong_tin['ngay_hen_tra']}", styles["NoiDungPhieu"]))
    story.append(Paragraph(f"<b>Trạng thái:</b> {thong_tin['trang_thai']}", styles["NoiDungPhieu"]))
    story.append(Spacer(1, 12))

    du_lieu_bang = [["STT", "Mã sách", "Tên sách", "Số lượng"]]
    for i, item in enumerate(chi_tiet, start=1):
        du_lieu_bang.append([str(i), item[0], item[1], str(item[2])])

    story.append(tao_bang(du_lieu_bang, [20 * mm, 30 * mm, 95 * mm, 25 * mm]))
    doc.build(story)


def xuat_pdf_phieu_tra(duong_dan_file, thong_tin, chi_tiet):
    styles = tao_styles()
    doc = SimpleDocTemplate(
        duong_dan_file,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm
    )

    story = []
    story.append(Paragraph("PHIẾU TRẢ SÁCH", styles["TieuDePhieu"]))
    story.append(Spacer(1, 6))

    story.append(Paragraph(f"<b>Mã phiếu trả:</b> {thong_tin['ma_phieu_tra']}", styles["NoiDungPhieu"]))
    story.append(Paragraph(f"<b>Mã phiếu mượn:</b> {thong_tin['ma_phieu_muon']}", styles["NoiDungPhieu"]))
    story.append(Paragraph(f"<b>Người mượn:</b> {thong_tin['ho_ten']}", styles["NoiDungPhieu"]))
    story.append(Paragraph(f"<b>Ngày trả:</b> {thong_tin['ngay_tra']}", styles["NoiDungPhieu"]))
    story.append(Paragraph(f"<b>Số ngày trễ:</b> {thong_tin['so_ngay_tre']}", styles["NoiDungPhieu"]))
    story.append(Spacer(1, 12))

    du_lieu_bang = [["STT", "Tên sách", "Trả", "Hỏng", "Mất", "Ghi chú"]]
    for i, item in enumerate(chi_tiet, start=1):
        du_lieu_bang.append([
            str(i),
            item[0],
            str(item[1]),
            str(item[2]),
            str(item[3]),
            item[4] or ""
        ])

    story.append(tao_bang(du_lieu_bang, [15 * mm, 70 * mm, 20 * mm, 20 * mm, 20 * mm, 45 * mm]))
    doc.build(story)


def xuat_pdf_phieu_phat(duong_dan_file, thong_tin, chi_tiet):
    styles = tao_styles()
    doc = SimpleDocTemplate(
        duong_dan_file,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm
    )

    story = []
    story.append(Paragraph("PHIẾU PHẠT", styles["TieuDePhieu"]))
    story.append(Spacer(1, 6))

    story.append(Paragraph(f"<b>Mã phiếu phạt:</b> {thong_tin['ma_phieu_phat']}", styles["NoiDungPhieu"]))
    story.append(Paragraph(f"<b>Người mượn:</b> {thong_tin['ho_ten']}", styles["NoiDungPhieu"]))
    story.append(Paragraph(f"<b>Mã phiếu mượn:</b> {thong_tin['ma_phieu_muon']}", styles["NoiDungPhieu"]))
    story.append(Paragraph(f"<b>Trạng thái thanh toán:</b> {thong_tin['trang_thai_thanh_toan']}", styles["NoiDungPhieu"]))
    story.append(Paragraph(f"<b>Tổng tiền:</b> {thong_tin['tong_tien']:,} VNĐ", styles["NoiDungDam"]))
    story.append(Spacer(1, 12))

    du_lieu_bang = [["STT", "Lý do", "Số lượng", "Đơn giá", "Thành tiền", "Ghi chú"]]
    for i, item in enumerate(chi_tiet, start=1):
        du_lieu_bang.append([
            str(i),
            item[0],
            str(item[1]),
            f"{item[2]:,}",
            f"{item[3]:,}",
            item[4] or ""
        ])

    story.append(tao_bang(du_lieu_bang, [15 * mm, 35 * mm, 20 * mm, 30 * mm, 30 * mm, 50 * mm]))
    doc.build(story)