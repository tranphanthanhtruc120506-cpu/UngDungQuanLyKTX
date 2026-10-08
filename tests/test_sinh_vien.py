"""Kiểm thử - SinhVien và ViPham.
Chạy: python -m unittest tests.test_sinh_vien -v """
import unittest
from datetime import date, timedelta

from exceptions import InvalidDataError
from models.sinh_vien import SinhVien
from models.vi_pham import ViPham


def tao_sv(**ghi_de):
    tham_so = dict(ma_sv="2100000001", ho_ten="Nguyễn Văn An", ngay_sinh="15/03/2005",
                   so_dien_thoai="0912345678", lop="DH21CNTT", email="an@gmail.com")
    tham_so.update(ghi_de)
    return SinhVien(**tham_so)


def ngay_cach_day(so_nam=0, so_ngay=0):
    """Chuỗi dd/mm/yyyy cách hôm nay một khoảng (âm = quá khứ)."""
    d = date.today()
    try:
        d = d.replace(year=d.year + so_nam)
    except ValueError:                       # 29/02
        d = d.replace(year=d.year + so_nam, day=28)
    d = d + timedelta(days=so_ngay)
    return d.strftime("%d/%m/%Y")


class KiemTraTaoSinhVien(unittest.TestCase):
    def test_tao_hop_le(self):                                     # test case 1
        sv = tao_sv()
        self.assertEqual(sv.ma_sv, "2100000001")
        self.assertEqual(sv.ma, "2100000001")
        self.assertEqual(sv.ho_ten, "Nguyễn Văn An")
        self.assertEqual(sv.ngay_sinh, date(2005, 3, 15))
        self.assertEqual(sv.so_dien_thoai, "0912345678")
        self.assertEqual(sv.lop, "DH21CNTT")
        self.assertEqual(str(sv), "2100000001 - Nguyễn Văn An - DH21CNTT")

    def test_chuan_hoa_khi_tao(self):
        sv = tao_sv(ho_ten="  Trần   Thị  Bé ", so_dien_thoai="+84912345678",
                    lop="  DH21CNTT ", ma_sv=" 2100000001 ")
        self.assertEqual(sv.ho_ten, "Trần Thị Lan")
        self.assertEqual(sv.so_dien_thoai, "0912345678")
        self.assertEqual(sv.lop, "DH21CNTT")
        self.assertEqual(sv.ma_sv, "2100000001")

    def test_email_khong_bat_buoc(self):
        for rong in (None, "", "   "):
            with self.subTest(email=rong):
                self.assertIsNone(tao_sv(email=rong).email)
        self.assertIsNone(SinhVien("2100000001", "An Văn", "15/03/2005", "0912345678", "DH21").email)

    def test_nhan_ngay_sinh_kieu_date(self):
        self.assertEqual(tao_sv(ngay_sinh=date(2005, 3, 15)).ngay_sinh, date(2005, 3, 15))


class KiemTraDuLieuSai(unittest.TestCase):
    def _sai(self, truong, **kw):
        with self.assertRaises(InvalidDataError) as ctx:
            tao_sv(**kw)
        self.assertEqual(ctx.exception.truong, truong)

    def test_ma_sv_sai(self):
        for sai in ("", "210000001", "21000000012", "21000000AB", None, 2100000001):
            with self.subTest(ma_sv=sai):
                self._sai("ma_sv", ma_sv=sai)

    def test_ho_ten_sai(self):                                      # test case 4
        for sai in ("", "   ", "A", "Nguyen 123", "An@", "x" * 101, None, 123):
            with self.subTest(ho_ten=sai):
                self._sai("ho_ten", ho_ten=sai)

    def test_sdt_sai(self):                                         # test case 3
        for sai in ("12345", "091234567", "09123abc78", "", None, 912345678):
            with self.subTest(sdt=sai):
                self._sai("so_dien_thoai", so_dien_thoai=sai)

    def test_email_sai(self):
        for sai in ("an@gmail", "an gmail.com", "@gmail.com", 123):
            with self.subTest(email=sai):
                self._sai("email", email=sai)

    def test_ngay_sinh_sai_dinh_dang(self):
        for sai in ("30/02/2005", "2005-03-15", "abc", "", None, 20050315):
            with self.subTest(ngay_sinh=sai):
                self._sai("ngay_sinh", ngay_sinh=sai)

    def test_ngay_sinh_tuong_lai_va_tuoi(self):
        self._sai("ngay_sinh", ngay_sinh=ngay_cach_day(so_ngay=1))        # ngày mai
        self._sai("ngay_sinh", ngay_sinh=ngay_cach_day(so_nam=-15))       # 15 tuổi
        self._sai("ngay_sinh", ngay_sinh=ngay_cach_day(so_nam=-70))       # 70 tuổi

    def test_tuoi_bien(self):
        # đủ 16 tuổi đúng hôm nay: được; thiếu 1 ngày: không
        self.assertIsNotNone(tao_sv(ngay_sinh=ngay_cach_day(so_nam=-16)))
        self._sai("ngay_sinh", ngay_sinh=ngay_cach_day(so_nam=-16, so_ngay=1))
        # đủ 60 tuổi hôm nay: được
        self.assertIsNotNone(tao_sv(ngay_sinh=ngay_cach_day(so_nam=-60)))

    def test_lop_sai(self):
        for sai in ("", "   ", None, 5, "x" * 21):
            with self.subTest(lop=sai):
                self._sai("lop", lop=sai)

    def test_khong_nem_loi_khac_loai(self):
        """Dù dữ liệu quái đến đâu cũng chỉ ra InvalidDataError, không TypeError/ValueError."""
        for quai in (None, [], {}, 3.5, object()):
            with self.subTest(gia_tri=quai):
                with self.assertRaises(InvalidDataError):
                    SinhVien(quai, quai, quai, quai, quai, quai)


class KiemTraSetterVaCapNhat(unittest.TestCase):
    def test_setter_hop_le(self):
        sv = tao_sv()
        sv.ho_ten = "Lê Đức"
        sv.so_dien_thoai = "+84356789012"
        sv.lop = "DH22"
        sv.email = None
        sv.ngay_sinh = "01/01/2004"
        self.assertEqual((sv.ho_ten, sv.so_dien_thoai, sv.lop, sv.email, sv.ngay_sinh),
                         ("Lê Đức", "0356789012", "DH22", None, date(2004, 1, 1)))

    def test_setter_tu_choi_du_lieu_sai_va_giu_gia_tri_cu(self):     # "Xong khi" của B2
        sv = tao_sv()
        for ten_truong, gia_tri_sai in (("ho_ten", "An123"), ("so_dien_thoai", "12345"),
                                        ("email", "sai"), ("lop", ""), ("ngay_sinh", "32/01/2005")):
            with self.subTest(truong=ten_truong):
                truoc = getattr(sv, ten_truong)
                with self.assertRaises(InvalidDataError) as ctx:
                    setattr(sv, ten_truong, gia_tri_sai)
                self.assertEqual(ctx.exception.truong, ten_truong)
                self.assertEqual(getattr(sv, ten_truong), truoc)

    def test_ma_sv_chi_doc(self):
        sv = tao_sv()
        with self.assertRaises(AttributeError):
            sv.ma_sv = "2100000002"
        with self.assertRaises(AttributeError):
            sv.ma = "X"

    def test_cap_nhat_thanh_cong(self):
        sv = tao_sv()
        sv.cap_nhat(ho_ten="Trần Thị Bé", lop="DH22")
        self.assertEqual((sv.ho_ten, sv.lop), ("Trần Thị Bé", "DH22"))

    def test_cap_nhat_tat_ca_hoac_khong_gi(self):
        sv = tao_sv()
        truoc = sv.to_dict()
        with self.assertRaises(InvalidDataError):
            sv.cap_nhat(ho_ten="Trần Thị Bé", so_dien_thoai="12345")   # trường 2 sai
        self.assertEqual(sv.to_dict(), truoc)                          # trường 1 cũng không đổi

    def test_cap_nhat_khong_doi_ma_va_truong_la(self):
        sv = tao_sv()
        for khoa in ("ma_sv", "ma", "khong_co"):
            with self.subTest(khoa=khoa):
                with self.assertRaises(InvalidDataError):
                    sv.cap_nhat(**{khoa: "X"})
        self.assertEqual(sv.ma_sv, "2100000001")


class KiemTraJson(unittest.TestCase):
    def test_to_dict(self):
        self.assertEqual(tao_sv().to_dict(), {
            "ma_sv": "2100000001", "ho_ten": "Nguyễn Văn An", "ngay_sinh": "15/03/2005",
            "so_dien_thoai": "0912345678", "email": "an@gmail.com", "lop": "DH21CNTT"})

    def test_khu_hoi(self):
        sv = tao_sv()
        sv2 = SinhVien.from_dict(sv.to_dict())
        self.assertEqual(sv2.to_dict(), sv.to_dict())
        self.assertEqual(SinhVien.tu_dict(sv.to_dict()).to_dict(), sv.to_dict())

    def test_from_dict_thieu_truong_hoac_sai_kieu(self):
        goc = tao_sv().to_dict()
        for truong in ("ma_sv", "ho_ten", "ngay_sinh", "so_dien_thoai", "lop"):
            d = dict(goc)
            del d[truong]
            with self.subTest(thieu=truong):
                with self.assertRaises(InvalidDataError) as ctx:
                    SinhVien.from_dict(d)
                self.assertEqual(ctx.exception.truong, truong)
        for khong_phai_dict in (None, [], "abc", 5):
            with self.subTest(kieu=khong_phai_dict):
                with self.assertRaises(InvalidDataError):
                    SinhVien.from_dict(khong_phai_dict)

    def test_from_dict_file_bi_sua_tay_thanh_sai(self):
        d = tao_sv().to_dict()
        d["so_dien_thoai"] = "12345"
        with self.assertRaises(InvalidDataError):
            SinhVien.from_dict(d)

    def test_from_dict_bo_qua_khoa_thua_va_thieu_email(self):
        d = tao_sv().to_dict()
        d["khoa_la"] = 1
        del d["email"]
        self.assertIsNone(SinhVien.from_dict(d).email)


def tao_vp(**ghi_de):
    tham_so = dict(ma_vp="VP0001", ma_sv="2100000001", noi_dung="Về muộn sau 23h",
                   ngay="02/10/2025", muc_phat=50000)
    tham_so.update(ghi_de)
    return ViPham(**tham_so)


class KiemTraViPham(unittest.TestCase):
    def test_tao_hop_le(self):
        vp = tao_vp(ma_vp="vp0001")
        self.assertEqual(vp.ma, "VP0001")
        self.assertEqual(vp.ma_vp, "VP0001")
        self.assertEqual(vp.ma_sv, "2100000001")
        self.assertEqual(vp.ngay, date(2025, 10, 2))
        self.assertEqual(vp.muc_phat, 50000)
        self.assertIn("50,000", str(vp))

    def test_muc_phat_mac_dinh_va_chuoi_so(self):
        self.assertEqual(ViPham("VP0002", "2100000001", "Nhắc nhở", "02/10/2025").muc_phat, 0)
        self.assertEqual(tao_vp(muc_phat="70000").muc_phat, 70000)

    def _sai(self, truong, **kw):
        with self.assertRaises(InvalidDataError) as ctx:
            tao_vp(**kw)
        self.assertEqual(ctx.exception.truong, truong)

    def test_du_lieu_sai(self):
        for sai in ("VP001", "HD0001", "", None):
            with self.subTest(ma_vp=sai):
                self._sai("ma_vp", ma_vp=sai)
        for sai in ("21", "", None):
            with self.subTest(ma_sv=sai):
                self._sai("ma_sv", ma_sv=sai)
        for sai in ("", "   ", None, "x" * 301):
            with self.subTest(noi_dung=sai):
                self._sai("noi_dung", noi_dung=sai)
        for sai in ("30/02/2025", "abc", "", None, ngay_cach_day(so_ngay=1)):
            with self.subTest(ngay=sai):
                self._sai("ngay", ngay=sai)
        for sai in (-1, "-5", "abc", 1.5, True, None):
            with self.subTest(muc_phat=sai):
                self._sai("muc_phat", muc_phat=sai)

    def test_setter_va_cap_nhat(self):
        vp = tao_vp()
        vp.muc_phat = 100000
        vp.noi_dung = "Hút thuốc"
        self.assertEqual((vp.muc_phat, vp.noi_dung), (100000, "Hút thuốc"))
        truoc = vp.to_dict()
        with self.assertRaises(InvalidDataError):
            vp.cap_nhat(noi_dung="Mới", muc_phat=-5)
        self.assertEqual(vp.to_dict(), truoc)
        for khoa in ("ma_vp", "ma_sv", "ma"):
            with self.subTest(khoa=khoa):
                with self.assertRaises(InvalidDataError):
                    vp.cap_nhat(**{khoa: "X"})
        with self.assertRaises(AttributeError):
            vp.ma_sv = "2100000002"

    def test_json(self):
        vp = tao_vp()
        self.assertEqual(vp.to_dict(), {"ma_vp": "VP0001", "ma_sv": "2100000001",
                                        "noi_dung": "Về muộn sau 23h", "ngay": "02/10/2025",
                                        "muc_phat": 50000})
        self.assertEqual(ViPham.from_dict(vp.to_dict()).to_dict(), vp.to_dict())
        with self.assertRaises(InvalidDataError):
            ViPham.from_dict({"ma_vp": "VP0001"})
        with self.assertRaises(InvalidDataError):
            ViPham.from_dict(None)


if __name__ == "__main__":
    unittest.main()