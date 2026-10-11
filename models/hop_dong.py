from exceptions import InvalidDataError
import config

class HopDong:
    def __init__(self, ma_hd, ma_sv, ma_phong, ngay_bat_dau, ngay_ket_thuc, trang_thai=config.TT_HIEU_LUC):
        self.__ma_hd = ma_hd
        self.__ma_sv = ma_sv
        self.__ma_phong = ma_phong
        self.__ngay_bat_dau = ngay_bat_dau
        self.__ngay_ket_thuc = ngay_ket_thuc
        self.__trang_thai = trang_thai

    @property
    def ma_hd(self):
        return self.__ma_hd

    @property
    def ma_sv(self):
        return self.__ma_sv

    @property
    def ma_phong(self):
        return self.__ma_phong

    @ma_phong.setter
    def ma_phong(self, value):
        if not value.strip():
            raise InvalidDataError("Mã phòng không được để trống!")
        self.__ma_phong = value

    @property
    def ngay_bat_dau(self):
        return self.__ngay_bat_dau

    @property
    def ngay_ket_thuc(self):
        return self.__ngay_ket_thuc

    @ngay_ket_thuc.setter
    def ngay_ket_thuc(self, value):
        self.__ngay_ket_thuc = value

    @property
    def trang_thai(self):
        return self.__trang_thai

    @trang_thai.setter
    def trang_thai(self, value):
        self.__trang_thai = value

    def to_dict(self):
        # Chuyển đối tượng thành Dictionary để lưu file JSON
        return {
            "ma_hd": self.__ma_hd,
            "ma_sv": self.__ma_sv,
            "ma_phong": self.__ma_phong,
            "ngay_bat_dau": self.__ngay_bat_dau,
            "ngay_ket_thuc": self.__ngay_ket_thuc,
            "trang_thai": self.__trang_thai
        }