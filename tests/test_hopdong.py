"""Kiểm thử models/hop_dong.py. Chạy từ thư mục gốc:
    python -m unittest tests.test_hop_dong -v
Mọi test truyền ngày cố định nên kết quả không phụ thuộc ngày chạy.
"""
import datetime
import unittest

from exceptions import InvalidDataError
from models.hop_dong import HopDong

D = datetime.date
BD, KT = D(2026, 9, 1), D(2027, 6, 30)


def tao(**kw):
    tham_so = dict(ma_hd="HD0001", ma_sv="2100000001", ma_phong="A101",
                   ngay_bat_dau="01/09/2026", ngay_ket_thuc="30/06/2027")
    tham_so.update(kw)
    return HopDong(**tham_so)


class TestTaoMoi(unittest.TestCase):
    def test_tao_tu_chuoi_va_date_deu_luu_date(self):
        a = tao()
        b = tao(ngay_bat_dau=BD, ngay_ket_thuc=KT)
        self.assertEqual((a.ngay_bat_dau, a.ngay_ket_thuc), (BD, KT))
        self.assertEqual((b.ngay_bat_dau, b.ngay_ket_thuc), (BD, KT))
        self.assertIsInstance(a.ngay_bat_dau, D)

    def test_ma_duoc_chuan_hoa(self):
        h = tao(ma_hd=" hd0001 ", ma_phong="a101")
        self.assertEqual((h.ma, h.ma_hd, h.ma_phong), ("HD0001", "HD0001", "A101"))

    def test_trang_thai_mac_dinh(self):
        self.assertEqual(tao().trang_thai, "hieu_luc")

    def test_ma_hd_sai(self):
        for v in ("HD1", "XX0001", "0001", "", None, 1):
            with self.subTest(ma_hd=v):
                with self.assertRaises(InvalidDataError):
                    tao(ma_hd=v)

    def test_ma_hd_dai_hon_4_chu_so_van_dung(self):
        self.assertEqual(tao(ma_hd="HD123456").ma, "HD123456")

    def test_ma_sv_va_ma_phong_sai(self):
        for ten, v in (("ma_sv", "123"), ("ma_sv", None), ("ma_phong", "Z999"),
                       ("ma_phong", ""), ("ma_phong", None)):
            with self.subTest(**{ten: v}):
                with self.assertRaises(InvalidDataError):
                    tao(**{ten: v})

    def test_ngay_sai_dinh_dang(self):
        for v in ("2026-09-01", "32/01/2026", "abc", "", None, 20260901):
            with self.subTest(v=v):
                with self.assertRaises(InvalidDataError):
                    tao(ngay_bat_dau=v)

    def test_ket_thuc_truoc_hoac_bang_bat_dau(self):          # ca 19 của hợp đồng
        for kt in ("31/08/2026", "01/09/2026"):
            with self.subTest(kt=kt):
                with self.assertRaises(InvalidDataError) as ctx:
                    tao(ngay_ket_thuc=kt)
                self.assertEqual(ctx.exception.truong, "ngay_ket_thuc")

    def test_ket_thuc_sau_bat_dau_1_ngay_la_hop_le(self):
        self.assertEqual(tao(ngay_ket_thuc="02/09/2026").ngay_ket_thuc, D(2026, 9, 2))

    def test_trang_thai_la(self):
        for v in ("het_han", "HIEU_LUC", "", None, True):
            with self.subTest(v=v):
                with self.assertRaises(InvalidDataError):
                    tao(trang_thai=v)

    def test_so_sanh_ngay_bang_date_khong_bang_chuoi(self):
        # chuỗi: "30/06/2027" < "31/08/2026" (sai); date: đúng là sau
        self.assertTrue(tao().ngay_ket_thuc > tao().ngay_bat_dau)

    def test_khong_co_setter_cho_ma_va_ngay_bat_dau(self):
        h = tao()
        for ten in ("ma", "ma_hd", "ma_sv", "ngay_bat_dau"):
            with self.subTest(ten=ten):
                with self.assertRaises(AttributeError):
                    setattr(h, ten, "x")


class TestConHieuLuc(unittest.TestCase):
    def setUp(self):
        self.h = tao()

    def test_ngay_dau_va_cuoi_deu_tinh(self):
        self.assertTrue(self.h.con_hieu_luc(BD))
        self.assertTrue(self.h.con_hieu_luc(KT))

    def test_giua_hop_dong(self):
        self.assertTrue(self.h.con_hieu_luc(D(2026, 12, 25)))

    def test_truoc_bat_dau_va_sau_ket_thuc(self):
        self.assertFalse(self.h.con_hieu_luc(D(2026, 8, 31)))
        self.assertFalse(self.h.con_hieu_luc(D(2027, 7, 1)))

    def test_da_ket_thuc_thi_khong_con_hieu_luc(self):
        self.h.ket_thuc()
        self.assertFalse(self.h.con_hieu_luc(D(2026, 12, 25)))

    def test_nhan_ngay_dang_chuoi(self):
        self.assertTrue(self.h.con_hieu_luc("01/09/2026"))

    def test_ngay_sai_kieu_bao_loi(self):
        with self.assertRaises(InvalidDataError):
            self.h.con_hieu_luc("hom nay")

    def test_mac_dinh_la_hom_nay(self):
        homnay = tao(ngay_bat_dau=D.today() - datetime.timedelta(days=1),
                     ngay_ket_thuc=D.today() + datetime.timedelta(days=10))
        self.assertTrue(homnay.con_hieu_luc())
        self.assertTrue(homnay.sap_het_han())


class TestSapHetHan(unittest.TestCase):                      # ca 20 của hợp đồng
    def setUp(self):
        self.h = tao()   # kết thúc 30/06/2027

    def test_29_30_31_ngay_truoc_han(self):
        self.assertTrue(self.h.sap_het_han(KT - datetime.timedelta(days=29)))
        self.assertTrue(self.h.sap_het_han(KT - datetime.timedelta(days=30)))
        self.assertFalse(self.h.sap_het_han(KT - datetime.timedelta(days=31)))

    def test_dung_ngay_het_han_van_canh_bao(self):
        self.assertTrue(self.h.sap_het_han(KT))

    def test_sau_han_khong_canh_bao(self):
        self.assertFalse(self.h.sap_het_han(KT + datetime.timedelta(days=1)))

    def test_hop_dong_da_ket_thuc_khong_canh_bao(self):
        self.h.ket_thuc()
        self.assertFalse(self.h.sap_het_han(KT - datetime.timedelta(days=5)))

    def test_truoc_ngay_bat_dau_khong_canh_bao(self):
        ngan = tao(ngay_ket_thuc="10/09/2026")
        self.assertFalse(ngan.sap_het_han(D(2026, 8, 25)))

    def test_so_ngay_tuy_chinh(self):
        self.assertTrue(self.h.sap_het_han(KT - datetime.timedelta(days=60), so_ngay=60))
        self.assertFalse(self.h.sap_het_han(KT - datetime.timedelta(days=61), so_ngay=60))


class TestTinhTrangThai(unittest.TestCase):
    def test_ba_trang_thai(self):
        h = tao()
        self.assertEqual(h.tinh_trang_thai(D(2026, 12, 1)), "hieu_luc")
        self.assertEqual(h.tinh_trang_thai(KT), "hieu_luc")
        self.assertEqual(h.tinh_trang_thai(D(2027, 7, 1)), "het_han")
        h.ket_thuc()
        self.assertEqual(h.tinh_trang_thai(D(2026, 12, 1)), "da_ket_thuc")
        self.assertEqual(h.tinh_trang_thai(D(2027, 7, 1)), "da_ket_thuc")

    def test_het_han_khong_duoc_luu_vao_trang_thai(self):
        h = tao()
        h.tinh_trang_thai(D(2030, 1, 1))
        self.assertEqual(h.trang_thai, "hieu_luc")
        self.assertEqual(h.to_dict()["trang_thai"], "hieu_luc")


class TestGiaHanVaKetThuc(unittest.TestCase):
    def test_gia_han_thanh_cong(self):
        h = tao()
        h.gia_han("31/08/2027")
        self.assertEqual(h.ngay_ket_thuc, D(2027, 8, 31))

    def test_gia_han_nhan_date(self):
        h = tao()
        h.gia_han(D(2027, 7, 1))
        self.assertEqual(h.ngay_ket_thuc, D(2027, 7, 1))

    def test_gia_han_khong_sau_ngay_ket_thuc_cu(self):
        for v in ("30/06/2027", "01/01/2027"):
            with self.subTest(v=v):
                h = tao()
                with self.assertRaises(InvalidDataError):
                    h.gia_han(v)
                self.assertEqual(h.ngay_ket_thuc, KT)

    def test_gia_han_ngay_sai(self):
        with self.assertRaises(InvalidDataError):
            tao().gia_han("abc")

    def test_gia_han_hop_dong_da_ket_thuc(self):
        h = tao()
        h.ket_thuc()
        with self.assertRaises(InvalidDataError):
            h.gia_han("31/12/2027")

    def test_ket_thuc(self):
        h = tao()
        h.ket_thuc()
        self.assertEqual(h.trang_thai, "da_ket_thuc")

    def test_ket_thuc_hai_lan(self):
        h = tao()
        h.ket_thuc()
        with self.assertRaises(InvalidDataError):
            h.ket_thuc()


class TestCapNhat(unittest.TestCase):
    def test_sua_ba_truong_duoc_phep(self):
        h = tao()
        h.cap_nhat(ngay_ket_thuc="31/12/2026", ma_phong="b202", trang_thai="da_ket_thuc")
        self.assertEqual((h.ngay_ket_thuc, h.ma_phong, h.trang_thai),
                         (D(2026, 12, 31), "B202", "da_ket_thuc"))

    def test_khong_duoc_sua_ma_sv_ma_hd_ngay_bat_dau(self):
        for ten, v in (("ma_hd", "HD0002"), ("ma_sv", "2100000002"),
                       ("ngay_bat_dau", "02/09/2026"), ("ten_la", 1)):
            with self.subTest(ten=ten):
                with self.assertRaises(InvalidDataError):
                    tao().cap_nhat(**{ten: v})

    def test_khong_co_gi_de_sua(self):
        with self.assertRaises(InvalidDataError):
            tao().cap_nhat()

    def test_tat_ca_hoac_khong_gi(self):
        h = tao()
        with self.assertRaises(InvalidDataError):
            h.cap_nhat(ma_phong="B202", ngay_ket_thuc="01/01/2020")  # ngày sai
        self.assertEqual(h.ma_phong, "A101")
        self.assertEqual(h.ngay_ket_thuc, KT)

    def test_trang_thai_sai_khong_doi_gi(self):
        h = tao()
        with self.assertRaises(InvalidDataError):
            h.cap_nhat(ma_phong="B202", trang_thai="het_han")
        self.assertEqual(h.ma_phong, "A101")


class TestToDictTuDict(unittest.TestCase):
    def test_to_dict_ngay_dang_chuoi(self):
        self.assertEqual(tao().to_dict(), {
            "ma_hd": "HD0001", "ma_sv": "2100000001", "ma_phong": "A101",
            "ngay_bat_dau": "01/09/2026", "ngay_ket_thuc": "30/06/2027",
            "trang_thai": "hieu_luc"})

    def test_vong_tron(self):
        h = tao()
        h.gia_han("01/08/2027")
        h.ket_thuc()
        self.assertEqual(HopDong.tu_dict(h.to_dict()).to_dict(), h.to_dict())

    def test_to_dict_la_json_thuan(self):
        import json
        json.dumps(tao().to_dict())            # không ném lỗi => toàn kiểu cơ bản

    def test_tu_dict_thieu_truong_hoac_sai_kieu(self):
        goc = tao().to_dict()
        for d in (None, [], "HD0001", {},
                  {k: v for k, v in goc.items() if k != "ngay_ket_thuc"}):
            with self.subTest(d=d):
                with self.assertRaises(InvalidDataError):
                    HopDong.tu_dict(d)

    def test_tu_dict_file_bi_sua_tay(self):
        goc = tao().to_dict()
        for sai in ({"ngay_ket_thuc": "01/01/2020"}, {"ma_sv": "abc"},
                    {"trang_thai": "het_han"}, {"ngay_bat_dau": "xx"}):
            with self.subTest(sai=sai):
                with self.assertRaises(InvalidDataError):
                    HopDong.tu_dict({**goc, **sai})

    def test_tu_dict_thieu_trang_thai_thi_mac_dinh(self):
        goc = tao().to_dict()
        del goc["trang_thai"]
        self.assertEqual(HopDong.tu_dict(goc).trang_thai, "hieu_luc")

    def test_str(self):
        s = str(tao())
        for phan in ("HD0001", "A101", "01/09/2026", "30/06/2027"):
            self.assertIn(phan, s)


if __name__ == "__main__":
    unittest.main(verbosity=2)