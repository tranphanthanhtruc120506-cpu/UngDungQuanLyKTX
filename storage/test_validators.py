import unittest
from datetime import date, datetime

from exceptions import InvalidDataError
from utils import validators as v


class KiemTraHopLe(unittest.TestCase):
    """Kiểm tra từng hàm hop_le_*: danh sách ca đúng và ca sai."""

    def _kiem(self, ham, dung, sai):
        for x in dung:
            with self.subTest(ca="đúng", gia_tri=x):
                self.assertIs(ham(x), True)
        for x in sai:
            with self.subTest(ca="sai", gia_tri=x):
                self.assertIs(ham(x), False)  # và không ném lỗi

    def test_hop_le_sdt(self):
        self._kiem(
            v.hop_le_sdt,
            dung=["0912345678", "+84912345678", "  0356789012  ", "0987654321"],
            sai=["12345", "091234567", "09123456789", "1912345678",
                 "+8491234567", "09123abc78", "０９１２３４５６７８", "", None, 912345678],
        )

    def test_hop_le_email(self):
        self._kiem(
            v.hop_le_email,
            dung=["an@gmail.com", "nguyen.van-an+ktx@sv.edu.vn", "A_B@x-y.co", "a1@b.io"],
            sai=["an@gmail", "@gmail.com", "an@.com", "an gmail.com", "an@@gmail.com",
                 "an@gmail.c", "", None, 123, "a" * 250 + "@b.com"],
        )

    def test_hop_le_ma_sv(self):
        self._kiem(
            v.hop_le_ma_sv,
            dung=["2100000001", "2412345678", " 0000000000 "],
            sai=["210000001", "21000000012", "21000000AB", "2100 00001", "", None, 2100000001],
        )

    def test_hop_le_ma_phong(self):
        self._kiem(
            v.hop_le_ma_phong,
            dung=["A101", "d999", " B205 ", "C000"],
            sai=["E101", "A10", "A1010", "101A", "AA01", "", None, 101],
        )

    def test_hop_le_ngay(self):
        self._kiem(
            v.hop_le_ngay,
            dung=["15/03/2005", "29/02/2024", "31/12/1999", " 01/01/2026 "],
            sai=["30/02/2026", "29/02/2025", "32/01/2026", "15/13/2005", "1/3/2005",
                 "2005/03/15", "15-03-2005", "", None, date(2005, 3, 15)],
        )

    # ---- các hàm bổ sung 
    def test_hop_le_ma_hd(self):
        self._kiem(v.hop_le_ma_hd, ["HD0001", "hd12345", " HD9999 "],
                   ["HD001", "H0001", "HD00A1", "", None])

    def test_hop_le_ma_vp(self):
        self._kiem(v.hop_le_ma_vp, ["VP0001", "vp00123", "VP9999"],
                   ["VP001", "V0001", "VPABCD", "", None])

    def test_hop_le_ho_ten(self):
        self._kiem(
            v.hop_le_ho_ten,
            dung=["Nguyễn Văn An", "  Trần   Thị  Bé ", "Lê Đức", "Ng"],
            sai=["", "A", "Nguyen 123", "An@", "x" * 101, None, 123],
        )

    def test_hop_le_ho_ten_unicode_to_hop(self):
        # viết kiểu tổ hợp (e + dấu rời) vẫn được chấp nhận
        self.assertTrue(v.hop_le_ho_ten(unicodedata_nfd("Nguyễn Việt")))

    def test_hop_le_username(self):
        self._kiem(v.hop_le_username, ["admin", "an_01", "ABC", "a" * 20],
                   ["ab", "a" * 21, "an an", "an-01", "", None])

    def test_hop_le_thang(self):
        self._kiem(v.hop_le_thang, ["10/2026", "01/1999", "12/2030"],
                   ["13/2026", "00/2026", "1/2026", "10-2026", "", None])


def unicodedata_nfd(s):
    import unicodedata
    return unicodedata.normalize("NFD", s)


class KiemTraChuanHoa(unittest.TestCase):
    def test_chuan_hoa_ma(self):
        self.assertEqual(v.chuan_hoa_ma("  a101 "), "A101")
        self.assertEqual(v.chuan_hoa_ma("2100000001"), "2100000001")
        for sai in ["", "   ", None, 123]:
            with self.subTest(sai=sai):
                with self.assertRaises(InvalidDataError) as ctx:
                    v.chuan_hoa_ma(sai, "ma_phong")
                self.assertEqual(ctx.exception.truong, "ma_phong")

    def test_chuan_hoa_sdt(self):
        self.assertEqual(v.chuan_hoa_sdt("+84912345678"), "0912345678")
        self.assertEqual(v.chuan_hoa_sdt(" 0912345678 "), "0912345678")
        with self.assertRaises(InvalidDataError) as ctx:
            v.chuan_hoa_sdt("12345")  # ca 3 của file hướng dẫn
        self.assertEqual(ctx.exception.truong, "so_dien_thoai")
        with self.assertRaises(InvalidDataError):
            v.chuan_hoa_sdt(None)

    def test_chuan_hoa_ho_ten(self):
        self.assertEqual(v.chuan_hoa_ho_ten("  Nguyễn   Văn  An "), "Nguyễn Văn An")
        with self.assertRaises(InvalidDataError) as ctx:
            v.chuan_hoa_ho_ten("")
        self.assertEqual(ctx.exception.truong, "ho_ten")

    def test_doc_ngay(self):
        self.assertEqual(v.doc_ngay("15/03/2005"), date(2005, 3, 15))
        self.assertEqual(v.doc_ngay(date(2026, 1, 2)), date(2026, 1, 2))
        self.assertEqual(v.doc_ngay(datetime(2026, 1, 2, 8, 30)), date(2026, 1, 2))
        for sai in ["30/02/2026", "abc", "", None, 20050315]:
            with self.subTest(sai=sai):
                with self.assertRaises(InvalidDataError):
                    v.doc_ngay(sai, "ngay_sinh")

    def test_dinh_dang_ngay(self):
        self.assertEqual(v.dinh_dang_ngay(date(2005, 3, 5)), "05/03/2005")
        self.assertEqual(v.dinh_dang_ngay(v.doc_ngay("31/12/1999")), "31/12/1999")
        with self.assertRaises(InvalidDataError):
            v.dinh_dang_ngay("05/03/2005")

    def test_doc_so_nguyen(self):
        self.assertEqual(v.doc_so_nguyen("4", "so_cho"), 4)
        self.assertEqual(v.doc_so_nguyen(" -7 "), -7)
        self.assertEqual(v.doc_so_nguyen(12), 12)
        for sai in ["abc", "12.5", "", None, True, 3.0, "1 2"]:  # ca 8: chữ vào ô số
            with self.subTest(sai=sai):
                with self.assertRaises(InvalidDataError):  # không được là ValueError
                    v.doc_so_nguyen(sai, "so_cho")

    def test_doc_so_nguyen_khoang(self):
        self.assertEqual(v.doc_so_nguyen("12", "so_cho", toi_thieu=1, toi_da=12), 12)
        with self.assertRaises(InvalidDataError):
            v.doc_so_nguyen("0", "so_cho", toi_thieu=1)
        with self.assertRaises(InvalidDataError):
            v.doc_so_nguyen("13", "so_cho", toi_da=12)

    def test_yeu_cau_chuoi(self):
        self.assertEqual(v.yeu_cau_chuoi("  DH21CNTT ", "lop", toi_da=20), "DH21CNTT")
        for sai in ["", "   ", None, 5]:
            with self.subTest(sai=sai):
                with self.assertRaises(InvalidDataError):
                    v.yeu_cau_chuoi(sai, "lop")
        with self.assertRaises(InvalidDataError):
            v.yeu_cau_chuoi("x" * 21, "lop", toi_da=20)


if __name__ == "__main__":
    unittest.main()