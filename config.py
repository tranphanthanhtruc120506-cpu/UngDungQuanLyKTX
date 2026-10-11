import os

# Thư mục chứa data
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

# Đường dẫn tới các file JSON
FILE_PHONG = os.path.join(DATA_DIR, "phong.json")
FILE_SINH_VIEN = os.path.join(DATA_DIR, "sinhvien.json")
FILE_HOP_DONG = os.path.join(DATA_DIR, "hopdong.json")
FILE_HOA_DON = os.path.join(DATA_DIR, "hoadon.json")
FILE_VI_PHAM = os.path.join(DATA_DIR, "vipham.json")
FILE_TAI_KHOAN = os.path.join(DATA_DIR, "accounts.json")


LOAI_THUONG = "thuong"
LOAI_MAY_LANH = "maylanh"

# Đơn giá
DON_GIA_DIEN = 3500
DON_GIA_NUOC = 15000
PHU_THU_MAY_LANH = 500000 

# Trạng thái hợp đồng
TT_HIEU_LUC = "hieu_luc"
TT_DA_KET_THUC = "da_ket_thuc"

# Phân quyền
VAI_TRO_ADMIN = "admin"
VAI_TRO_USER = "user"