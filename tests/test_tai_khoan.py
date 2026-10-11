"""Kiểm thử TaiKhoan (B4). Chạy: python -m unittest tests.test_tai_khoan -v"""
import unittest

import config
from exceptions import InvalidDataError
from models.tai_khoan import TaiKhoan


class TestTaiKhoan(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Giảm số vòng băm cho test chạy nhanh; trả lại giá trị cũ ở tearDownClass
        cls.so_vong_cu = config.PBKDF2_SO_VONG
        config.PBKDF2_SO_VONG = 1000

    @classmethod
    def tearDownClass(cls):
        config.PBKDF2_SO_VONG = cls.so_vong_cu

    # ---- tao / băm mật khẩu ----
    def test_tao_chi_luu_chuoi_bam_khong_luu_mat_khau_goc(self):
        tk = TaiKhoan.tao("an01", "matkhau123")
        self.assertTrue(tk.mat_khau_bam.startswith("pbkdf2_sha256$"))
        self.assertNotIn("matkhau123", tk.mat_khau_bam)
        self.assertNotIn("matkhau123", str(tk.to_dict()))

    def test_cung_mat_khau_nhung_salt_khac_nen_chuoi_bam_khac(self):
        a = TaiKhoan.tao("an01", "matkhau123")
        b = TaiKhoan.tao("binh02", "matkhau123")
        self.assertNotEqual(a.mat_khau_bam, b.mat_khau_bam)

    def test_mat_khau_ngan_hon_toi_thieu_nem_InvalidDataError(self):
        with self.assertRaises(InvalidDataError) as ctx:
            TaiKhoan.tao("an01", "12345")          # 5 ký tự
        self.assertEqual(ctx.exception.truong, "mat_khau")

    def test_bien_mat_khau_dung_toi_thieu_6_ky_tu_hop_le(self):
        tk = TaiKhoan.tao("an01", "123456")
        self.assertTrue(tk.kiem_tra_mat_khau("123456"))

    def test_mat_khau_khong_phai_chuoi_nem_InvalidDataError(self):
        with self.assertRaises(InvalidDataError):
            TaiKhoan.tao("an01", 123456)

    # ---- kiem_tra_mat_khau ----
    def test_kiem_tra_mat_khau_dung_tra_True(self):
        tk = TaiKhoan.tao("an01", "matkhau123")
        self.assertTrue(tk.kiem_tra_mat_khau("matkhau123"))

    def test_kiem_tra_mat_khau_sai_tra_False(self):
        tk = TaiKhoan.tao("an01", "matkhau123")
        self.assertFalse(tk.kiem_tra_mat_khau("matkhau124"))

    def test_kiem_tra_mat_khau_khong_phai_chuoi_tra_False_khong_nem_loi(self):
        tk = TaiKhoan.tao("an01", "matkhau123")
        self.assertFalse(tk.kiem_tra_mat_khau(None))
        self.assertFalse(tk.kiem_tra_mat_khau(123456))

    # ---- username ----
    def test_username_duoc_luu_chu_thuong(self):
        self.assertEqual(TaiKhoan.tao("  AnNguyen01 ", "matkhau123").username, "annguyen01")

    def test_username_sai_dinh_dang_nem_InvalidDataError(self):
        for ten in ("ab", "co dau", "nguyễn", "a" * 21, ""):
            with self.assertRaises(InvalidDataError):
                TaiKhoan.tao(ten, "matkhau123")

    def test_bien_username_dung_3_va_20_ky_tu_hop_le(self):
        self.assertEqual(TaiKhoan.tao("abc", "matkhau123").username, "abc")
        self.assertEqual(len(TaiKhoan.tao("a" * 20, "matkhau123").username), 20)

    # ---- vai trò, ma_sv ----
    def test_vai_tro_mac_dinh_la_user_va_la_admin_False(self):
        tk = TaiKhoan.tao("an01", "matkhau123")
        self.assertEqual(tk.vai_tro, "user")
        self.assertFalse(tk.la_admin())

    def test_vai_tro_admin(self):
        self.assertTrue(TaiKhoan.tao("quantri", "matkhau123", "admin").la_admin())

    def test_vai_tro_la_nem_InvalidDataError(self):
        with self.assertRaises(InvalidDataError):
            TaiKhoan.tao("an01", "matkhau123", "boss")

    def test_ma_sv_hop_le_va_sai(self):
        self.assertEqual(TaiKhoan.tao("an01", "matkhau123", "user", "2100000001").ma_sv, "2100000001")
        self.assertIsNone(TaiKhoan.tao("an02", "matkhau123").ma_sv)
        with self.assertRaises(InvalidDataError):
            TaiKhoan.tao("an03", "matkhau123", "user", "abc")

    # ---- to_dict / tu_dict ----
    def test_to_dict_roi_tu_dict_van_dang_nhap_duoc(self):
        goc = TaiKhoan.tao("an01", "matkhau123", "user", "2100000001")
        moi = TaiKhoan.tu_dict(goc.to_dict())
        self.assertEqual(moi.username, "an01")
        self.assertEqual(moi.ma_sv, "2100000001")
        self.assertTrue(moi.kiem_tra_mat_khau("matkhau123"))

    def test_tu_dict_thieu_truong_nem_InvalidDataError(self):
        with self.assertRaises(InvalidDataError):
            TaiKhoan.tu_dict({"username": "an01", "vai_tro": "user"})

    def test_tu_dict_chuoi_bam_gia_nem_InvalidDataError(self):
        with self.assertRaises(InvalidDataError):
            TaiKhoan.tu_dict({"username": "an01", "mat_khau_bam": "matkhau123", "vai_tro": "user"})

    def test_tu_dict_khong_phai_dict_nem_InvalidDataError(self):
        with self.assertRaises(InvalidDataError):
            TaiKhoan.tu_dict("không phải dict")


if __name__ == "__main__":
    unittest.main()