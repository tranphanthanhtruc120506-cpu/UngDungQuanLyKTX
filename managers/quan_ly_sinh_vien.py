"""Quản lý danh sách sinh viên (phần B3, mục 5.3 của Hợp đồng hàm và lỗi).

Toàn bộ phần dùng chung (thêm, xóa, sửa, tìm theo mã, lọc theo tiêu chí,
lưu file) đã có sẵn trong QuanLyCoSo. Lớp này chỉ khai báo "quản lý cái gì"
và bổ sung hàm tim_theo_ten().
"""
from exceptions import InvalidDataError
from managers.co_so import QuanLyCoSo
from models.sinh_vien import SinhVien


class QuanLySinhVien(QuanLyCoSo):
    """Quản lý các đối tượng SinhVien, khóa chính là ma_sv."""

    LOP_DOI_TUONG = SinhVien   # lớp nền dùng để tạo đối tượng khi đọc file
    TEN_DOI_TUONG = "sinh viên"  # dùng trong thông báo lỗi
    TRUONG_MA = "ma_sv"        # tên trường mã, dùng để chặn sửa mã

    def tim_theo_ten(self, tu_khoa):
        """Tìm sinh viên có họ tên chứa từ khóa (tìm tương đối).

        Không phân biệt hoa thường, tìm theo chuỗi con. Ví dụ "aN" tìm ra
        "Nguyễn Văn An". Khoảng trắng thừa ở hai đầu từ khóa được bỏ qua.

        Trả về:
            list các SinhVien khớp (list rỗng nếu không có ai khớp).
            Đây là list mới, sửa nó không ảnh hưởng dữ liệu bên trong.
        Ném lỗi:
            InvalidDataError: từ khóa không phải chuỗi hoặc rỗng.
        """
        if not isinstance(tu_khoa, str):
            raise InvalidDataError("Từ khóa tìm kiếm phải là chuỗi", "tu_khoa")
        tu_khoa = tu_khoa.strip()
        if not tu_khoa:
            raise InvalidDataError("Vui lòng nhập từ khóa tìm kiếm", "tu_khoa")
        # Tái sử dụng bộ lọc của lớp nền (chuỗi: chứa chuỗi con, không phân biệt hoa thường)
        return self.tim_theo_tieu_chi(ho_ten=tu_khoa)