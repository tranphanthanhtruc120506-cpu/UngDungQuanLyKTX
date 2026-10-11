"""Kiểm thử QuanLyViPham (B3). Chạy: python -m unittest tests.test_quan_ly_vi_pham -v"""
import os
import tempfile
import unittest

from exceptions import DuplicateIdError, InvalidDataError, NotFoundError
from managers.quan_ly_sinh_vien import QuanLySinhVien
from managers.quan_ly_vi_pham import QuanLyViPham
from models.sinh_vien import SinhVien
from models.vi_pham import ViPham
from storage.json_storage import JsonStorage


def tao_storage(thu_muc, ten_file):
    return JsonStorage(os.path.join(thu_muc, ten_file), mac_dinh=[],
                       thu_muc_backup=os.path.join(thu_muc, "backup"))


def tao_vp(ma_vp, ma_sv, ngay, muc_phat=0):
    return ViPham(ma_vp, ma_sv, "Về muộn sau 23h", ngay, muc_phat)


class TestQuanLyViPham(unittest.TestCase):
    def setUp(self):
        tam = tempfile.TemporaryDirectory()
        self.addCleanup(tam.cleanup)
        self.ql_sv = QuanLySinhVien(tao_storage(tam.name, "sinhvien.json"))
        self.ql_sv.them(SinhVien("2100000001", "Nguyễn Văn An", "15/03/2005", "0912345678", "DH21CNTT"))
        self.ql_sv.them(SinhVien("2100000002", "Lý Mỹ Linh", "20/07/2005", "0987654321", "DH21KT"))
        self.storage_vp = tao_storage(tam.name, "vipham.json")
        self.ql = QuanLyViPham(self.storage_vp, self.ql_sv)

    # ---- _truoc_khi_them ----
    def test_them_vi_pham_hop_le(self):
        self.ql.them(tao_vp("VP0001", "2100000001", "01/10/2025", 50000))
        self.assertEqual(len(self.ql.lay_tat_ca()), 1)

    def test_them_vi_pham_cua_sv_khong_ton_tai_nem_NotFoundError(self):
        with self.assertRaises(NotFoundError):
            self.ql.them(tao_vp("VP0001", "2199999999", "01/10/2025"))
        self.assertEqual(self.ql.lay_tat_ca(), [])     # không bị thêm

    def test_them_trung_ma_nem_DuplicateIdError(self):
        self.ql.them(tao_vp("VP0001", "2100000001", "01/10/2025"))
        with self.assertRaises(DuplicateIdError):
            self.ql.them(tao_vp("VP0001", "2100000002", "02/10/2025"))

    # ---- sinh_ma ----
    def test_sinh_ma_danh_sach_rong(self):
        self.assertEqual(self.ql.sinh_ma(), "VP0001")

    def test_sinh_ma_lay_so_lon_nhat_cong_1(self):
        self.ql.them(tao_vp("VP0001", "2100000001", "01/10/2025"))
        self.ql.them(tao_vp("VP0003", "2100000001", "02/10/2025"))   # thiếu VP0002
        self.assertEqual(self.ql.sinh_ma(), "VP0004")                # không phải VP0003 (đếm số lượng + 1)

    # ---- lich_su_cua_sv ----
    def test_lich_su_sap_theo_ngay_giam_dan(self):
        self.ql.them(tao_vp("VP0001", "2100000001", "01/10/2025"))
        self.ql.them(tao_vp("VP0002", "2100000001", "05/10/2025"))
        self.ql.them(tao_vp("VP0003", "2100000001", "03/10/2025"))
        self.ql.them(tao_vp("VP0004", "2100000002", "04/10/2025"))   # của SV khác
        ma = [vp.ma for vp in self.ql.lich_su_cua_sv("2100000001")]
        self.assertEqual(ma, ["VP0002", "VP0003", "VP0001"])

    def test_lich_su_sv_chua_vi_pham_tra_list_rong(self):
        self.assertEqual(self.ql.lich_su_cua_sv("2100000002"), [])

    def test_lich_su_sv_khong_ton_tai_nem_NotFoundError(self):
        with self.assertRaises(NotFoundError):
            self.ql.lich_su_cua_sv("2199999999")

    def test_lich_su_ma_rong_nem_InvalidDataError(self):
        with self.assertRaises(InvalidDataError):
            self.ql.lich_su_cua_sv("   ")

    # ---- tong_phat_cua_sv ----
    def test_tong_phat_cong_cac_lan(self):
        self.ql.them(tao_vp("VP0001", "2100000001", "01/10/2025", 50000))
        self.ql.them(tao_vp("VP0002", "2100000001", "02/10/2025", 100000))
        self.ql.them(tao_vp("VP0003", "2100000002", "03/10/2025", 70000))
        self.assertEqual(self.ql.tong_phat_cua_sv("2100000001"), 150000)

    def test_tong_phat_bien_nhac_nho_muc_0_va_chua_vi_pham(self):
        self.ql.them(tao_vp("VP0001", "2100000001", "01/10/2025", 0))
        self.assertEqual(self.ql.tong_phat_cua_sv("2100000001"), 0)   # chỉ bị nhắc nhở
        self.assertEqual(self.ql.tong_phat_cua_sv("2100000002"), 0)   # chưa vi phạm

    def test_tong_phat_sv_khong_ton_tai_nem_NotFoundError(self):
        with self.assertRaises(NotFoundError):
            self.ql.tong_phat_cua_sv("2199999999")

    def test_du_lieu_duoc_luu_va_nap_lai(self):
        self.ql.them(tao_vp("VP0001", "2100000001", "01/10/2025", 50000))
        ql_moi = QuanLyViPham(self.storage_vp, self.ql_sv)
        self.assertEqual(ql_moi.tong_phat_cua_sv("2100000001"), 50000)


if __name__ == "__main__":
    unittest.main()