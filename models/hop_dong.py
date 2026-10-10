"""models/hop_dong.py - Lớp HopDong (việc A5).

Điểm chính:
  * So sánh ngày bằng datetime.date, không so sánh chuỗi "dd/mm/yyyy".
  * Trạng thái chỉ LƯU 2 giá trị: hieu_luc / da_ket_thuc.
    "Hết hạn" được TÍNH từ ngày (tinh_trang_thai), không lưu vào file.
  * Constructor gán qua setter nên tạo mới, sửa và đọc từ file dùng chung một bộ kiểm tra.
  * ngay=None nghĩa là hôm nay; test luôn truyền ngày cố định.
Theo HOPDONG_LOI mục 4.1 và 4.4: không print, không input; lỗi luôn là KtxError.
"""
import datetime

import config
from exceptions import InvalidDataError
from utils.validators import (chuan_hoa_ma, hop_le_ma_hd, hop_le_ma_phong,
                              hop_le_ma_sv, doc_ngay, dinh_dang_ngay)

# Trạng thái được lưu trong file
_TRANG_THAI_HOP_LE = (config.TT_HIEU_LUC, config.TT_DA_KET_THUC)
# Trạng thái tính ra (thêm "het_han")
TT_HET_HAN = "het_han"
# Các trường được phép sửa qua cap_nhat
_TRUONG_SUA_DUOC = ("ngay_ket_thuc", "ma_phong", "trang_thai")


class HopDong:
    def __init__(self, ma_hd, ma_sv, ma_phong, ngay_bat_dau, ngay_ket_thuc,
                 trang_thai=config.TT_HIEU_LUC):
        self.__ma_hd = self.__kiem_tra_ma_hd(ma_hd)           # private, không có setter
        self.__ma_sv = self.__kiem_tra_ma_sv(ma_sv)           # private, không có setter
        self.__ngay_bat_dau = doc_ngay(ngay_bat_dau, "ngay_bat_dau")  # không sửa sau khi tạo
        self.__ma_phong = ""
        self.__ngay_ket_thuc = None
        self.__trang_thai = config.TT_HIEU_LUC
        self.ma_phong = ma_phong                              # các setter dưới đây tự kiểm tra
        self.ngay_ket_thuc = ngay_ket_thuc
        self.trang_thai = trang_thai

    # ---------- kiểm tra dữ liệu (dùng chung cho constructor, setter, cap_nhat) ----------
    @staticmethod
    def __kiem_tra_ma_hd(ma_hd):
        ma = chuan_hoa_ma(ma_hd, "ma_hd")
        if not hop_le_ma_hd(ma):
            raise InvalidDataError("Mã hợp đồng phải có dạng HD kèm ít nhất 4 chữ số "
                                   "(ví dụ HD0001)", "ma_hd")
        return ma

    @staticmethod
    def __kiem_tra_ma_sv(ma_sv):
        ma = chuan_hoa_ma(ma_sv, "ma_sv")
        if not hop_le_ma_sv(ma):
            raise InvalidDataError("Mã sinh viên phải gồm đúng 10 chữ số", "ma_sv")
        return ma

    @staticmethod
    def __kiem_tra_ma_phong(ma_phong):
        ma = chuan_hoa_ma(ma_phong, "ma_phong")
        if not hop_le_ma_phong(ma):
            raise InvalidDataError(
                "Mã phòng phải gồm 1 chữ cái A-D và 3 chữ số (ví dụ A101)", "ma_phong")
        return ma

    def __kiem_tra_ngay_ket_thuc(self, gia_tri):
        ngay = doc_ngay(gia_tri, "ngay_ket_thuc")
        if ngay <= self.__ngay_bat_dau:                       # bằng nhau cũng sai
            raise InvalidDataError("Ngày kết thúc phải sau ngày bắt đầu", "ngay_ket_thuc")
        return ngay

    @staticmethod
    def __kiem_tra_trang_thai(gia_tri):
        if gia_tri not in _TRANG_THAI_HOP_LE:                 # cũng chặn None, số, list...
            raise InvalidDataError(
                f"Trạng thái chỉ có thể là: {', '.join(_TRANG_THAI_HOP_LE)}", "trang_thai")
        return gia_tri

    @staticmethod
    def __hom_nay_neu_none(ngay):
        return datetime.date.today() if ngay is None else doc_ngay(ngay, "ngay")

    # ---------- property ----------
    @property
    def ma(self):
        return self.__ma_hd

    @property
    def ma_hd(self):
        return self.__ma_hd

    @property
    def ma_sv(self):
        return self.__ma_sv

    @property
    def ngay_bat_dau(self):
        return self.__ngay_bat_dau

    @property
    def ma_phong(self):
        return self.__ma_phong

    @ma_phong.setter
    def ma_phong(self, value):
        self.__ma_phong = self.__kiem_tra_ma_phong(value)

    @property
    def ngay_ket_thuc(self):
        return self.__ngay_ket_thuc

    @ngay_ket_thuc.setter
    def ngay_ket_thuc(self, value):
        self.__ngay_ket_thuc = self.__kiem_tra_ngay_ket_thuc(value)

    @property
    def trang_thai(self):
        return self.__trang_thai

    @trang_thai.setter
    def trang_thai(self, value):
        self.__trang_thai = self.__kiem_tra_trang_thai(value)

    # ---------- nghiệp vụ theo ngày ----------
    def con_hieu_luc(self, ngay=None):
        """Đang lưu hieu_luc VÀ bat_dau <= ngay <= ket_thuc (cả hai đầu đều tính)."""
        ngay = self.__hom_nay_neu_none(ngay)
        return (self.__trang_thai == config.TT_HIEU_LUC
                and self.__ngay_bat_dau <= ngay <= self.__ngay_ket_thuc)

    def sap_het_han(self, ngay=None, so_ngay=config.SO_NGAY_CANH_BAO_HET_HAN):
        """Còn hiệu lực và còn 0..so_ngay ngày nữa là hết hạn (đúng ngày hết hạn vẫn tính)."""
        ngay = self.__hom_nay_neu_none(ngay)
        if not self.con_hieu_luc(ngay):
            return False
        con_lai = (self.__ngay_ket_thuc - ngay).days
        return 0 <= con_lai <= so_ngay

    def tinh_trang_thai(self, ngay=None):
        """'da_ket_thuc' nếu đã kết thúc; 'het_han' nếu quá ngày kết thúc; còn lại 'hieu_luc'.
        Lưu ý: hợp đồng đã ký nhưng chưa tới ngày bắt đầu vẫn trả 'hieu_luc'
        (trạng thái đang lưu), dù con_hieu_luc() lúc đó là False."""
        ngay = self.__hom_nay_neu_none(ngay)
        if self.__trang_thai == config.TT_DA_KET_THUC:
            return config.TT_DA_KET_THUC
        if ngay > self.__ngay_ket_thuc:
            return TT_HET_HAN
        return config.TT_HIEU_LUC

    # ---------- thao tác ----------
    def gia_han(self, ngay_ket_thuc_moi):
        if self.__trang_thai == config.TT_DA_KET_THUC:
            raise InvalidDataError("Hợp đồng đã kết thúc, không thể gia hạn", "trang_thai")
        moi = doc_ngay(ngay_ket_thuc_moi, "ngay_ket_thuc")
        if moi <= self.__ngay_ket_thuc:
            raise InvalidDataError(
                "Ngày kết thúc mới phải sau ngày kết thúc hiện tại "
                f"({dinh_dang_ngay(self.__ngay_ket_thuc)})", "ngay_ket_thuc")
        self.__ngay_ket_thuc = moi

    def ket_thuc(self):
        if self.__trang_thai == config.TT_DA_KET_THUC:
            raise InvalidDataError("Hợp đồng đã kết thúc từ trước", "trang_thai")
        self.__trang_thai = config.TT_DA_KET_THUC

    def cap_nhat(self, **kw):
        """Chỉ sửa ngay_ket_thuc, ma_phong, trang_thai. Kiểm tra hết rồi mới gán."""
        if not kw:
            raise InvalidDataError("Không có thông tin nào để cập nhật")
        la = [k for k in kw if k not in _TRUONG_SUA_DUOC]
        if la:
            raise InvalidDataError(
                f"Không được sửa trường: {', '.join(la)} "
                f"(chỉ sửa được {', '.join(_TRUONG_SUA_DUOC)})", la[0])
        moi = {}
        if "ngay_ket_thuc" in kw:
            moi["ngay_ket_thuc"] = self.__kiem_tra_ngay_ket_thuc(kw["ngay_ket_thuc"])
        if "ma_phong" in kw:
            moi["ma_phong"] = self.__kiem_tra_ma_phong(kw["ma_phong"])
        if "trang_thai" in kw:
            moi["trang_thai"] = self.__kiem_tra_trang_thai(kw["trang_thai"])
        if "ngay_ket_thuc" in moi:
            self.__ngay_ket_thuc = moi["ngay_ket_thuc"]
        if "ma_phong" in moi:
            self.__ma_phong = moi["ma_phong"]
        if "trang_thai" in moi:
            self.__trang_thai = moi["trang_thai"]

    # ---------- lưu file ----------
    def to_dict(self):
        return {
            "ma_hd": self.__ma_hd,
            "ma_sv": self.__ma_sv,
            "ma_phong": self.__ma_phong,
            "ngay_bat_dau": dinh_dang_ngay(self.__ngay_bat_dau),
            "ngay_ket_thuc": dinh_dang_ngay(self.__ngay_ket_thuc),
            "trang_thai": self.__trang_thai,
        }

    @classmethod
    def tu_dict(cls, d):
        """Dữ liệu từ file cũng được kiểm tra như nhập tay."""
        if not isinstance(d, dict):
            raise InvalidDataError("Dữ liệu hợp đồng phải là một dict")
        for khoa in ("ma_hd", "ma_sv", "ma_phong", "ngay_bat_dau", "ngay_ket_thuc"):
            if khoa not in d:
                raise InvalidDataError(f"Thiếu trường {khoa}", khoa)
        return cls(d["ma_hd"], d["ma_sv"], d["ma_phong"],
                   d["ngay_bat_dau"], d["ngay_ket_thuc"],
                   d.get("trang_thai", config.TT_HIEU_LUC))

    def __str__(self):
        return (f"{self.__ma_hd}: SV {self.__ma_sv} - phòng {self.__ma_phong} - "
                f"{dinh_dang_ngay(self.__ngay_bat_dau)} đến "
                f"{dinh_dang_ngay(self.__ngay_ket_thuc)} ({self.__trang_thai})")
