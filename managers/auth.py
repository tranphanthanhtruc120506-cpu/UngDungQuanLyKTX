import json
import os
import config
from exceptions import InvalidDataError
from models.tai_khoan import TaiKhoan 

class AuthService:
    def __init__(self):
        self.file_path = config.FILE_TAI_KHOAN
        self.danh_sach_tk = []
        self.tai_khoan_hien_tai = None
        self.doc_file()
        
        if len(self.danh_sach_tk) == 0:
            admin = TaiKhoan("admin", "admin123", config.VAI_TRO_ADMIN)
            self.danh_sach_tk.append(admin)
            self.ghi_file()

    def doc_file(self):
        if not os.path.exists(self.file_path):
            return
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data:
                    tk = TaiKhoan(item['username'], item['mat_khau'], item['vai_tro'], item.get('ma_sv'))
                    self.danh_sach_tk.append(tk)
        except Exception as e:
            print(f"Loi doc file tai khoan: {e}") # ĐÃ BỎ DẤU TIẾNG VIỆT

    def ghi_file(self):
        try:
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            with open(self.file_path, 'w', encoding='utf-8') as f:
                data = [tk.to_dict() for tk in self.danh_sach_tk]
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Loi ghi file tai khoan: {e}")

    def dang_nhap(self, username, mat_khau):
        for tk in self.danh_sach_tk:
            if tk.username == username and tk.kiem_tra_mat_khau(mat_khau):
                self.tai_khoan_hien_tai = tk
                return True
        raise InvalidDataError("Tên đăng nhập hoặc mật khẩu không đúng!")

    def dang_xuat(self):
        self.tai_khoan_hien_tai = None

    def la_admin(self):
        if self.tai_khoan_hien_tai is not None:
            return self.tai_khoan_hien_tai.vai_tro == config.VAI_TRO_ADMIN
        return False