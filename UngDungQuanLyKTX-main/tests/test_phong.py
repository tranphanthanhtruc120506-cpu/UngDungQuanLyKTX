"""Kiểm thử models/phong.py. Chạy từ thư mục gốc KTX:
    python -m unittest tests.test_phong -v
"""
import unittest

import config
from exceptions import (InvalidDataError, DuplicateIdError,
                        NotFoundError, RoomFullError)
from models.phong import Phong, PhongThuong, PhongMayLanh, tao_phong

SV1, SV2, SV3, SV4, SV5 = ("2100000001", "2100000002", "2100000003",
                           "2100000004", "2100000005")


class TestTruuTuongVaDaHinh(unittest.TestCase):
    def test_khong_tao_truc_tiep_Phong(self):
        with self.assertRaises(TypeError):
            Phong("A101", 4, 400000)

    def test_phi_o_phong_thuong(self):
        self.assertEqual(PhongThuong("A101", 4, 400000).tinh_phi_o(), 400000)

    def test_phi_o_phong_may_lanh_cong_phu_thu(self):
        self.assertEqual(PhongMayLanh("A102", 4, 400000).tinh_phi_o(),
                         400000 + config.PHU_THU_MAY_LANH)

    def test_da_hinh_cung_gia_khac_phi(self):
        ds = [PhongThuong("A101", 4, 500000), PhongMayLanh("A102", 4, 500000)]
        phi = [p.tinh_phi_o() for p in ds]
        self.assertNotEqual(phi[0], phi[1])
        self.assertEqual(sum(phi), 1200000)

    def test_isinstance(self):
        p = PhongMayLanh("B201", 2, 1)
        self.assertIsInstance(p, Phong)
        self.assertTrue(issubclass(PhongThuong, Phong))


class TestDongGoiVaRangBuoc(unittest.TestCase):
    def test_ma_chuan_hoa(self):
        p = PhongThuong("  a101 ", 4, 1000)
        self.assertEqual(p.ma_phong, "A101")
        self.assertEqual(p.ma, "A101")

    def test_ma_khong_co_setter(self):
        p = PhongThuong("A101", 4, 1000)
        with self.assertRaises(AttributeError):
            p.ma_phong = "A102"

    def test_ma_sai_dinh_dang(self):
        for ma in ("E101", "A1", "AA101", "", "   ", None, 101):
            with self.subTest(ma=ma):
                with self.assertRaises(InvalidDataError):
                    PhongThuong(ma, 4, 1000)

    def test_so_cho_hop_le_bien(self):
        self.assertEqual(PhongThuong("A101", 1, 0).so_cho, 1)
        self.assertEqual(PhongThuong("A101", 12, 0).so_cho, 12)

    def test_so_cho_sai(self):
        for v in (0, -1, 13, 2.5, "4", None, True):
            with self.subTest(so_cho=v):
                with self.assertRaises(InvalidDataError):
                    PhongThuong("A101", v, 1000)

    def test_gia_sai(self):
        for v in (-1, "500", 1.5, None, True):
            with self.subTest(gia=v):
                with self.assertRaises(InvalidDataError):
                    PhongThuong("A101", 4, v)

    def test_gia_bang_0_hop_le(self):
        self.assertEqual(PhongThuong("A101", 4, 0).tinh_phi_o(), 0)

    def test_setter_sai_giu_nguyen_gia_tri(self):
        p = PhongThuong("A101", 4, 1000)
        with self.assertRaises(InvalidDataError) as ctx:
            p.so_cho = -5
        self.assertEqual(ctx.exception.truong, "so_cho")
        self.assertEqual(p.so_cho, 4)

    def test_danh_sach_sv_chi_doc(self):
        p = PhongThuong("A101", 2, 1000)
        p.them_sv(SV1)
        self.assertIsInstance(p.danh_sach_sv, tuple)
        with self.assertRaises(AttributeError):
            p.danh_sach_sv.append(SV2)
        with self.assertRaises(AttributeError):
            p.danh_sach_sv = []

    def test_private_khong_truy_cap_truc_tiep(self):
        p = PhongThuong("A101", 4, 1000)
        with self.assertRaises(AttributeError):
            p.__gia_co_ban


class TestThemBoSinhVien(unittest.TestCase):
    def setUp(self):
        self.p = PhongThuong("A101", 2, 400000)

    def test_them_thanh_cong(self):
        self.p.them_sv(SV1)
        self.assertTrue(self.p.co_sv(SV1))
        self.assertEqual(self.p.con_cho(), 1)
        self.assertEqual(len(self.p), 1)

    def test_bien_nguoi_cuoi_cung_roi_het_cho(self):
        self.p.them_sv(SV1)
        self.assertFalse(self.p.da_day())
        self.p.them_sv(SV2)
        self.assertTrue(self.p.da_day())
        self.assertTrue(self.p.la_day())
        self.assertEqual(self.p.con_cho(), 0)

    def test_phong_day_bao_RoomFullError(self):
        self.p.them_sv(SV1)
        self.p.them_sv(SV2)
        with self.assertRaises(RoomFullError):
            self.p.them_sv(SV3)
        self.assertEqual(len(self.p), 2)

    def test_trung_sv_bao_DuplicateIdError(self):
        self.p.them_sv(SV1)
        with self.assertRaises(DuplicateIdError):
            self.p.them_sv(SV1)

    def test_thu_tu_kiem_tra_trung_truoc_het_cho(self):
        self.p.them_sv(SV1)
        self.p.them_sv(SV2)           # phòng đầy
        with self.assertRaises(DuplicateIdError):   # trùng được kiểm tra trước
            self.p.them_sv(SV1)

    def test_ma_sv_sai_dinh_dang(self):
        for ma in ("123", "abcdefghij", "", None, 2100000001):
            with self.subTest(ma=ma):
                with self.assertRaises(InvalidDataError):
                    self.p.them_sv(ma)

    def test_bo_sv(self):
        self.p.them_sv(SV1)
        self.p.bo_sv(SV1)
        self.assertFalse(self.p.co_sv(SV1))
        self.assertEqual(self.p.con_cho(), 2)

    def test_bo_sv_khong_o_phong_bao_NotFoundError(self):
        with self.assertRaises(NotFoundError):
            self.p.bo_sv(SV5)

    def test_co_sv_ma_sai_tra_False_khong_nem_loi(self):
        self.assertFalse(self.p.co_sv("abc"))
        self.assertFalse(self.p.co_sv(None))


class TestCapNhat(unittest.TestCase):
    def test_cap_nhat_hop_le(self):
        p = PhongThuong("A101", 4, 400000)
        p.cap_nhat(so_cho=6, gia_co_ban=450000)
        self.assertEqual((p.so_cho, p.gia_co_ban), (6, 450000))

    def test_giam_so_cho_thap_hon_nguoi_o(self):
        p = PhongThuong("A101", 4, 400000)
        for ma in (SV1, SV2, SV3):
            p.them_sv(ma)
        with self.assertRaises(InvalidDataError):
            p.cap_nhat(so_cho=2)
        self.assertEqual(p.so_cho, 4)

    def test_giam_dung_bang_so_nguoi_o_la_duoc(self):
        p = PhongThuong("A101", 4, 400000)
        for ma in (SV1, SV2, SV3):
            p.them_sv(ma)
        p.cap_nhat(so_cho=3)
        self.assertTrue(p.da_day())

    def test_tat_ca_hoac_khong_gi(self):
        p = PhongThuong("A101", 4, 400000)
        with self.assertRaises(InvalidDataError):
            p.cap_nhat(so_cho=6, gia_co_ban=-1)   # giá sai -> số chỗ cũng không đổi
        self.assertEqual((p.so_cho, p.gia_co_ban), (4, 400000))

    def test_cap_nhat_khong_co_gi(self):
        with self.assertRaises(InvalidDataError):
            PhongThuong("A101", 4, 400000).cap_nhat()


class TestToDictVaTuDict(unittest.TestCase):
    def test_to_dict_co_khoa_loai(self):
        p = PhongMayLanh("A101", 4, 400000)
        p.them_sv(SV1)
        self.assertEqual(p.to_dict(), {
            "ma_phong": "A101", "loai": "maylanh", "so_cho": 4,
            "gia_co_ban": 400000, "danh_sach_sv": [SV1]})

    def test_vong_tron_to_dict_tu_dict(self):
        p = PhongThuong("B202", 6, 350000)
        p.them_sv(SV1)
        p.them_sv(SV2)
        q = Phong.tu_dict(p.to_dict())
        self.assertIsInstance(q, PhongThuong)
        self.assertEqual(q.to_dict(), p.to_dict())

    def test_tu_dict_chon_dung_lop_con(self):
        d = {"ma_phong": "A101", "loai": "maylanh", "so_cho": 4,
             "gia_co_ban": 400000, "danh_sach_sv": []}
        self.assertIsInstance(tao_phong(d), PhongMayLanh)
        d["loai"] = "thuong"
        self.assertIsInstance(Phong.tu_dict(d), PhongThuong)

    def test_tu_dict_loai_la(self):
        with self.assertRaises(InvalidDataError) as ctx:
            Phong.tu_dict({"ma_phong": "A101", "loai": "vip",
                           "so_cho": 4, "gia_co_ban": 1})
        self.assertEqual(ctx.exception.truong, "loai")

    def test_tu_dict_thieu_truong_hoac_sai_kieu(self):
        for d in ({"loai": "thuong"}, None, [], "A101",
                  {"ma_phong": "A101", "loai": "thuong", "so_cho": 4}):
            with self.subTest(d=d):
                with self.assertRaises(InvalidDataError):
                    Phong.tu_dict(d)

    def test_tu_dict_file_bi_sua_tay(self):
        base = {"ma_phong": "A101", "loai": "thuong", "so_cho": 2, "gia_co_ban": 1}
        for bat_thuong in ({"danh_sach_sv": [SV1, SV1]},             # trùng
                           {"danh_sach_sv": [SV1, SV2, SV3]},        # quá chỗ
                           {"danh_sach_sv": ["abc"]},                # mã sai
                           {"danh_sach_sv": "2100000001"},           # không phải list
                           {"so_cho": "hai"}):
            with self.subTest(bat_thuong=bat_thuong):
                with self.assertRaises(InvalidDataError):
                    Phong.tu_dict({**base, **bat_thuong})

    def test_str(self):
        s = str(PhongMayLanh("A102", 4, 400000))
        self.assertIn("A102", s)
        self.assertIn("600,000", s)


if __name__ == "__main__":
    unittest.main(verbosity=2)