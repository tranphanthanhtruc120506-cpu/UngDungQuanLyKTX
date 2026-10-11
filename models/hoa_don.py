import json
import os
import config
from exceptions import InvalidDataError, DuplicateIdError

# ==========================================
# LỚP ĐỐI TƯỢNG (MODEL): HÓA ĐƠN
# ==========================================
class HoaDon:
    def __init__(self, ma_hd, ma_phong, thang, so_dien_cu, so_dien_moi, so_nuoc_cu, so_nuoc_moi, phi_o, da_thanh_toan=False):
        self.__ma_hd = ma_hd
        self.__ma_phong = ma_phong
        self.__thang = thang
        
        # Kiểm tra tính hợp lệ của số điện nước
        if so_dien_moi < so_dien_cu or so_nuoc_moi < so_nuoc_cu:
            raise InvalidDataError("Số mới không được nhỏ hơn số cũ!")
            
        self.__so_dien_cu = so_dien_cu
        self.__so_dien_moi = so_dien_moi
        self.__so_nuoc_cu = so_nuoc_cu
        self.__so_nuoc_moi = so_nuoc_moi
        self.__phi_o = phi_o
        self.__da_thanh_toan = da_thanh_toan

    @property
    def ma_hd(self): return self.__ma_hd
    
    @property
    def ma_phong(self): return self.__ma_phong
    
    @property
    def da_thanh_toan(self): return self.__da_thanh_toan

    def danh_dau_thanh_toan(self):
        self.__da_thanh_toan = True

    # Các hàm tính toán
    def tinh_tien_dien(self):
        return (self.__so_dien_moi - self.__so_dien_cu) * config.DON_GIA_DIEN

    def tinh_tien_nuoc(self):
        return (self.__so_nuoc_moi - self.__so_nuoc_cu) * config.DON_GIA_NUOC

    def tong_tien(self):
        return self.__phi_o + self.tinh_tien_dien() + self.tinh_tien_nuoc()

    def to_dict(self):
        return {
            "ma_hd": self.__ma_hd,
            "ma_phong": self.__ma_phong,
            "thang": self.__thang,
            "so_dien_cu": self.__so_dien_cu,
            "so_dien_moi": self.__so_dien_moi,
            "so_nuoc_cu": self.__so_nuoc_cu,
            "so_nuoc_moi": self.__so_nuoc_moi,
            "phi_o": self.__phi_o,
            "da_thanh_toan": self.__da_thanh_toan,
            "tong_tien": self.tong_tien() # Lưu thêm tổng tiền để dễ hiển thị
        }