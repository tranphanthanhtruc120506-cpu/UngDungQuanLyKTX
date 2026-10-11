import json
import os
import config
from exceptions import InvalidDataError

# ==========================================
# LỚP ĐỐI TƯỢNG (MODEL): TÀI KHOẢN
# ==========================================
class TaiKhoan:
    def __init__(self, username, mat_khau, vai_tro=config.VAI_TRO_USER, ma_sv=None):
        self.__username = username
        self.__mat_khau = mat_khau
        self.__vai_tro = vai_tro
        self.__ma_sv = ma_sv # Dùng để liên kết tài khoản user với sinh viên

    @property
    def username(self): return self.__username

    @property
    def vai_tro(self): return self.__vai_tro

    @property
    def ma_sv(self): return self.__ma_sv

    # So sánh mật khẩu trực tiếp (đơn giản, dễ giải thích)
    def kiem_tra_mat_khau(self, mat_khau_nhap):
        return self.__mat_khau == mat_khau_nhap
        
    def doi_mat_khau(self, mat_khau_moi):
        if len(mat_khau_moi) < 6:
            raise InvalidDataError("Mật khẩu phải từ 6 ký tự trở lên!")
        self.__mat_khau = mat_khau_moi

    def to_dict(self):
        return {
            "username": self.__username,
            "mat_khau": self.__mat_khau,
            "vai_tro": self.__vai_tro,
            "ma_sv": self.__ma_sv
        }