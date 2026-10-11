"""managers/quan_ly_hop_dong.py - QuanLyHopDong (việc A8, phần 1)."""
import datetime
import re

import config
from exceptions import InvalidDataError
from managers.co_so import QuanLyCoSo
from models.hop_dong import HopDong
from utils.validators import chuan_hoa_ma, doc_ngay


class QuanLyHopDong(QuanLyCoSo):
    LOP_DOI_TUONG = HopDong
    TEN_DOI_TUONG = "hợp đồng"
    TRUONG_MA = "ma_hd"

    def sinh_ma(self):
        """Mã kế tiếp: HD0001, HD0002... (lớn nhất hiện có + 1, nên xóa giữa chừng không sinh trùng)."""
        lon_nhat = 0
        for ma in self._ds:
            m = re.fullmatch(r"HD([0-9]+)", ma)
            if m:
                lon_nhat = max(lon_nhat, int(m.group(1)))
        return f"HD{lon_nhat + 1:04d}"

    def hop_dong_hieu_luc_cua_sv(self, ma_sv, ngay=None):
        """Ngoại lệ có chủ đích: trả None nếu SV không có hợp đồng hiệu lực."""
        ma_sv = chuan_hoa_ma(ma_sv, "ma_sv")
        ngay = datetime.date.today() if ngay is None else doc_ngay(ngay, "ngay")
        con_hieu_luc = [h for h in self._ds.values()
                        if h.ma_sv == ma_sv and h.con_hieu_luc(ngay)]
        if not con_hieu_luc:
            return None
        return max(con_hieu_luc, key=lambda h: h.ngay_bat_dau)

    def sap_het_han(self, ngay=None, so_ngay=None):
        """Hợp đồng sắp hết hạn, sắp theo ngày kết thúc tăng dần."""
        ngay = datetime.date.today() if ngay is None else doc_ngay(ngay, "ngay")
        if so_ngay is None:
            so_ngay = config.SO_NGAY_CANH_BAO_HET_HAN
        elif not isinstance(so_ngay, int) or isinstance(so_ngay, bool) or so_ngay < 0:
            raise InvalidDataError("so_ngay phải là số nguyên không âm", "so_ngay")
        ket_qua = [h for h in self._ds.values() if h.sap_het_han(ngay, so_ngay)]
        return sorted(ket_qua, key=lambda h: (h.ngay_ket_thuc, h.ma))