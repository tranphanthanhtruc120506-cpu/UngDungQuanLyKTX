"""Kiểm thử models/hoa_don.py. Chạy từ thư mục gốc:
    python -m unittest tests.test_hoa_don -v
"""
import json
import unittest
from unittest import mock

import config
from exceptions import InvalidDataError
from models.hoa_don import HoaDon


def tao(**kw):
    tham_so = dict(ma_phong="A101", thang="10/2026", so_dien_cu=100, so_dien_moi=150,
                   so_nuoc_cu=10, so_nuoc_moi=14, phi_o=600000,
                   don_gia_dien=3500, don_gia_nuoc=15000)
    tham_so.update(kw)
    return HoaDon(**tham_so)


class TestTinhTay(unittest.TestCase):
    """Ví dụ kiểm tay trong hợp đồng: máy lạnh 400000 -> phi_o 600000; điện 100->150; nước 10->14."""

    def test_tien_dien(self):
        self.assertEqual(tao().tinh_tien_dien(), 175000)      # 50 x 3500

    def test_tien_nuoc(self):
        self.assertEqual(tao().tinh_tien_nuoc(), 60000)       # 4 x 15000

    def test_tong_tien(self):
        self.assertEqual(tao().tong_tien(), 835000)           # 600000 + 175000 + 60000

    def test_la_int(self):
        h = tao()
        for v in (h.tinh_tien_dien(), h.tinh_tien_nuoc(), h.tong_tien()):
            self.assertIs(type(v), int)

    def test_khong_dung_thi_chi_tinh_phi_o(self):             # moi == cu hợp lệ
        h = tao(so_dien_moi=100, so_nuoc_moi=10)
        self.assertEqual((h.tinh_tien_dien(), h.tinh_tien_nuoc()), (0, 0))
        self.assertEqual(h.tong_tien(), 600000)

    def test_so_bang_0_hop_le(self):
        h = tao(so_dien_cu=0, so_dien_moi=0, so_nuoc_cu=0, so_nuoc_moi=0, phi_o=0)
        self.assertEqual(h.tong_tien(), 0)


class TestMaTuSinh(unittest.TestCase):
    def test_dinh_dang_ma(self):
        self.assertEqual(tao().ma, "HDA101202610")

    def test_ma_chuan_hoa_phong(self):
        self.assertEqual(tao(ma_phong=" b202 ", thang="03/2027").ma, "HDB202202703")

    def test_cung_phong_cung_thang_trung_ma(self):
        self.assertEqual(tao(so_dien_moi=160).ma, tao().ma)

    def test_khac_thang_hoac_phong_thi_khac_ma(self):
        self.assertNotEqual(tao(thang="11/2026").ma, tao().ma)
        self.assertNotEqual(tao(ma_phong="A102").ma, tao().ma)

    def test_khong_co_setter_ma_phong_thang(self):
        h = tao()
        for ten in ("ma", "ma_phong", "thang", "don_gia_dien", "don_gia_nuoc",
                    "so_dien_moi", "phi_o", "da_thanh_toan"):
            with self.subTest(ten=ten):
                with self.assertRaises(AttributeError):
                    setattr(h, ten, 1)


class TestKiemTraDuLieu(unittest.TestCase):
    def test_dien_moi_nho_hon_cu(self):                       # ca 7 của hợp đồng
        with self.assertRaises(InvalidDataError) as ctx:
            tao(so_dien_cu=120, so_dien_moi=100)
        self.assertEqual(ctx.exception.truong, "so_dien_moi")

    def test_nuoc_moi_nho_hon_cu(self):
        with self.assertRaises(InvalidDataError) as ctx:
            tao(so_nuoc_cu=20, so_nuoc_moi=19)
        self.assertEqual(ctx.exception.truong, "so_nuoc_moi")

    def test_so_sai_kieu_hoac_am(self):
        for ten in ("so_dien_cu", "so_dien_moi", "so_nuoc_cu", "so_nuoc_moi", "phi_o"):
            for v in (-1, "10", 1.5, None, True):
                with self.subTest(ten=ten, v=v):
                    with self.assertRaises(InvalidDataError):
                        tao(**{ten: v})

    def test_don_gia_sai(self):
        for ten in ("don_gia_dien", "don_gia_nuoc"):
            for v in (-1, "3500", 1.5, True):
                with self.subTest(ten=ten, v=v):
                    with self.assertRaises(InvalidDataError):
                        tao(**{ten: v})

    def test_thang_sai(self):
        for v in ("13/2026", "00/2026", "1/2026", "10/26", "2026/10", "10-2026",
                  "", None, 102026, "10/2026\n"[:-1] + "x"):
            with self.subTest(v=v):
                with self.assertRaises(InvalidDataError) as ctx:
                    tao(thang=v)
                self.assertEqual(ctx.exception.truong, "thang")

    def test_thang_hop_le_bien(self):
        self.assertEqual(tao(thang="01/2026").ma, "HDA101202601")
        self.assertEqual(tao(thang="12/2026").ma, "HDA101202612")

    def test_ma_phong_sai(self):
        for v in ("Z999", "A1", "", None):
            with self.subTest(v=v):
                with self.assertRaises(InvalidDataError):
                    tao(ma_phong=v)

    def test_da_thanh_toan_phai_la_bool(self):
        for v in ("false", 0, None):
            with self.subTest(v=v):
                with self.assertRaises(InvalidDataError):
                    tao(da_thanh_toan=v)


class TestSnapshotDonGia(unittest.TestCase):
    def test_none_lay_tu_config_luc_tao(self):
        h = HoaDon("A101", "10/2026", 0, 10, 0, 2, 0)
        self.assertEqual((h.don_gia_dien, h.don_gia_nuoc),
                         (config.DON_GIA_DIEN, config.DON_GIA_NUOC))

    def test_doi_config_khong_doi_hoa_don_cu(self):
        h = HoaDon("A101", "10/2026", 0, 10, 0, 2, 0)
        tong_truoc = h.tong_tien()
        with mock.patch.object(config, "DON_GIA_DIEN", config.DON_GIA_DIEN + 1000), \
             mock.patch.object(config, "DON_GIA_NUOC", config.DON_GIA_NUOC + 1000):
            self.assertEqual(h.tong_tien(), tong_truoc)
            moi = HoaDon("A101", "11/2026", 0, 10, 0, 2, 0)
            self.assertGreater(moi.tong_tien(), tong_truoc)

    def test_don_gia_truyen_vao_duoc_uu_tien(self):
        h = tao(don_gia_dien=4000)
        self.assertEqual(h.tinh_tien_dien(), 200000)


class TestThanhToan(unittest.TestCase):
    def test_mac_dinh_chua_thanh_toan(self):
        self.assertFalse(tao().da_thanh_toan)

    def test_dat_da_thanh_toan(self):
        h = tao()
        h.dat_da_thanh_toan()
        self.assertTrue(h.da_thanh_toan)

    def test_thanh_toan_hai_lan(self):
        h = tao()
        h.dat_da_thanh_toan()
        with self.assertRaises(InvalidDataError):
            h.dat_da_thanh_toan()


class TestCapNhat(unittest.TestCase):
    def test_sua_so_dien_moi(self):
        h = tao()
        h.cap_nhat(so_dien_moi=160)
        self.assertEqual(h.tinh_tien_dien(), 210000)

    def test_sua_nhieu_truong(self):
        h = tao()
        h.cap_nhat(so_dien_cu=90, so_dien_moi=150, so_nuoc_moi=20, phi_o=500000)
        self.assertEqual(h.tong_tien(), 500000 + 60 * 3500 + 10 * 15000)

    def test_sua_moi_nho_hon_cu_hien_tai(self):
        h = tao()
        with self.assertRaises(InvalidDataError):
            h.cap_nhat(so_dien_moi=99)
        self.assertEqual(h.so_dien_moi, 150)

    def test_sua_cu_lon_hon_moi_hien_tai(self):
        with self.assertRaises(InvalidDataError):
            tao().cap_nhat(so_dien_cu=151)

    def test_tat_ca_hoac_khong_gi(self):
        h = tao()
        with self.assertRaises(InvalidDataError):
            h.cap_nhat(phi_o=1, so_nuoc_moi=5)       # nước mới 5 < cũ 10
        self.assertEqual((h.phi_o, h.so_nuoc_moi), (600000, 14))

    def test_khong_duoc_sua_ma_phong_thang_don_gia_trang_thai(self):
        for ten, v in (("ma", "HDX"), ("ma_phong", "A102"), ("thang", "11/2026"),
                       ("don_gia_dien", 1), ("da_thanh_toan", True), ("la", 1)):
            with self.subTest(ten=ten):
                with self.assertRaises(InvalidDataError):
                    tao().cap_nhat(**{ten: v})

    def test_khong_co_gi_de_sua(self):
        with self.assertRaises(InvalidDataError):
            tao().cap_nhat()

    def test_da_thanh_toan_khong_cho_sua(self):
        h = tao()
        h.dat_da_thanh_toan()
        with self.assertRaises(InvalidDataError):
            h.cap_nhat(so_dien_moi=160)
        self.assertEqual(h.so_dien_moi, 150)


class TestToDictTuDict(unittest.TestCase):
    MAU = {"ma": "HDA101202610", "ma_phong": "A101", "thang": "10/2026",
           "so_dien_cu": 100, "so_dien_moi": 150, "so_nuoc_cu": 10, "so_nuoc_moi": 14,
           "phi_o": 600000, "don_gia_dien": 3500, "don_gia_nuoc": 15000,
           "tong_tien": 835000, "da_thanh_toan": False}

    def test_to_dict_dung_mau_hop_dong(self):
        self.assertEqual(tao().to_dict(), self.MAU)

    def test_to_dict_la_json_thuan(self):
        json.dumps(tao().to_dict())

    def test_vong_tron(self):
        h = tao()
        h.dat_da_thanh_toan()
        self.assertEqual(HoaDon.tu_dict(h.to_dict()).to_dict(), h.to_dict())

    def test_tu_dict_mau_hop_dong(self):
        self.assertEqual(HoaDon.tu_dict(dict(self.MAU)).tong_tien(), 835000)

    def test_tu_dict_giu_don_gia_trong_file_du_config_doi(self):
        with mock.patch.object(config, "DON_GIA_DIEN", 9999):
            self.assertEqual(HoaDon.tu_dict(dict(self.MAU)).tong_tien(), 835000)

    def test_tong_tien_lech_thi_tinh_lai_va_canh_bao(self):
        d = dict(self.MAU, tong_tien=1)
        with self.assertLogs("models.hoa_don", level="WARNING"):
            h = HoaDon.tu_dict(d)
        self.assertEqual(h.tong_tien(), 835000)

    def test_tu_dict_khong_co_ma_va_tong_van_duoc(self):
        d = dict(self.MAU)
        del d["ma"], d["tong_tien"]
        self.assertEqual(HoaDon.tu_dict(d).ma, "HDA101202610")

    def test_tu_dict_ma_bi_sua_tay(self):
        with self.assertRaises(InvalidDataError) as ctx:
            HoaDon.tu_dict(dict(self.MAU, ma="HDA999202610"))
        self.assertEqual(ctx.exception.truong, "ma")

    def test_tu_dict_file_bi_sua_tay(self):
        for sai in ({"so_dien_moi": 50}, {"thang": "13/2026"}, {"phi_o": -1},
                    {"da_thanh_toan": "false"}, {"so_nuoc_moi": "14"}):
            with self.subTest(sai=sai):
                with self.assertRaises(InvalidDataError):
                    HoaDon.tu_dict({**self.MAU, **sai})

    def test_tu_dict_thieu_truong_hoac_sai_kieu(self):
        for khoa in ("ma_phong", "thang", "so_dien_moi", "phi_o", "don_gia_dien"):
            d = dict(self.MAU)
            del d[khoa]
            with self.subTest(thieu=khoa):
                with self.assertRaises(InvalidDataError):
                    HoaDon.tu_dict(d)
        for d in (None, [], "HDA101202610", {}):
            with self.subTest(d=d):
                with self.assertRaises(InvalidDataError):
                    HoaDon.tu_dict(d)

    def test_str(self):
        s = str(tao())
        for phan in ("HDA101202610", "A101", "10/2026", "835,000", "chưa thanh toán"):
            self.assertIn(phan, s)


if __name__ == "__main__":
    unittest.main(verbosity=2)