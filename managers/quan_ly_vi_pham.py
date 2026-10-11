import json
import os
import config
from exceptions import InvalidDataError, DuplicateIdError
from models.vi_pham import ViPham 

class QuanLyViPham:
    def __init__(self):
        self.file_path = config.FILE_VI_PHAM
        self.danh_sach_vp = []
        self.doc_file()

    def doc_file(self):
        if not os.path.exists(self.file_path):
            return
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data:
                    vp = ViPham(item['ma_vp'], item['ma_sv'], item['noi_dung'], item['ngay'], item.get('muc_phat', 0))
                    self.danh_sach_vp.append(vp)
        except Exception as e:
            print(f"Loi doc file vi pham: {e}") # ĐÃ BỎ DẤU TIẾNG VIỆT

    def ghi_file(self):
        try:
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            with open(self.file_path, 'w', encoding='utf-8') as f:
                data = [vp.to_dict() for vp in self.danh_sach_vp]
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Loi ghi file vi pham: {e}")

    def them_vi_pham(self, vp):
        for v in self.danh_sach_vp:
            if v.ma_vp == vp.ma_vp:
                raise DuplicateIdError("Mã vi phạm đã tồn tại!")
        self.danh_sach_vp.append(vp)
        self.ghi_file()

    def tong_phat_cua_sv(self, ma_sv):
        tong = 0
        for vp in self.danh_sach_vp:
            if vp.ma_sv == ma_sv:
                tong += vp.muc_phat
        return tong