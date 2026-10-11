"""Kiểm thử QuanLySinhVien (B3). Chạy: python -m unittest tests.test_quan_ly_sinh_vien -v"""
import os
import tempfile
import unittest

from exceptions import DuplicateIdError, InvalidDataError
from managers.quan_ly_sinh_vien import QuanLySinhVien
from models.sinh_vien import SinhVien
from storage.json_storage import JsonStorage


def tao_storage(thu_muc, ten_file):
    """Storage tạm trong thư mục riêng để test không đụng vào data/ thật."""
    return JsonStorage(os.path.join(thu_muc, ten_file), mac_dinh=[],
                       thu_muc_backup=os.path.join(thu_muc, "backup"))


def tao_sv(ma, ho_ten, lop="DH21CNTT"):
    return SinhVien(ma, ho_ten, "15/03/2005", "0912345678", lop)


class TestQuanLySinhVien(unittest.TestCase):
    def setUp(self):
        tam = tempfile.TemporaryDirectory()
        self.addCleanup(tam.cleanup)
        self.storage = tao_storage(tam.name, "sinhvien.json")
        self.ql = QuanLySinhVien(self.storage)
        self.ql.them(tao_sv("2100000001", "Nguyễn Văn An", "DH21CNTT"))
        self.ql.them(tao_sv("2100000002", "Lý Mỹ Linh", "DH21KT"))
        self.ql.them(tao_sv("2100000003", "Trần Quốc Bảo", "DH21CNTT"))

    def ma_cua(self, ds):
        """Lấy danh sách mã của các sinh viên (giữ nguyên thứ tự thêm vào)."""
        return [sv.ma for sv in ds]

    # ---- tim_theo_ten ----
    def test_tim_theo_ten_khong_phan_biet_hoa_thuong(self):
        self.assertEqual(self.ma_cua(self.ql.tim_theo_ten("aN")), ["2100000001"])

    def test_tim_theo_ten_mot_phan_cua_ten(self):
        self.assertEqual(self.ma_cua(self.ql.tim_theo_ten("linh")), ["2100000002"])

    def test_tim_theo_ten_bo_khoang_trang_hai_dau(self):
        self.assertEqual(self.ma_cua(self.ql.tim_theo_ten("  BẢO ")), ["2100000003"])

    def test_tim_theo_ten_nhieu_ket_qua(self):
        # "n" có trong cả ba họ tên (Nguyễn, Lý Mỹ Linh, Trần)
        self.assertEqual(len(self.ql.tim_theo_ten("n")), 3)

    def test_tim_theo_ten_khong_khop_tra_list_rong(self):
        self.assertEqual(self.ql.tim_theo_ten("zzz"), [])

    def test_tim_theo_ten_rong_nem_InvalidDataError(self):
        with self.assertRaises(InvalidDataError):
            self.ql.tim_theo_ten("   ")

    def test_tim_theo_ten_khong_phai_chuoi_nem_InvalidDataError(self):
        with self.assertRaises(InvalidDataError):
            self.ql.tim_theo_ten(None)

    # ---- phần thừa kế từ lớp nền (kiểm tra việc khai báo đúng) ----
    def test_them_trung_ma_nem_DuplicateIdError(self):
        with self.assertRaises(DuplicateIdError):
            self.ql.them(tao_sv("2100000001", "Người Khác"))
        self.assertEqual(len(self.ql.lay_tat_ca()), 3)

    def test_tim_theo_tieu_chi_ho_ten_va_lop(self):
        ds = self.ql.tim_theo_tieu_chi(ho_ten="n", lop="DH21CNTT")
        self.assertEqual(self.ma_cua(ds), ["2100000001", "2100000003"])

    def test_du_lieu_duoc_luu_va_nap_lai(self):
        ql_moi = QuanLySinhVien(self.storage)
        self.assertEqual(len(ql_moi.lay_tat_ca()), 3)


if __name__ == "__main__":
    unittest.main()