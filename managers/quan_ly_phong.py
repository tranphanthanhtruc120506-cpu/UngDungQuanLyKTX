import json
import os
import config
from exceptions import InvalidDataError, DuplicateIdError
from models.phong import Phong, PhongMayLanh

class QuanLyPhong:
    def __init__(self):
        self.file_path = config.FILE_PHONG
        self.danh_sach_phong = []
        self.doc_file()

    def doc_file(self):
        if not os.path.exists(self.file_path):
            return
            
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data:
                    # Phân loại để khởi tạo đúng đối tượng (Phòng thường hay Máy lạnh)
                    if item.get("loai") == config.LOAI_MAY_LANH:
                        p = PhongMayLanh(item['ma_phong'], item['so_cho'], item['gia_co_ban'])
                    else:
                        p = Phong(item['ma_phong'], item['so_cho'], item['gia_co_ban'])
                    
                    # Nạp danh sách sinh viên đang ở vào phòng
                    for ma_sv in item.get('danh_sach_sv', []):
                        p.them_sv(ma_sv)
                        
                    self.danh_sach_phong.append(p)
        except Exception as e:
            print(f"Lỗi đọc file phòng: {e}")

    def ghi_file(self):
        try:
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            with open(self.file_path, 'w', encoding='utf-8') as f:
                # Gọi to_dict() của từng phòng (tự động phân biệt phòng thường/máy lạnh)
                data = [p.to_dict() for p in self.danh_sach_phong]
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Lỗi ghi file phòng: {e}")

    def them_phong(self, phong):
        for p in self.danh_sach_phong:
            if p.ma_phong == phong.ma_phong:
                raise DuplicateIdError("Mã phòng đã tồn tại!")
        self.danh_sach_phong.append(phong)
        self.ghi_file()

    def tim_phong(self, ma_phong):
        for p in self.danh_sach_phong:
            if p.ma_phong == ma_phong:
                return p
        return None
        
    def them_sv_vao_phong(self, ma_phong, ma_sv):
        phong = self.tim_phong(ma_phong)
        if phong:
            phong.them_sv(ma_sv)
            self.ghi_file() # Ghi lại vào file json ngay sau khi thêm
        else:
            raise InvalidDataError("Không tìm thấy phòng!")

    def thong_ke_phong(self):
        # Tính toán thống kê cơ bản dùng cho biểu đồ sau này
        tong_phong = len(self.danh_sach_phong)
        so_phong_day = sum(1 for p in self.danh_sach_phong if len(p.danh_sach_sv) >= p.so_cho)
        so_phong_trong = tong_phong - so_phong_day
        return {
            "tong_phong": tong_phong,
            "so_phong_day": so_phong_day,
            "so_phong_trong": so_phong_trong
        }