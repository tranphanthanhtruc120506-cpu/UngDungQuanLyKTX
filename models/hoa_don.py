"""models/hoa_don.py - Lớp HoaDon (việc A6).

Công thức (HOPDONG_LOI mục 4.5):
    tiền điện = (số điện mới - số điện cũ) x đơn giá điện
    tiền nước = (số nước mới - số nước cũ) x đơn giá nước
    tổng tiền = phí ở + tiền điện + tiền nước          (tất cả là int, đơn vị đồng)

Điểm chính:
  * Mã hóa đơn TỰ SINH từ (phòng, tháng): "HD" + ma_phong + yyyy + mm, ví dụ HDA101202610.
    Nhờ vậy cùng phòng cùng tháng sẽ trùng mã -> tầng quản lý báo DuplicateIdError.
  * Đơn giá điện/nước và phí ở được "chụp lại" (snapshot) lúc lập hóa đơn:
    đổi config về sau không làm đổi hóa đơn cũ.
  * Số mới >= số cũ (bằng nhau nghĩa là không dùng); mọi số là int không âm.
Không print, không input; lỗi nghiệp vụ luôn là InvalidDataError.
"""
import logging
import re

import config
from exceptions import InvalidDataError
from utils.validators import chuan_hoa_ma, hop_le_ma_phong

log = logging.getLogger(__name__)

_MAU_THANG = re.compile(r"(0[1-9]|1[0-2])/([0-9]{4})")
_TRUONG_SUA_DUOC = ("so_dien_cu", "so_dien_moi", "so_nuoc_cu", "so_nuoc_moi", "phi_o")


def _la_so_nguyen(value):
    """int thật sự (loại bool vì isinstance(True, int) là True)."""
    return isinstance(value, int) and not isinstance(value, bool)


class HoaDon:
    def __init__(self, ma_phong, thang, so_dien_cu, so_dien_moi, so_nuoc_cu, so_nuoc_moi,
                 phi_o, da_thanh_toan=False, don_gia_dien=None, don_gia_nuoc=None):
        self.__ma_phong = self.__kiem_tra_ma_phong(ma_phong)       # không đổi sau khi tạo
        self.__thang = self.__kiem_tra_thang(thang)                # không đổi sau khi tạo
        self.__so_dien_cu, self.__so_dien_moi = self.__kiem_tra_cap(
            so_dien_cu, so_dien_moi, "so_dien", "điện")
        self.__so_nuoc_cu, self.__so_nuoc_moi = self.__kiem_tra_cap(
            so_nuoc_cu, so_nuoc_moi, "so_nuoc", "nước")
        self.__phi_o = self.__kiem_tra_tien(phi_o, "phi_o", "Phí ở")
        # snapshot đơn giá: None -> lấy từ config ngay lúc tạo rồi giữ nguyên
        self.__don_gia_dien = self.__kiem_tra_tien(
            config.DON_GIA_DIEN if don_gia_dien is None else don_gia_dien,
            "don_gia_dien", "Đơn giá điện")
        self.__don_gia_nuoc = self.__kiem_tra_tien(
            config.DON_GIA_NUOC if don_gia_nuoc is None else don_gia_nuoc,
            "don_gia_nuoc", "Đơn giá nước")
        if not isinstance(da_thanh_toan, bool):
            raise InvalidDataError("da_thanh_toan phải là True hoặc False", "da_thanh_toan")
        self.__da_thanh_toan = da_thanh_toan

    # ---------- kiểm tra dữ liệu ----------
    @staticmethod
    def __kiem_tra_ma_phong(ma_phong):
        ma = chuan_hoa_ma(ma_phong, "ma_phong")
        if not hop_le_ma_phong(ma):
            raise InvalidDataError(
                "Mã phòng phải gồm 1 chữ cái A-D và 3 chữ số (ví dụ A101)", "ma_phong")
        return ma

    @staticmethod
    def __kiem_tra_thang(thang):
        if not isinstance(thang, str) or not _MAU_THANG.fullmatch(thang.strip()):
            raise InvalidDataError("Tháng phải có dạng mm/yyyy (ví dụ 10/2026)", "thang")
        return thang.strip()

    @staticmethod
    def __kiem_tra_tien(value, truong, ten):
        if not _la_so_nguyen(value) or value < 0:
            raise InvalidDataError(f"{ten} phải là số nguyên không âm", truong)
        return value

    @staticmethod
    def __kiem_tra_cap(cu, moi, truong, ten):
        """Kiểm tra cặp số cũ/mới: cùng là int >= 0 và mới >= cũ."""
        if not _la_so_nguyen(cu) or cu < 0:
            raise InvalidDataError(f"Số {ten} cũ phải là số nguyên không âm", truong + "_cu")
        if not _la_so_nguyen(moi) or moi < 0:
            raise InvalidDataError(f"Số {ten} mới phải là số nguyên không âm", truong + "_moi")
        if moi < cu:
            raise InvalidDataError(
                f"Số {ten} mới ({moi}) không được nhỏ hơn số cũ ({cu})", truong + "_moi")
        return cu, moi

    # ---------- property (chỉ đọc; sửa qua cap_nhat) ----------
    @property
    def ma(self):
        """Mã tự sinh: HD + phòng + yyyy + mm, ví dụ HDA101202610."""
        mm, yyyy = self.__thang.split("/")
        return f"HD{self.__ma_phong}{yyyy}{mm}"

    @property
    def ma_phong(self):
        return self.__ma_phong

    @property
    def thang(self):
        return self.__thang

    @property
    def so_dien_cu(self):
        return self.__so_dien_cu

    @property
    def so_dien_moi(self):
        return self.__so_dien_moi

    @property
    def so_nuoc_cu(self):
        return self.__so_nuoc_cu

    @property
    def so_nuoc_moi(self):
        return self.__so_nuoc_moi

    @property
    def phi_o(self):
        return self.__phi_o

    @property
    def don_gia_dien(self):
        return self.__don_gia_dien

    @property
    def don_gia_nuoc(self):
        return self.__don_gia_nuoc

    @property
    def da_thanh_toan(self):
        return self.__da_thanh_toan

    # ---------- tính tiền ----------
    def tinh_tien_dien(self):
        return (self.__so_dien_moi - self.__so_dien_cu) * self.__don_gia_dien

    def tinh_tien_nuoc(self):
        return (self.__so_nuoc_moi - self.__so_nuoc_cu) * self.__don_gia_nuoc

    def tong_tien(self):
        return self.__phi_o + self.tinh_tien_dien() + self.tinh_tien_nuoc()

    # ---------- thao tác ----------
    def dat_da_thanh_toan(self):
        if self.__da_thanh_toan:
            raise InvalidDataError("Hóa đơn này đã được thanh toán rồi", "da_thanh_toan")
        self.__da_thanh_toan = True

    def cap_nhat(self, **kw):
        """Sửa số điện/nước và phí ở (khi ghi nhầm). Kiểm tra hết rồi mới gán.
        Không sửa mã, phòng, tháng, đơn giá (đã chụp lại) hay trạng thái thanh toán;
        hóa đơn đã thanh toán thì không cho sửa."""
        if not kw:
            raise InvalidDataError("Không có thông tin nào để cập nhật")
        la = [k for k in kw if k not in _TRUONG_SUA_DUOC]
        if la:
            raise InvalidDataError(
                f"Không được sửa trường: {', '.join(la)} "
                f"(chỉ sửa được {', '.join(_TRUONG_SUA_DUOC)})", la[0])
        if self.__da_thanh_toan:
            raise InvalidDataError("Hóa đơn đã thanh toán, không thể sửa", "da_thanh_toan")
        dien = self.__kiem_tra_cap(kw.get("so_dien_cu", self.__so_dien_cu),
                                   kw.get("so_dien_moi", self.__so_dien_moi),
                                   "so_dien", "điện")
        nuoc = self.__kiem_tra_cap(kw.get("so_nuoc_cu", self.__so_nuoc_cu),
                                   kw.get("so_nuoc_moi", self.__so_nuoc_moi),
                                   "so_nuoc", "nước")
        phi_o = self.__kiem_tra_tien(kw.get("phi_o", self.__phi_o), "phi_o", "Phí ở")
        self.__so_dien_cu, self.__so_dien_moi = dien
        self.__so_nuoc_cu, self.__so_nuoc_moi = nuoc
        self.__phi_o = phi_o

    # ---------- lưu file ----------
    def to_dict(self):
        return {
            "ma": self.ma,
            "ma_phong": self.__ma_phong,
            "thang": self.__thang,
            "so_dien_cu": self.__so_dien_cu,
            "so_dien_moi": self.__so_dien_moi,
            "so_nuoc_cu": self.__so_nuoc_cu,
            "so_nuoc_moi": self.__so_nuoc_moi,
            "phi_o": self.__phi_o,
            "don_gia_dien": self.__don_gia_dien,
            "don_gia_nuoc": self.__don_gia_nuoc,
            "tong_tien": self.tong_tien(),          # chỉ để dễ đọc file, tu_dict không tin số này
            "da_thanh_toan": self.__da_thanh_toan,
        }

    @classmethod
    def tu_dict(cls, d):
        """Dữ liệu từ file cũng được kiểm tra như nhập tay; tổng tiền luôn tính lại."""
        if not isinstance(d, dict):
            raise InvalidDataError("Dữ liệu hóa đơn phải là một dict")
        for khoa in ("ma_phong", "thang", "so_dien_cu", "so_dien_moi", "so_nuoc_cu",
                     "so_nuoc_moi", "phi_o", "don_gia_dien", "don_gia_nuoc"):
            if khoa not in d:                       # đơn giá thiếu => không đoán theo config
                raise InvalidDataError(f"Thiếu trường {khoa}", khoa)
        hd = cls(d["ma_phong"], d["thang"], d["so_dien_cu"], d["so_dien_moi"],
                 d["so_nuoc_cu"], d["so_nuoc_moi"], d["phi_o"],
                 d.get("da_thanh_toan", False), d["don_gia_dien"], d["don_gia_nuoc"])
        if "ma" in d and d["ma"] != hd.ma:
            raise InvalidDataError(
                f"Mã {d['ma']!r} không khớp phòng/tháng (phải là {hd.ma})", "ma")
        if "tong_tien" in d and d["tong_tien"] != hd.tong_tien():
            log.warning("Hóa đơn %s: tong_tien lưu %r lệch số tính lại %d, dùng số tính lại",
                        hd.ma, d["tong_tien"], hd.tong_tien())
        return hd

    def __str__(self):
        tt = "đã thanh toán" if self.__da_thanh_toan else "chưa thanh toán"
        return (f"{self.ma}: phòng {self.__ma_phong} tháng {self.__thang} - "
                f"tổng {self.tong_tien():,} đ ({tt})")