"""Kiểm thử managers/quan_ly_hoa_don.py (A8, kèm thống kê A9).
    python -m unittest tests.test_quan_ly_hoa_don -v
"""
from exceptions import InvalidDataError, DuplicateIdError, NotFoundError, StorageError
from managers.quan_ly_hoa_don import QuanLyHoaDon
from models.phong import PhongThuong, PhongMayLanh
from tests.helpers import TestCoThuMuc


class TestQuanLyHoaDon(TestCoThuMuc):
    def setUp(self):
        super().setUp()
        self.st = self.storage()
        self.ql = QuanLyHoaDon(self.st)
        self.a101 = PhongMayLanh("A101", 4, 400000)      # phí ở 600000
        self.b202 = PhongThuong("B202", 4, 300000)       # phí ở 300000

    # ---- lập hóa đơn ----
    def test_lap_thang_dau_voi_so_cu(self):
        h = self.ql.lap_hoa_don(self.a101, "10/2026", 150, 14, so_dien_cu=100, so_nuoc_cu=10)
        self.assertEqual(h.ma, "HDA101202610")
        self.assertEqual((h.phi_o, h.tinh_tien_dien(), h.tinh_tien_nuoc(), h.tong_tien()),
                         (600000, 175000, 60000, 835000))          # khớp tính tay
        self.assertFalse(h.da_thanh_toan)
        self.assertEqual(len(self.ql), 1)

    def test_thang_dau_khong_nhap_so_cu(self):
        with self.assertRaises(InvalidDataError) as ctx:
            self.ql.lap_hoa_don(self.a101, "10/2026", 150, 14)
        self.assertIn("Tháng đầu tiên", str(ctx.exception))
        self.assertEqual(len(self.ql), 0)

    def test_thieu_mot_trong_hai_so_cu(self):
        with self.assertRaises(InvalidDataError):
            self.ql.lap_hoa_don(self.a101, "10/2026", 150, 14, so_dien_cu=100)
        with self.assertRaises(InvalidDataError):
            self.ql.lap_hoa_don(self.a101, "10/2026", 150, 14, so_nuoc_cu=10)

    def test_thang_sau_tu_lay_so_cu_cua_thang_truoc(self):
        self.ql.lap_hoa_don(self.a101, "10/2026", 150, 14, 100, 10)
        h = self.ql.lap_hoa_don(self.a101, "11/2026", 210, 20)
        self.assertEqual((h.so_dien_cu, h.so_nuoc_cu), (150, 14))
        self.assertEqual(h.tinh_tien_dien(), 60 * 3500)

    def test_qua_nam_thang_12_sang_thang_1(self):
        self.ql.lap_hoa_don(self.a101, "12/2026", 150, 14, 100, 10)
        h = self.ql.lap_hoa_don(self.a101, "01/2027", 160, 15)
        self.assertEqual((h.so_dien_cu, h.so_nuoc_cu), (150, 14))

    def test_thang_truoc_cua_phong_khac_khong_dung_duoc(self):
        self.ql.lap_hoa_don(self.a101, "10/2026", 150, 14, 100, 10)
        with self.assertRaises(InvalidDataError):
            self.ql.lap_hoa_don(self.b202, "11/2026", 50, 5)

    def test_nhay_coc_thang_phai_nhap_so_cu(self):
        self.ql.lap_hoa_don(self.a101, "10/2026", 150, 14, 100, 10)
        with self.assertRaises(InvalidDataError):
            self.ql.lap_hoa_don(self.a101, "12/2026", 250, 30)      # thiếu hóa đơn tháng 11

    def test_cung_phong_cung_thang_trung_ma(self):
        self.ql.lap_hoa_don(self.a101, "10/2026", 150, 14, 100, 10)
        with self.assertRaises(DuplicateIdError):
            self.ql.lap_hoa_don(self.a101, "10/2026", 160, 15, 100, 10)
        self.assertEqual(len(self.ql), 1)

    def test_cung_thang_khac_phong_thi_duoc(self):
        self.ql.lap_hoa_don(self.a101, "10/2026", 150, 14, 100, 10)
        self.ql.lap_hoa_don(self.b202, "10/2026", 60, 6, 50, 5)
        self.assertEqual(len(self.ql), 2)

    def test_so_moi_nho_hon_cu(self):
        with self.assertRaises(InvalidDataError):
            self.ql.lap_hoa_don(self.a101, "10/2026", 100, 14, so_dien_cu=120, so_nuoc_cu=10)
        self.assertEqual(len(self.ql), 0)

    def test_so_moi_nho_hon_so_cu_lay_tu_thang_truoc(self):
        self.ql.lap_hoa_don(self.a101, "10/2026", 150, 14, 100, 10)
        with self.assertRaises(InvalidDataError):
            self.ql.lap_hoa_don(self.a101, "11/2026", 140, 20)

    def test_thang_sai_dinh_dang(self):
        for v in ("13/2026", "10-2026", "", None, "1/2026"):
            with self.subTest(v=v):
                with self.assertRaises(InvalidDataError):
                    self.ql.lap_hoa_don(self.a101, v, 150, 14, 100, 10)

    def test_phong_khong_phai_Phong(self):
        for v in ("A101", None, {"ma_phong": "A101"}):
            with self.subTest(v=v):
                with self.assertRaises(InvalidDataError):
                    self.ql.lap_hoa_don(v, "10/2026", 150, 14, 100, 10)

    def test_so_sai_kieu(self):
        for kw in ({"so_dien_moi": "150"}, {"so_nuoc_moi": -1}, {"so_dien_moi": 1.5}):
            args = dict(phong=self.a101, thang="10/2026", so_dien_moi=150, so_nuoc_moi=14,
                        so_dien_cu=100, so_nuoc_cu=10)
            args.update(kw)
            with self.subTest(kw=kw):
                with self.assertRaises(InvalidDataError):
                    self.ql.lap_hoa_don(**args)

    def test_phi_o_duoc_chup_lai_khi_doi_phong_sau_do(self):
        h = self.ql.lap_hoa_don(self.a101, "10/2026", 150, 14, 100, 10)
        self.a101.cap_nhat(gia_co_ban=999999)
        self.assertEqual(h.phi_o, 600000)

    def test_lap_ghi_file_va_nap_lai(self):
        self.ql.lap_hoa_don(self.a101, "10/2026", 150, 14, 100, 10)
        ql2 = QuanLyHoaDon(self.storage())
        self.assertEqual(ql2.tim_theo_ma("hda101202610").tong_tien(), 835000)

    def test_lap_loi_ghi_file_hoan_tac(self):
        self.st.ghi_loi = True
        with self.assertRaises(StorageError):
            self.ql.lap_hoa_don(self.a101, "10/2026", 150, 14, 100, 10)
        self.assertEqual(len(self.ql), 0)

    # ---- thanh toán ----
    def test_danh_dau_da_thanh_toan(self):
        self.ql.lap_hoa_don(self.a101, "10/2026", 150, 14, 100, 10)
        h = self.ql.danh_dau_da_thanh_toan("HDA101202610")
        self.assertTrue(h.da_thanh_toan)
        self.assertTrue(QuanLyHoaDon(self.storage()).tim_theo_ma("HDA101202610").da_thanh_toan)

    def test_thanh_toan_hai_lan(self):
        self.ql.lap_hoa_don(self.a101, "10/2026", 150, 14, 100, 10)
        self.ql.danh_dau_da_thanh_toan("HDA101202610")
        with self.assertRaises(InvalidDataError):
            self.ql.danh_dau_da_thanh_toan("HDA101202610")

    def test_thanh_toan_ma_khong_co(self):
        with self.assertRaises(NotFoundError):
            self.ql.danh_dau_da_thanh_toan("HDZ999202610")

    def test_thanh_toan_loi_ghi_file_hoan_tac(self):
        self.ql.lap_hoa_don(self.a101, "10/2026", 150, 14, 100, 10)
        self.st.ghi_loi = True
        with self.assertRaises(StorageError):
            self.ql.danh_dau_da_thanh_toan("HDA101202610")
        self.assertFalse(self.ql.tim_theo_ma("HDA101202610").da_thanh_toan)

    # ---- lọc: tiêu chí "Lọc đúng" ----
    def _du_lieu_mau(self):
        self.ql.lap_hoa_don(self.a101, "10/2026", 150, 14, 100, 10)   # 835000
        self.ql.lap_hoa_don(self.a101, "11/2026", 200, 20)            # 600000+175000+90000=865000
        self.ql.lap_hoa_don(self.b202, "10/2026", 60, 6, 50, 5)       # 300000+35000+15000=350000
        self.ql.danh_dau_da_thanh_toan("HDA101202610")

    def test_chua_thanh_toan(self):
        self._du_lieu_mau()
        self.assertEqual(sorted(h.ma for h in self.ql.chua_thanh_toan()),
                         ["HDA101202611", "HDB202202610"])

    def test_chua_thanh_toan_theo_phong(self):
        self._du_lieu_mau()
        self.assertEqual([h.ma for h in self.ql.chua_thanh_toan("a101")], ["HDA101202611"])
        self.assertEqual(self.ql.chua_thanh_toan("C303"), [])

    def test_chua_thanh_toan_ma_phong_rong(self):
        with self.assertRaises(InvalidDataError):
            self.ql.chua_thanh_toan("")

    def test_theo_thang(self):
        self._du_lieu_mau()
        self.assertEqual(sorted(h.ma for h in self.ql.theo_thang("10/2026")),
                         ["HDA101202610", "HDB202202610"])
        self.assertEqual(self.ql.theo_thang("12/2026"), [])

    def test_theo_thang_sai_dinh_dang(self):
        for v in ("2026/10", "13/2026", "", None):
            with self.subTest(v=v):
                with self.assertRaises(InvalidDataError):
                    self.ql.theo_thang(v)

    # ---- thống kê ----
    def test_tong_cong_no(self):
        self._du_lieu_mau()
        self.assertEqual(self.ql.tong_cong_no(), 865000 + 350000)
        self.assertEqual(self.ql.tong_cong_no("A101"), 865000)
        self.assertEqual(self.ql.tong_cong_no("C303"), 0)

    def test_cong_no_giam_khi_thanh_toan(self):
        self._du_lieu_mau()
        self.ql.danh_dau_da_thanh_toan("HDB202202610")
        self.assertEqual(self.ql.tong_cong_no(), 865000)

    def test_doanh_thu_chi_tinh_da_thanh_toan(self):
        self._du_lieu_mau()
        self.assertEqual(self.ql.doanh_thu_theo_thang("10/2026"), 835000)   # B202 chưa trả
        self.assertEqual(self.ql.doanh_thu_theo_thang("11/2026"), 0)
        self.ql.danh_dau_da_thanh_toan("HDB202202610")
        self.assertEqual(self.ql.doanh_thu_theo_thang("10/2026"), 835000 + 350000)

    def test_thong_ke_khi_rong(self):
        self.assertEqual(self.ql.tong_cong_no(), 0)
        self.assertEqual(self.ql.doanh_thu_theo_thang("10/2026"), 0)

    def test_doanh_thu_thang_sai_dinh_dang(self):
        with self.assertRaises(InvalidDataError):
            self.ql.doanh_thu_theo_thang("10-2026")

    # ---- sửa / xóa qua lớp nền ----
    def test_sua_so_dien_moi(self):
        self.ql.lap_hoa_don(self.a101, "10/2026", 150, 14, 100, 10)
        h = self.ql.sua("HDA101202610", so_dien_moi=160)
        self.assertEqual(h.tong_tien(), 600000 + 60 * 3500 + 60000)

    def test_khong_sua_duoc_hoa_don_da_thanh_toan(self):
        self.ql.lap_hoa_don(self.a101, "10/2026", 150, 14, 100, 10)
        self.ql.danh_dau_da_thanh_toan("HDA101202610")
        with self.assertRaises(InvalidDataError):
            self.ql.sua("HDA101202610", so_dien_moi=160)

    def test_sua_ma_hoac_phong_bi_chan(self):
        self.ql.lap_hoa_don(self.a101, "10/2026", 150, 14, 100, 10)
        for kw in ({"ma": "HDX"}, {"ma_phong": "B202"}, {"thang": "11/2026"}):
            with self.subTest(kw=kw):
                with self.assertRaises(InvalidDataError):
                    self.ql.sua("HDA101202610", **kw)

    def test_xoa_hoa_don(self):
        self.ql.lap_hoa_don(self.a101, "10/2026", 150, 14, 100, 10)
        self.ql.xoa("HDA101202610")
        self.assertEqual(len(self.ql), 0)

    def test_xoa_roi_lap_lai_duoc(self):
        self.ql.lap_hoa_don(self.a101, "10/2026", 150, 14, 100, 10)
        self.ql.xoa("HDA101202610")
        self.ql.lap_hoa_don(self.a101, "10/2026", 155, 15, 100, 10)
        self.assertEqual(len(self.ql), 1)

    def test_tim_theo_tieu_chi_thang_va_phong(self):
        self._du_lieu_mau()
        r = self.ql.tim_theo_tieu_chi(thang="10/2026", ma_phong="B202")
        self.assertEqual([h.ma for h in r], ["HDB202202610"])
        self.assertEqual(len(self.ql.tim_theo_tieu_chi(da_thanh_toan=False)), 2)


if __name__ == "__main__":
    import unittest
    unittest.main(verbosity=2)