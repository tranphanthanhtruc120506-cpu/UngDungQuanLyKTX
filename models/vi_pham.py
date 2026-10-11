import json
import os
import config
from exceptions import InvalidDataError, DuplicateIdError

# ==========================================
# LỚP ĐỐI TƯỢNG (MODEL): VI PHẠM
# ==========================================
class ViPham:
    def __init__(self, ma_vp, ma_sv, noi_dung, ngay, muc_phat=0):
        self.__ma_vp = ma_vp
        self.__ma_sv = ma_sv
        self.__noi_dung = noi_dung
        self.__ngay = ngay
        self.__muc_phat = muc_phat

    @property
    def ma_vp(self): return self.__ma_vp
    
    @property
    def ma_sv(self): return self.__ma_sv

    @property
    def noi_dung(self): return self.__noi_dung

    @property
    def ngay(self): return self.__ngay

    @property
    def muc_phat(self): return self.__muc_phat

    @muc_phat.setter
    def muc_phat(self, value):
        if value < 0:
            raise InvalidDataError("Mức phạt không được là số âm!")
        self.__muc_phat = value

    def to_dict(self):
        return {
            "ma_vp": self.__ma_vp,
            "ma_sv": self.__ma_sv,
            "noi_dung": self.__noi_dung,
            "ngay": self.__ngay,
            "muc_phat": self.__muc_phat
        }