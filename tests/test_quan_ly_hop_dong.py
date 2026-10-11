"""Kiểm thử managers/quan_ly_hop_dong.py (A8).
    python -m unittest tests.test_quan_ly_hop_dong -v
Mọi ngày đều truyền cố định nên kết quả không phụ thuộc ngày chạy.
"""
import datetime

from exceptions import InvalidDataError, DuplicateIdError, NotFoundError, StorageError
from managers.quan_ly_hop_dong import QuanLyHopDong
from models.hop_dong import HopDong
from tests.helpers import TestCoThuMuc

D = datetime.date
SV1, SV2, SV3 = "2100000001", "2100000002", "2100000003"


def hd(ma, sv, phong="A101", bd="01/09/2026", kt="30/06/2027", **kw):
    return HopDong(ma, sv, phong, bd, kt, **kw)


class TestQuanLyHopDong(TestCoThuMuc):
    def setUp(self):
        super().setUp()
        self.st = self.storage()
        self.ql = QuanLyHopDong(self.st)

    # ---- sinh mã ----
    def test_sinh_ma_dau_tien(self):
        self.assertEqual(self.ql.sinh_ma(), "HD0001")

    def test_sinh_ma_tang_dan(self):
        self.ql.them(hd(self.ql.sinh_ma(), SV1))
        self.assertEqual(self.ql.sinh_ma(), "HD0002")
        self.ql.them(hd(self.ql.sinh_ma(), SV2))
        self.assertEqual(self.ql.sinh_ma(), "HD0003")

    def test_sinh_ma_khong_trung_sau_khi_xoa_giua(self):
        for i, sv in enumerate((SV1, SV2, SV3), 1):
            self.ql.them(hd(f"HD{i:04d}", sv))
        self.ql.xoa("HD0002")
        self.assertEqual(self.ql.sinh_ma(), "HD0004")       # không dùng lại HD0002/HD0003

    def test_sinh_ma_khi_ma_dai_hon_4_chu_so(self):
        self.ql.them(hd("HD12345", SV1))
        self.assertEqual(self.ql.sinh_ma(), "HD12346")

    # ---- CRUD cơ bản ----
    def test_them_trung_ma(self):
        self.ql.them(hd("HD0001", SV1))
        with self.assertRaises(DuplicateIdError):
            self.ql.them(hd("HD0001", SV2))

    def test_them_luu_va_nap_lai(self):
        self.ql.them(hd("HD0001", SV1))
        ql2 = QuanLyHopDong(self.storage())
        self.assertEqual(ql2.tim_theo_ma("hd0001").ma_sv, SV1)
        self.assertEqual(ql2.tim_theo_ma("HD0001").ngay_ket_thuc, D(2027, 6, 30))

    def test_sua_ngay_ket_thuc_va_phong(self):
        self.ql.them(hd("HD0001", SV1))
        h = self.ql.sua("HD0001", ngay_ket_thuc="31/07/2027", ma_phong="B202")
        self.assertEqual((h.ngay_ket_thuc, h.ma_phong), (D(2027, 7, 31), "B202"))

    def test_sua_ma_sv_bi_chan(self):
        self.ql.them(hd("HD0001", SV1))
        with self.assertRaises(InvalidDataError):
            self.ql.sua("HD0001", ma_sv=SV2)
        with self.assertRaises(InvalidDataError):
            self.ql.sua("HD0001", ma_hd="HD0009")

    def test_sua_sai_ngay_giu_nguyen(self):
        self.ql.them(hd("HD0001", SV1))
        with self.assertRaises(InvalidDataError):
            self.ql.sua("HD0001", ngay_ket_thuc="01/01/2020")
        self.assertEqual(self.ql.tim_theo_ma("HD0001").ngay_ket_thuc, D(2027, 6, 30))

    def test_xoa_khong_co(self):
        with self.assertRaises(NotFoundError):
            self.ql.xoa("HD9999")

    def test_loi_ghi_file_hoan_tac(self):
        self.st.ghi_loi = True
        with self.assertRaises(StorageError):
            self.ql.them(hd("HD0001", SV1))
        self.assertEqual(len(self.ql), 0)

    def test_tim_theo_tieu_chi(self):
        self.ql.them(hd("HD0001", SV1, "A101"))
        self.ql.them(hd("HD0002", SV2, "B202"))
        self.assertEqual([h.ma for h in self.ql.tim_theo_tieu_chi(ma_phong="b2")], ["HD0002"])
        self.assertEqual([h.ma for h in self.ql.tim_theo_tieu_chi(ma_sv=SV1)], ["HD0001"])
        self.assertEqual([h.ma for h in self.ql.tim_theo_tieu_chi(trang_thai="hieu_luc")],
                         ["HD0001", "HD0002"])

    # ---- hop_dong_hieu_luc_cua_sv ----
    def test_hop_dong_hieu_luc_cua_sv(self):
        self.ql.them(hd("HD0001", SV1))
        self.assertEqual(self.ql.hop_dong_hieu_luc_cua_sv(SV1, D(2026, 12, 1)).ma, "HD0001")

    def test_khong_co_hop_dong_tra_None(self):
        self.ql.them(hd("HD0001", SV1))
        self.assertIsNone(self.ql.hop_dong_hieu_luc_cua_sv(SV2, D(2026, 12, 1)))

    def test_ngoai_khoang_ngay_tra_None(self):
        self.ql.them(hd("HD0001", SV1))
        self.assertIsNone(self.ql.hop_dong_hieu_luc_cua_sv(SV1, D(2026, 8, 31)))   # trước
        self.assertIsNone(self.ql.hop_dong_hieu_luc_cua_sv(SV1, D(2027, 7, 1)))    # sau
        self.assertIsNotNone(self.ql.hop_dong_hieu_luc_cua_sv(SV1, D(2027, 6, 30)))  # biên

    def test_hop_dong_da_ket_thuc_tra_None(self):
        self.ql.them(hd("HD0001", SV1, trang_thai="da_ket_thuc"))
        self.assertIsNone(self.ql.hop_dong_hieu_luc_cua_sv(SV1, D(2026, 12, 1)))

    def test_sv_co_hop_dong_cu_va_moi_lay_cai_dang_hieu_luc(self):
        self.ql.them(hd("HD0001", SV1, "A101", "01/09/2025", "30/06/2026",
                        trang_thai="da_ket_thuc"))
        self.ql.them(hd("HD0002", SV1, "B202"))
        self.assertEqual(self.ql.hop_dong_hieu_luc_cua_sv(SV1, D(2026, 12, 1)).ma, "HD0002")

    def test_hieu_luc_nhan_ngay_chuoi_va_ma_sv_sai(self):
        self.ql.them(hd("HD0001", SV1))
        self.assertIsNotNone(self.ql.hop_dong_hieu_luc_cua_sv(SV1, "01/12/2026"))
        with self.assertRaises(InvalidDataError):
            self.ql.hop_dong_hieu_luc_cua_sv("", D(2026, 12, 1))
        with self.assertRaises(InvalidDataError):
            self.ql.hop_dong_hieu_luc_cua_sv(SV1, "hom nay")

    # ---- sap_het_han ----
    def test_sap_het_han_sap_theo_ngay_ket_thuc_tang_dan(self):
        self.ql.them(hd("HD0001", SV1, kt="30/06/2027"))
        self.ql.them(hd("HD0002", SV2, kt="10/06/2027"))
        self.ql.them(hd("HD0003", SV3, kt="20/06/2027"))
        ket_qua = self.ql.sap_het_han(D(2027, 6, 1))
        self.assertEqual([h.ma for h in ket_qua], ["HD0002", "HD0003", "HD0001"])

    def test_sap_het_han_bien_30_ngay(self):
        self.ql.them(hd("HD0001", SV1, kt="30/06/2027"))
        self.assertEqual(len(self.ql.sap_het_han(D(2027, 5, 31))), 1)   # còn 30 ngày
        self.assertEqual(len(self.ql.sap_het_han(D(2027, 5, 30))), 0)   # còn 31 ngày

    def test_sap_het_han_so_ngay_tuy_chinh(self):
        self.ql.them(hd("HD0001", SV1, kt="30/06/2027"))
        self.assertEqual(len(self.ql.sap_het_han(D(2027, 5, 1), so_ngay=60)), 1)
        self.assertEqual(len(self.ql.sap_het_han(D(2027, 5, 1), so_ngay=10)), 0)

    def test_sap_het_han_bo_qua_hop_dong_da_ket_thuc_va_da_het(self):
        self.ql.them(hd("HD0001", SV1, kt="30/06/2027", trang_thai="da_ket_thuc"))
        self.ql.them(hd("HD0002", SV2, kt="10/06/2027"))
        self.assertEqual(self.ql.sap_het_han(D(2027, 6, 20)), [])

    def test_sap_het_han_rong(self):
        self.assertEqual(self.ql.sap_het_han(D(2027, 6, 1)), [])

    def test_sap_het_han_tham_so_sai(self):
        for v in (-1, "30", 1.5, True):
            with self.subTest(v=v):
                with self.assertRaises(InvalidDataError):
                    self.ql.sap_het_han(D(2027, 6, 1), so_ngay=v)


if __name__ == "__main__":
    import unittest
    unittest.main(verbosity=2)