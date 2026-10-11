import json
import os
import config
from exceptions import InvalidDataError, DuplicateIdError
from models.hop_dong import HopDong

class QuanLyHopDong:
    def __init__(self):
        self.file_path = config.FILE_HOP_DONG
        self.danh_sach_hd = [] # Danh sách chứa các object HopDong
        self.doc_file()

    def doc_file(self):
        if not os.path.exists(self.file_path):
            return
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data:
                    hd = HopDong(
                        item['ma_hd'],
                        item['ma_sv'],
                        item['ma_phong'],
                        item['ngay_bat_dau'],
                        item['ngay_ket_thuc'],
                        item.get('trang_thai', config.TT_HIEU_LUC)
                    )
                    self.danh_sach_hd.append(hd)
        except Exception as e:
            print(f"Lỗi đọc file hợp đồng: {e}")

    def ghi_file(self):
        try:
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            with open(self.file_path, 'w', encoding='utf-8') as f:
                # Chuyển từng object HopDong thành dict để lưu
                data = [hd.to_dict() for hd in self.danh_sach_hd]
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Lỗi ghi file hợp đồng: {e}")

    def them_hop_dong(self, hd):
        # Kiểm tra trùng mã
        for h in self.danh_sach_hd:
            if h.ma_hd == hd.ma_hd:
                raise DuplicateIdError("Mã hợp đồng đã tồn tại!")
        self.danh_sach_hd.append(hd)
        self.ghi_file()

    def xoa_hop_dong(self, ma_hd):
        for hd in self.danh_sach_hd:
            if hd.ma_hd == ma_hd:
                self.danh_sach_hd.remove(hd)
                self.ghi_file()
                return True
        raise InvalidDataError("Không tìm thấy hợp đồng để xóa!")

    def tim_hop_dong(self, ma_hd):
        for hd in self.danh_sach_hd:
            if hd.ma_hd == ma_hd:
                return hd
        return None