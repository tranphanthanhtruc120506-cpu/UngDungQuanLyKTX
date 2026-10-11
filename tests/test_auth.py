"""Kiểm thử AuthService (B4). Chạy: python -m unittest tests.test_auth -v"""
import json
import os
import tempfile
import unittest

import config
from exceptions import (AuthenticationError, DuplicateIdError, InvalidDataError,
                        PermissionDeniedError, StorageError)
from models.tai_khoan import TaiKhoan
from services.auth import AuthService
from storage.json_storage import JsonStorage


class KhoGia:
    """Kho giả để thử tình huống ghi file thất bại (hết quyền ghi, ổ đĩa đầy...)."""

    def __init__(self):
        self.du_lieu = []
        self.loi = False

    def doc(self):
        return list(self.du_lieu)

    def ghi(self, du_lieu):
        if self.loi:
            raise StorageError("Không ghi được file tài khoản", None)
        self.du_lieu = list(du_lieu)


class TestAuthService(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.so_vong_cu = config.PBKDF2_SO_VONG
        config.PBKDF2_SO_VONG = 1000           # băm nhanh hơn khi test

    @classmethod
    def tearDownClass(cls):
        config.PBKDF2_SO_VONG = cls.so_vong_cu

    def setUp(self):
        tam = tempfile.TemporaryDirectory()
        self.addCleanup(tam.cleanup)
        self.duong_dan = os.path.join(tam.name, "accounts.json")
        self.storage = JsonStorage(self.duong_dan, mac_dinh=[],
                                   thu_muc_backup=os.path.join(tam.name, "backup"))
        self.auth = AuthService(self.storage)

    # ---- admin mặc định ----
    def test_file_trong_tu_tao_admin_mac_dinh_dang_nhap_duoc(self):
        tk = self.auth.dang_nhap("admin", "admin123")
        self.assertTrue(tk.la_admin())

    # ---- dang_ky ----
    def test_dang_ky_user_thanh_cong_chua_tu_dang_nhap(self):
        tk = self.auth.dang_ky("an01", "matkhau123", ma_sv="2100000001")
        self.assertEqual(tk.vai_tro, "user")
        self.assertIsNone(self.auth.tai_khoan_hien_tai)

    def test_dang_ky_file_khong_chua_mat_khau_goc_va_bat_dau_bang_pbkdf2(self):
        self.auth.dang_ky("an01", "matkhau123")
        with open(self.duong_dan, "r", encoding="utf-8") as f:
            noi_dung = f.read()
        self.assertNotIn("matkhau123", noi_dung)
        self.assertIn("pbkdf2_sha256$", noi_dung)

    def test_dang_ky_trung_username_khong_phan_biet_hoa_thuong(self):
        self.auth.dang_ky("an01", "matkhau123")
        with self.assertRaises(DuplicateIdError):
            self.auth.dang_ky("AN01", "matkhau456")

    def test_dang_ky_mat_khau_5_ky_tu_nem_InvalidDataError_va_6_ky_tu_thanh_cong(self):
        with self.assertRaises(InvalidDataError):
            self.auth.dang_ky("an01", "12345")
        self.assertEqual(self.auth.dang_ky("an01", "123456").username, "an01")

    def test_dang_ky_username_sai_dinh_dang_nem_InvalidDataError(self):
        with self.assertRaises(InvalidDataError):
            self.auth.dang_ky("a b", "matkhau123")

    def test_dang_ky_vai_tro_la_nem_InvalidDataError(self):
        with self.assertRaises(InvalidDataError):
            self.auth.dang_ky("an01", "matkhau123", vai_tro="boss")

    def test_dang_ky_admin_khong_co_nguoi_thuc_hien_nem_PermissionDeniedError(self):
        with self.assertRaises(PermissionDeniedError):
            self.auth.dang_ky("quantri2", "matkhau123", vai_tro="admin")

    def test_dang_ky_admin_boi_user_nem_PermissionDeniedError(self):
        user = self.auth.dang_ky("an01", "matkhau123")
        with self.assertRaises(PermissionDeniedError):
            self.auth.dang_ky("quantri2", "matkhau123", vai_tro="admin", nguoi_thuc_hien=user)

    def test_dang_ky_admin_boi_admin_thanh_cong(self):
        admin = self.auth.dang_nhap("admin", "admin123")
        moi = self.auth.dang_ky("quantri2", "matkhau123", vai_tro="admin", nguoi_thuc_hien=admin)
        self.assertTrue(moi.la_admin())

    def test_dang_ky_ghi_file_loi_thi_hoan_tac_khong_con_tai_khoan(self):
        kho = KhoGia()
        auth = AuthService(kho)
        kho.loi = True
        with self.assertRaises(StorageError):
            auth.dang_ky("an01", "matkhau123")
        with self.assertRaises(AuthenticationError):   # tài khoản không tồn tại
            auth.dang_nhap("an01", "matkhau123")

    # ---- dang_nhap / dang_xuat ----
    def test_dang_nhap_thanh_cong_gan_tai_khoan_hien_tai(self):
        self.auth.dang_ky("an01", "matkhau123")
        tk = self.auth.dang_nhap("AN01", "matkhau123")     # không phân biệt hoa thường
        self.assertIs(self.auth.tai_khoan_hien_tai, tk)

    def test_dang_nhap_sai_mat_khau_va_sai_username_cung_mot_thong_bao(self):
        self.auth.dang_ky("an01", "matkhau123")
        with self.assertRaises(AuthenticationError) as sai_mk:
            self.auth.dang_nhap("an01", "saimatkhau")
        with self.assertRaises(AuthenticationError) as sai_ten:
            self.auth.dang_nhap("khongco", "matkhau123")
        self.assertEqual(sai_mk.exception.thong_bao, sai_ten.exception.thong_bao)
        self.assertIsNone(self.auth.tai_khoan_hien_tai)

    def test_dang_nhap_rong_hoac_khong_phai_chuoi_nem_InvalidDataError(self):
        for username, mat_khau in (("", "abc123"), ("an01", ""), ("   ", "abc123"), (None, "abc123"), ("an01", 123)):
            with self.assertRaises(InvalidDataError):
                self.auth.dang_nhap(username, mat_khau)

    def test_dang_xuat(self):
        self.auth.dang_nhap("admin", "admin123")
        self.auth.dang_xuat()
        self.assertIsNone(self.auth.tai_khoan_hien_tai)
        self.auth.dang_xuat()                               # gọi lần nữa không lỗi

    # ---- doi_mat_khau ----
    def test_doi_mat_khau_chua_dang_nhap_nem_PermissionDeniedError(self):
        with self.assertRaises(PermissionDeniedError):
            self.auth.doi_mat_khau("admin123", "matkhaumoi")

    def test_doi_mat_khau_sai_mat_khau_cu_nem_AuthenticationError(self):
        self.auth.dang_nhap("admin", "admin123")
        with self.assertRaises(AuthenticationError):
            self.auth.doi_mat_khau("sai_mk_cu", "matkhaumoi")

    def test_doi_mat_khau_moi_yeu_hoac_trung_cu_nem_InvalidDataError(self):
        self.auth.dang_nhap("admin", "admin123")
        with self.assertRaises(InvalidDataError):
            self.auth.doi_mat_khau("admin123", "123")
        with self.assertRaises(InvalidDataError):
            self.auth.doi_mat_khau("admin123", "admin123")

    def test_doi_mat_khau_thanh_cong_mat_khau_cu_het_dung_va_duoc_luu_file(self):
        self.auth.dang_nhap("admin", "admin123")
        self.auth.doi_mat_khau("admin123", "matkhaumoi")
        self.auth.dang_xuat()
        with self.assertRaises(AuthenticationError):
            self.auth.dang_nhap("admin", "admin123")
        self.auth.dang_nhap("admin", "matkhaumoi")
        # nạp lại từ file: mật khẩu mới vẫn đúng
        auth_moi = AuthService(self.storage)
        self.assertTrue(auth_moi.dang_nhap("admin", "matkhaumoi").la_admin())

    def test_doi_mat_khau_ghi_file_loi_thi_mat_khau_cu_van_dung(self):
        kho = KhoGia()
        auth = AuthService(kho)
        auth.dang_nhap("admin", "admin123")
        kho.loi = True
        with self.assertRaises(StorageError):
            auth.doi_mat_khau("admin123", "matkhaumoi")
        kho.loi = False
        auth.dang_xuat()
        auth.dang_nhap("admin", "admin123")                 # mật khẩu cũ vẫn dùng được

    # ---- co_quyen / yeu_cau_quyen ----
    def test_chua_dang_nhap_khong_co_quyen_nao(self):
        self.assertFalse(self.auth.co_quyen("phong.xem"))
        self.assertFalse(self.auth.co_quyen("phong.ghi"))

    def test_user_chi_co_quyen_xem_va_doi_mat_khau(self):
        self.auth.dang_ky("an01", "matkhau123", ma_sv="2100000001")
        self.auth.dang_nhap("an01", "matkhau123")
        for hanh_dong in ("phong.xem", "tim_kiem", "hoadon.xem", "sinhvien.xem", "taikhoan.doi_mat_khau"):
            self.assertTrue(self.auth.co_quyen(hanh_dong), hanh_dong)
        for hanh_dong in ("phong.ghi", "sinhvien.ghi", "hopdong.ghi", "hoadon.ghi", "vipham.ghi",
                          "xep_phong", "thongke.xem", "baocao.xuat", "dulieu.nap_mau", "crawl",
                          "taikhoan.tao_admin"):
            self.assertFalse(self.auth.co_quyen(hanh_dong), hanh_dong)

    def test_admin_co_moi_quyen_trong_ma_tran(self):
        self.auth.dang_nhap("admin", "admin123")
        for hanh_dong in ("phong.xem", "phong.ghi", "xep_phong", "thongke.xem", "crawl", "taikhoan.tao_admin"):
            self.assertTrue(self.auth.co_quyen(hanh_dong), hanh_dong)

    def test_hanh_dong_la_hoac_khong_phai_chuoi_tra_False(self):
        self.auth.dang_nhap("admin", "admin123")
        self.assertFalse(self.auth.co_quyen("bay_len_mat_trang"))
        self.assertFalse(self.auth.co_quyen(None))

    def test_user_xoa_phong_bi_chan_boi_yeu_cau_quyen(self):          # test case 12
        self.auth.dang_ky("an01", "matkhau123")
        self.auth.dang_nhap("an01", "matkhau123")
        with self.assertRaises(PermissionDeniedError):
            self.auth.yeu_cau_quyen("phong.ghi")

    def test_yeu_cau_quyen_khi_chua_dang_nhap_nem_PermissionDeniedError(self):
        with self.assertRaises(PermissionDeniedError):
            self.auth.yeu_cau_quyen("phong.xem")

    def test_yeu_cau_quyen_admin_khong_nem_loi(self):
        self.auth.dang_nhap("admin", "admin123")
        self.assertIsNone(self.auth.yeu_cau_quyen("phong.ghi"))

    # ---- dữ liệu file ----
    def test_ban_ghi_hong_bi_bo_qua_khong_lam_sap(self):
        admin = TaiKhoan.tao("admin", "admin123", "admin")
        kho = KhoGia()
        kho.du_lieu = [{"username": "hong"}, "không phải dict", admin.to_dict()]
        auth = AuthService(kho)
        self.assertTrue(auth.dang_nhap("admin", "admin123").la_admin())
        with self.assertRaises(AuthenticationError):
            auth.dang_nhap("hong", "matkhau123")

    def test_du_lieu_tai_khoan_duoc_luu_va_nap_lai(self):
        self.auth.dang_ky("an01", "matkhau123", ma_sv="2100000001")
        auth_moi = AuthService(self.storage)
        tk = auth_moi.dang_nhap("an01", "matkhau123")
        self.assertEqual(tk.ma_sv, "2100000001")


if __name__ == "__main__":
    unittest.main()