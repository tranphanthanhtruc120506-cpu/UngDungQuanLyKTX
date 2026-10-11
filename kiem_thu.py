import sys
# Ép Terminal của Windows hiển thị đúng tiếng Việt
sys.stdout.reconfigure(encoding='utf-8')

from managers.quan_ly_sinh_vien import QuanLySinhVien
from managers.quan_ly_phong import QuanLyPhong

# 1. Khởi tạo đối tượng quản lý (Tự động đọc data từ file JSON)
ql_sv = QuanLySinhVien()
ql_phong = QuanLyPhong()

# 2. In thử danh sách sinh viên ra màn hình
print("--- DANH SÁCH SINH VIÊN ---")
for sv in ql_sv.danh_sach_sv:
    print(f"MSSV: {sv.ma_sv} - Họ tên: {sv.ho_ten} - Lớp: {sv.lop}")

# 3. In thử danh sách phòng để test Đa hình
print("\n--- THÔNG TIN PHÒNG ---")
for p in ql_phong.danh_sach_phong:
    print(f"Phòng: {p.ma_phong} - Loại: {p.to_dict().get('loai')} - Phí ở: {p.tinh_phi_o():,} VNĐ")