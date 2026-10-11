"""managers/quan_ly_hoa_don.py - QuanLyHoaDon (việc A8, phần 2; có sẵn các hàm thống kê của A9).

Mã hóa đơn do HoaDon tự sinh từ (phòng, tháng) nên cùng phòng cùng tháng sẽ trùng mã
và them() tự báo DuplicateIdError, không cần luật riêng.
"""
import copy
import re

from exceptions import InvalidDataError
from managers.co_so import QuanLyCoSo
from models.hoa_don import HoaDon
from models.phong import Phong
from utils.validators import chuan_hoa_ma

_MAU_THANG = re.compile(r"(0[1-9]|1[0-2])/([0-9]{4})")


def _tach_thang(thang):
    """'10/2026' -> (10, 2026); sai định dạng -> InvalidDataError."""
    if not isinstance(thang, str):
        raise InvalidDataError("Tháng phải có dạng mm/yyyy (ví dụ 10/2026)", "thang")
    m = _MAU_THANG.fullmatch(thang.strip())
    if not m:
        raise InvalidDataError("Tháng phải có dạng mm/yyyy (ví dụ 10/2026)", "thang")
    return int(m.group(1)), int(m.group(2))


def _thang_truoc(thang):
    """Tháng liền trước, ví dụ '01/2027' -> '12/2026'."""
    thang_so, nam = _tach_thang(thang)
    if thang_so == 1:
        thang_so, nam = 12, nam - 1
    else:
        thang_so -= 1
    return f"{thang_so:02d}/{nam:04d}"


class QuanLyHoaDon(QuanLyCoSo):
    LOP_DOI_TUONG = HoaDon
    TEN_DOI_TUONG = "hóa đơn"
    TRUONG_MA = "ma"            # mã tự sinh nên trường mã tên là "ma"

    # ---------- lập hóa đơn ----------
    def _hoa_don_thang_truoc(self, ma_phong, thang):
        thang_truoc = _thang_truoc(thang)
        for h in self._ds.values():
            if h.ma_phong == ma_phong and h.thang == thang_truoc:
                return h
        return None

    def lap_hoa_don(self, phong, thang, so_dien_moi, so_nuoc_moi,
                    so_dien_cu=None, so_nuoc_cu=None):
        """phi_o = phong.tinh_phi_o() (chụp lại lúc lập).
        so_*_cu = None -> lấy số mới của hóa đơn tháng liền trước của phòng;
        không có hóa đơn đó -> InvalidDataError('Tháng đầu tiên phải nhập số cũ')."""
        if not isinstance(phong, Phong):
            raise InvalidDataError("phong phải là một đối tượng Phong", "ma_phong")
        _tach_thang(thang)                              # sai định dạng -> báo sớm, đúng trường
        if so_dien_cu is None or so_nuoc_cu is None:
            truoc = self._hoa_don_thang_truoc(phong.ma_phong, thang.strip())
            if truoc is None:
                thieu = "so_dien_cu" if so_dien_cu is None else "so_nuoc_cu"
                raise InvalidDataError("Tháng đầu tiên phải nhập số cũ", thieu)
            if so_dien_cu is None:
                so_dien_cu = truoc.so_dien_moi
            if so_nuoc_cu is None:
                so_nuoc_cu = truoc.so_nuoc_moi
        hoa_don = HoaDon(phong.ma_phong, thang, so_dien_cu, so_dien_moi,
                         so_nuoc_cu, so_nuoc_moi, phong.tinh_phi_o())
        return self.them(hoa_don)                       # trùng (phòng, tháng) -> DuplicateIdError

    def danh_dau_da_thanh_toan(self, ma):
        """NotFound · InvalidDataError (đã thanh toán rồi) · Storage."""
        ban_sao = copy.deepcopy(self.tim_theo_ma(ma))
        ban_sao.dat_da_thanh_toan()
        return self._thay_the(ban_sao)

    # ---------- lọc / tìm ----------
    def _loc_theo_phong(self, ma_phong):
        if ma_phong is None:
            return list(self._ds.values())
        ma_phong = chuan_hoa_ma(ma_phong, "ma_phong")
        return [h for h in self._ds.values() if h.ma_phong == ma_phong]

    def chua_thanh_toan(self, ma_phong=None):
        return [h for h in self._loc_theo_phong(ma_phong) if not h.da_thanh_toan]

    def theo_thang(self, thang):
        _tach_thang(thang)
        thang = thang.strip()
        return [h for h in self._ds.values() if h.thang == thang]

    # ---------- thống kê ----------
    def tong_cong_no(self, ma_phong=None):
        return sum(h.tong_tien() for h in self.chua_thanh_toan(ma_phong))

    def doanh_thu_theo_thang(self, thang):
        """Chỉ tính hóa đơn ĐÃ thanh toán."""
        return sum(h.tong_tien() for h in self.theo_thang(thang) if h.da_thanh_toan)