import json
import os
import config
from exceptions import InvalidDataError, DuplicateIdError
from models.sinh_vien import SinhVien

class QuanLySinhVien:
    def __init__(self):
        # Lấy đường dẫn file từ config
        self.file_path = config.FILE_SINH_VIEN
        # Dùng List cơ bản để chứa danh sách sinh viên
        self.danh_sach_sv = [] 
        self.doc_file()

    def doc_file(self):
        if not os.path.exists(self.file_path):
            return # Nếu file chưa tồn tại thì bỏ qua
            
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Đọc từng dòng json, tạo đối tượng SinhVien và đưa vào List
                for item in data:
                    sv = SinhVien(
                        item['ma_sv'], 
                        item['ho_ten'], 
                        item['ngay_sinh'], 
                        item['so_dien_thoai'], 
                        item['lop']
                    )
                    self.danh_sach_sv.append(sv)
        except Exception as e:
            print(f"Lỗi đọc file sinh viên: {e}")

    def ghi_file(self):
        try:
            # Tạo thư mục data nếu chưa có
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            with open(self.file_path, 'w', encoding='utf-8') as f:
                # Ép kiểu đối tượng về dạng dict để ghi json
                data = [sv.to_dict() for sv in self.danh_sach_sv]
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Lỗi ghi file sinh viên: {e}")

    def them_sinh_vien(self, sv):
        # Kiểm tra mã sinh viên đã tồn tại chưa bằng vòng lặp
        for s in self.danh_sach_sv:
            if s.ma_sv == sv.ma_sv:
                raise DuplicateIdError("Mã sinh viên đã tồn tại!")
        self.danh_sach_sv.append(sv)
        self.ghi_file()

    def xoa_sinh_vien(self, ma_sv):
        for sv in self.danh_sach_sv:
            if sv.ma_sv == ma_sv:
                self.danh_sach_sv.remove(sv)
                self.ghi_file()
                return True
        raise InvalidDataError("Không tìm thấy sinh viên để xóa!")

    def tim_theo_ten(self, tu_khoa):
        ket_qua = []
        for sv in self.danh_sach_sv:
            # So sánh chuỗi không phân biệt hoa thường
            if tu_khoa.lower() in sv.ho_ten.lower():
                ket_qua.append(sv)
        return ket_qua