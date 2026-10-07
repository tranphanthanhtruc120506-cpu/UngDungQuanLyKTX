"""Hằng số và đường dẫn dùng chung. KHÔNG đặt đường dẫn tuyệt đối ở nơi khác."""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
BACKUP_DIR = os.path.join(DATA_DIR, "backup")

FILE_PHONG = os.path.join(DATA_DIR, "phong.json")
FILE_SINH_VIEN = os.path.join(DATA_DIR, "sinhvien.json")
FILE_HOP_DONG = os.path.join(DATA_DIR, "hopdong.json")
FILE_HOA_DON = os.path.join(DATA_DIR, "hoadon.json")
FILE_VI_PHAM = os.path.join(DATA_DIR, "vipham.json")
FILE_TAI_KHOAN = os.path.join(DATA_DIR, "accounts.json")

# --- Đơn giá giả định của nhóm (đồng, kiểu int) ---
DON_GIA_DIEN = 3500
DON_GIA_NUOC = 15000
PHU_THU_MAY_LANH = 200000

# --- Quy ước giá trị cố định (dùng hằng số, không gõ chuỗi trần trong code) ---
LOAI_THUONG = "thuong"
LOAI_MAY_LANH = "maylanh"
LOAI_PHONG_HOP_LE = (LOAI_THUONG, LOAI_MAY_LANH)

TT_HIEU_LUC = "hieu_luc"
TT_HET_HAN = "het_han"
TT_DA_KET_THUC = "da_ket_thuc"

VAI_TRO_ADMIN = "admin"
VAI_TRO_USER = "user"
VAI_TRO_HOP_LE = (VAI_TRO_ADMIN, VAI_TRO_USER)

# --- Ngưỡng ---
SO_NGAY_CANH_BAO_HET_HAN = 30
MAT_KHAU_TOI_THIEU = 6
PBKDF2_SO_VONG = 200_000

# --- Định dạng ngày ---
DINH_DANG_NGAY = "%d/%m/%Y"     # 31/12/2026
DINH_DANG_THANG = "%m/%Y"       # 12/2026