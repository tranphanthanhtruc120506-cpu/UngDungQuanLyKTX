import json
import os
import config
from exceptions import InvalidDataError, DuplicateIdError
from models.hoa_don import HoaDon 

class QuanLyHoaDon:
    def __init__(self):
        self.file_path = config.FILE_HOA_DON
        self.danh_sach_hd = []
        self.doc_file()

    def doc_file(self):
        if not os.path.exists(self.file_path):
            return
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data:
                    hd = HoaDon(
                        item['ma_hd'], item['ma_phong'], item['thang'],
                        item['so_dien_cu'], item['so_dien_moi'],
                        item['so_nuoc_cu'], item['so_nuoc_moi'],
                        item['phi_o'], item.get('da_thanh_toan', False)
                    )
                    self.danh_sach_hd.append(hd)
        except Exception as e:
            print(f"Loi doc file hoa don: {e}") # ĐÃ BỎ DẤU TIẾNG VIỆT

    def ghi_file(self):
        try:
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            with open(self.file_path, 'w', encoding='utf-8') as f:
                data = [hd.to_dict() for hd in self.danh_sach_hd]
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Loi ghi file hoa don: {e}")

    def lap_hoa_don(self, hd):
        for h in self.danh_sach_hd:
            if h.ma_hd == hd.ma_hd:
                raise DuplicateIdError("Mã hóa đơn đã tồn tại!")
        self.danh_sach_hd.append(hd)
        self.ghi_file()

    def thanh_toan_hoa_don(self, ma_hd):
        for hd in self.danh_sach_hd:
            if hd.ma_hd == ma_hd:
                hd.danh_dau_thanh_toan()
                self.ghi_file()
                return True
        raise InvalidDataError("Không tìm thấy hóa đơn!")

    def tong_cong_no(self):
        tong = 0
        for hd in self.danh_sach_hd:
            if not hd.da_thanh_toan:
                tong += hd.tong_tien()
        return tong