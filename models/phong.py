"""models/phong.py - Lớp trừu tượng Phong và hai lớp con (việc A4).

Kỹ thuật OOP thể hiện trong file này:
  * Trừu tượng : Phong kế thừa ABC, tinh_phi_o() là @abstractmethod.
  * Đóng gói   : __ma_phong, __gia_co_ban, __danh_sach_sv là private;
                 _so_cho là protected; truy cập qua @property + setter có kiểm tra.
  * Kế thừa    : PhongThuong, PhongMayLanh kế thừa Phong.
  * Đa hình    : cùng gọi tinh_phi_o() nhưng mỗi loại phòng ra phí khác nhau.
  * Ghi đè     : hai lớp con viết lại tinh_phi_o().

Theo HOPDONG_LOI mục 4.2: tầng này không print, không input;
lỗi nghiệp vụ luôn là KtxError (InvalidDataError, DuplicateIdError, ...).
"""
from abc import ABC, abstractmethod

import config
from exceptions import (InvalidDataError, DuplicateIdError,
                        NotFoundError, RoomFullError)
from utils.validators import chuan_hoa_ma, hop_le_ma_phong, hop_le_ma_sv

# Giả định của nhóm: một phòng có 1..12 chỗ (ghi vào báo cáo).
SO_CHO_TOI_THIEU = 1
SO_CHO_TOI_DA = getattr(config, "SO_CHO_TOI_DA", 12)


def _la_so_nguyen(value):
    """int thật sự. isinstance(True, int) là True nên phải loại bool."""
    return isinstance(value, int) and not isinstance(value, bool)


class Phong(ABC):
    """Lớp trừu tượng: không tạo trực tiếp được (Phong(...) -> TypeError)."""

    LOAI = ""   # thuộc tính lớp; lớp con gán "thuong" / "maylanh"

    def __init__(self, ma_phong, so_cho, gia_co_ban, danh_sach_sv=None):
        self.__ma_phong = self.__kiem_tra_ma_phong(ma_phong)   # private
        self.__danh_sach_sv = []          # private, chỉ đổi qua them_sv / bo_sv
        self._so_cho = SO_CHO_TOI_THIEU   # protected, gán lại qua setter
        self.__gia_co_ban = 0             # private, gán lại qua setter
        self.so_cho = so_cho              # setter có kiểm tra
        self.gia_co_ban = gia_co_ban      # setter có kiểm tra
        self.__nap_danh_sach_sv(danh_sach_sv)

    # ---------- kiểm tra dữ liệu (dùng chung cho constructor, setter, cap_nhat) ----------
    @staticmethod
    def __kiem_tra_ma_phong(ma_phong):
        ma = chuan_hoa_ma(ma_phong, "ma_phong")
        if not hop_le_ma_phong(ma):
            raise InvalidDataError(
                "Mã phòng phải gồm 1 chữ cái A-D và 3 chữ số (ví dụ A101)", "ma_phong")
        return ma

    @staticmethod
    def __kiem_tra_ma_sv(ma_sv):
        ma = chuan_hoa_ma(ma_sv, "ma_sv")
        if not hop_le_ma_sv(ma):
            raise InvalidDataError("Mã sinh viên phải gồm đúng 10 chữ số", "ma_sv")
        return ma

    @staticmethod
    def __kiem_tra_so_cho(value):
        if not _la_so_nguyen(value) or not (SO_CHO_TOI_THIEU <= value <= SO_CHO_TOI_DA):
            raise InvalidDataError(
                f"Số chỗ phải là số nguyên từ {SO_CHO_TOI_THIEU} đến {SO_CHO_TOI_DA}",
                "so_cho")
        return value

    @staticmethod
    def __kiem_tra_gia(value):
        if not _la_so_nguyen(value) or value < 0:
            raise InvalidDataError("Giá cơ bản phải là số nguyên không âm", "gia_co_ban")
        return value

    def __kiem_tra_so_cho_voi_nguoi_o(self, so_cho):
        dang_o = len(self.__danh_sach_sv)
        if so_cho < dang_o:
            raise InvalidDataError(
                f"Phòng đang có {dang_o} người, không thể giảm xuống {so_cho} chỗ",
                "so_cho")

    def __nap_danh_sach_sv(self, danh_sach_sv):
        """Nạp danh sách ban đầu (đọc từ file). Sai thì báo InvalidDataError."""
        if danh_sach_sv is None:
            return
        if isinstance(danh_sach_sv, (str, bytes)) or not hasattr(danh_sach_sv, "__iter__"):
            raise InvalidDataError("danh_sach_sv phải là một danh sách", "danh_sach_sv")
        for ma in danh_sach_sv:
            ma = self.__kiem_tra_ma_sv(ma)
            if ma in self.__danh_sach_sv:
                raise InvalidDataError(f"Sinh viên {ma} bị lặp trong phòng", "danh_sach_sv")
            if len(self.__danh_sach_sv) >= self._so_cho:
                raise InvalidDataError(
                    f"Số sinh viên vượt quá số chỗ ({self._so_cho})", "danh_sach_sv")
            self.__danh_sach_sv.append(ma)

    # ---------- property ----------
    @property
    def ma(self):
        return self.__ma_phong

    @property
    def ma_phong(self):
        return self.__ma_phong            # cùng giá trị với ma, không có setter

    @property
    def so_cho(self):
        return self._so_cho

    @so_cho.setter
    def so_cho(self, value):
        self.__kiem_tra_so_cho(value)
        self.__kiem_tra_so_cho_voi_nguoi_o(value)
        self._so_cho = value

    @property
    def gia_co_ban(self):
        return self.__gia_co_ban

    @gia_co_ban.setter
    def gia_co_ban(self, value):
        self.__gia_co_ban = self.__kiem_tra_gia(value)

    @property
    def loai(self):
        return self.LOAI

    @property
    def danh_sach_sv(self):
        return tuple(self.__danh_sach_sv)  # chỉ đọc: append() từ ngoài không được

    # ---------- nghiệp vụ ----------
    def con_cho(self):
        return self._so_cho - len(self.__danh_sach_sv)

    def da_day(self):
        return self.con_cho() <= 0

    la_day = da_day   # tên la_day() trong sơ đồ lớp

    def co_sv(self, ma_sv):
        try:
            ma = self.__kiem_tra_ma_sv(ma_sv)
        except InvalidDataError:
            return False
        return ma in self.__danh_sach_sv

    def them_sv(self, ma_sv):
        """Thứ tự kiểm tra: mã hợp lệ -> đã trong phòng -> hết chỗ."""
        ma = self.__kiem_tra_ma_sv(ma_sv)
        if ma in self.__danh_sach_sv:
            raise DuplicateIdError(
                f"Sinh viên {ma} đã ở trong phòng {self.ma_phong}", "ma_sv")
        if self.da_day():
            raise RoomFullError(
                f"Phòng {self.ma_phong} đã hết chỗ ({len(self.__danh_sach_sv)}/{self._so_cho})")
        self.__danh_sach_sv.append(ma)

    def bo_sv(self, ma_sv):
        ma = self.__kiem_tra_ma_sv(ma_sv)
        if ma not in self.__danh_sach_sv:
            raise NotFoundError(
                f"Sinh viên {ma} không ở trong phòng {self.ma_phong}", "ma_sv")
        self.__danh_sach_sv.remove(ma)

    @abstractmethod
    def tinh_phi_o(self):
        """Mỗi loại phòng tự quy định cách tính phí ở (trả int, đơn vị đồng)."""

    # ---------- sửa / lưu ----------
    def cap_nhat(self, so_cho=None, gia_co_ban=None):
        """Kiểm tra hết rồi mới gán: sai một trường thì không đổi trường nào."""
        if so_cho is None and gia_co_ban is None:
            raise InvalidDataError("Không có thông tin nào để cập nhật")
        if so_cho is not None:
            self.__kiem_tra_so_cho(so_cho)
            self.__kiem_tra_so_cho_voi_nguoi_o(so_cho)
        if gia_co_ban is not None:
            self.__kiem_tra_gia(gia_co_ban)
        if so_cho is not None:
            self._so_cho = so_cho
        if gia_co_ban is not None:
            self.__gia_co_ban = gia_co_ban

    def to_dict(self):
        return {
            "ma_phong": self.ma_phong,
            "loai": self.loai,
            "so_cho": self.so_cho,
            "gia_co_ban": self.gia_co_ban,
            "danh_sach_sv": list(self.__danh_sach_sv),
        }

    @classmethod
    def tu_dict(cls, d):
        """Dựng đúng lớp con theo d["loai"]; loại lạ -> InvalidDataError."""
        return tao_phong(d)

    def __str__(self):
        return (f"{self.ma_phong} - {self.loai} - {len(self.__danh_sach_sv)}/{self.so_cho} chỗ"
                f" - phí ở {self.tinh_phi_o():,} đ")

    def __len__(self):
        return len(self.__danh_sach_sv)   # số người đang ở


class PhongThuong(Phong):
    LOAI = "thuong"

    def tinh_phi_o(self):                 # ghi đè (override)
        return self.gia_co_ban


class PhongMayLanh(Phong):
    LOAI = "maylanh"

    def tinh_phi_o(self):                 # ghi đè: cộng thêm phụ thu máy lạnh
        return self.gia_co_ban + config.PHU_THU_MAY_LANH


# Bảng tra "loai" -> lớp con. Thêm loại phòng mới chỉ cần thêm vào tuple này.
_LOAI_PHONG = {lop.LOAI: lop for lop in (PhongThuong, PhongMayLanh)}


def tao_phong(du_lieu):
    """Factory: chọn lớp con theo du_lieu["loai"] (dùng khi đọc JSON)."""
    if not isinstance(du_lieu, dict):
        raise InvalidDataError("Dữ liệu phòng phải là một dict")
    loai = du_lieu.get("loai")
    lop = _LOAI_PHONG.get(loai) if isinstance(loai, str) else None
    if lop is None:
        raise InvalidDataError(
            f"Loại phòng không hợp lệ: {loai!r} (chỉ có {', '.join(_LOAI_PHONG)})", "loai")
    for khoa in ("ma_phong", "so_cho", "gia_co_ban"):
        if khoa not in du_lieu:
            raise InvalidDataError(f"Thiếu trường {khoa}", khoa)
    return lop(du_lieu["ma_phong"], du_lieu["so_cho"], du_lieu["gia_co_ban"],
               du_lieu.get("danh_sach_sv"))
