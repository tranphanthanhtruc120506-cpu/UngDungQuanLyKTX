"""Kiểm thử managers/quan_ly_phong.py (A7).
    python -m unittest tests.test_quan_ly_phong -v
"""
from exceptions import (InvalidDataError, DuplicateIdError, NotFoundError,
                        RoomFullError, StorageError)
from managers.quan_ly_phong import QuanLyPhong
from models.phong import PhongThuong, PhongMayLanh
from tests.helpers import TestCoThuMuc
import config

SV = ["21000000%02d" % i for i in range(1, 10)]     # 2100000001 ... 2100000009


class TestQuanLyPhong(TestCoThuMuc):
    def setUp(self):
        super().setUp()
        self.st = self.storage()
        self.ql = QuanLyPhong(self.st)
        self.ql.them(PhongThuong("A101", 2, 400000))      # sẽ để trống
        self.ql.them(PhongMayLanh("A102", 2, 400000))     # sẽ có 1 người
        self.ql.them(PhongThuong("B201", 2, 300000))      # sẽ đầy
        self.ql.them_sv_vao_phong("A102", SV[0])
        self.ql.them_sv_vao_phong("B201", SV[1])
        self.ql.them_sv_vao_phong("B201", SV[2])

    def ma(self, ds):
        return [p.ma_phong for p in ds]

    # ---- xếp chỗ: tiêu chí "xếp quá số chỗ bị từ chối" ----
    def test_xep_qua_so_cho_bi_tu_choi(self):
        with self.assertRaises(RoomFullError):
            self.ql.them_sv_vao_phong("B201", SV[3])
        self.assertEqual(len(self.ql.tim_theo_ma("B201")), 2)      # không ai bị thêm

    def test_xep_nguoi_cuoi_cung_thanh_cong(self):
        p = self.ql.them_sv_vao_phong("A102", SV[3])
        self.assertTrue(p.da_day())

    def test_xep_trung_sv_trong_phong(self):
        with self.assertRaises(DuplicateIdError):
            self.ql.them_sv_vao_phong("A102", SV[0])

    def test_xep_phong_khong_ton_tai(self):
        with self.assertRaises(NotFoundError):
            self.ql.them_sv_vao_phong("Z999", SV[3])

    def test_xep_ma_sv_sai(self):
        for v in ("abc", "", None):
            with self.subTest(v=v):
                with self.assertRaises(InvalidDataError):
                    self.ql.them_sv_vao_phong("A101", v)

    def test_xep_ghi_vao_file(self):
        QuanLyPhong(self.storage()).tim_theo_ma("A102")             # nạp lại không lỗi
        self.assertTrue(QuanLyPhong(self.storage()).tim_theo_ma("A102").co_sv(SV[0]))

    def test_xep_loi_ghi_file_thi_hoan_tac(self):
        self.st.ghi_loi = True
        with self.assertRaises(StorageError):
            self.ql.them_sv_vao_phong("A101", SV[5])
        self.assertEqual(len(self.ql.tim_theo_ma("A101")), 0)

    # ---- bỏ chỗ ----
    def test_bo_sv(self):
        p = self.ql.bo_sv_khoi_phong("B201", SV[1])
        self.assertFalse(p.co_sv(SV[1]))
        self.assertEqual(p.con_cho(), 1)

    def test_bo_sv_khong_o_phong_do(self):
        with self.assertRaises(NotFoundError):
            self.ql.bo_sv_khoi_phong("A101", SV[1])

    def test_bo_sv_phong_khong_ton_tai(self):
        with self.assertRaises(NotFoundError):
            self.ql.bo_sv_khoi_phong("Z999", SV[1])

    def test_bo_roi_xep_lai_duoc(self):
        self.ql.bo_sv_khoi_phong("B201", SV[1])
        self.ql.them_sv_vao_phong("B201", SV[4])
        self.assertEqual(len(self.ql.tim_theo_ma("B201")), 2)

    def test_bo_loi_ghi_file_thi_hoan_tac(self):
        self.st.ghi_loi = True
        with self.assertRaises(StorageError):
            self.ql.bo_sv_khoi_phong("B201", SV[1])
        self.assertTrue(self.ql.tim_theo_ma("B201").co_sv(SV[1]))

    # ---- tìm theo trạng thái ----
    def test_ba_trang_thai(self):
        self.assertEqual(self.ma(self.ql.tim_theo_trang_thai("trong")), ["A101"])
        self.assertEqual(self.ma(self.ql.tim_theo_trang_thai("con_cho")), ["A102"])
        self.assertEqual(self.ma(self.ql.tim_theo_trang_thai("day")), ["B201"])

    def test_trang_thai_la(self):
        for v in ("full", "", None, "TRONG"):
            with self.subTest(v=v):
                with self.assertRaises(InvalidDataError):
                    self.ql.tim_theo_trang_thai(v)

    def test_phong_con_cho_sap_theo_ma(self):
        self.assertEqual(self.ma(self.ql.phong_con_cho()), ["A101", "A102"])

    def test_phong_con_cho_khi_het_sach(self):
        self.ql.them_sv_vao_phong("A101", SV[5])
        self.ql.them_sv_vao_phong("A101", SV[6])
        self.ql.them_sv_vao_phong("A102", SV[7])
        self.assertEqual(self.ql.phong_con_cho(), [])

    # ---- tìm phòng của SV ----
    def test_tim_phong_cua_sv(self):
        self.assertEqual(self.ql.tim_phong_cua_sv(SV[0]).ma_phong, "A102")

    def test_tim_phong_cua_sv_chua_o_dau_tra_None(self):
        self.assertIsNone(self.ql.tim_phong_cua_sv(SV[8]))
        self.assertIsNone(self.ql.tim_phong_cua_sv("abc"))
        self.assertIsNone(self.ql.tim_phong_cua_sv(None))

    # ---- xóa phòng ----
    def test_xoa_phong_con_nguoi(self):
        with self.assertRaises(InvalidDataError) as ctx:
            self.ql.xoa("B201")
        self.assertIn("B201 còn 2 người", str(ctx.exception))
        self.assertTrue(self.ql.co("B201"))

    def test_xoa_phong_trong(self):
        self.ql.xoa("A101")
        self.assertFalse(self.ql.co("A101"))

    def test_xoa_duoc_sau_khi_bo_het_nguoi(self):
        self.ql.bo_sv_khoi_phong("A102", SV[0])
        self.ql.xoa("A102")
        self.assertEqual(len(self.ql), 2)

    # ---- đổi loại ----
    def test_doi_loai_giu_nguyen_sv_va_doi_phi(self):
        p = self.ql.doi_loai("A102", "thuong")
        self.assertIsInstance(p, PhongThuong)
        self.assertEqual(p.danh_sach_sv, (SV[0],))
        self.assertEqual(p.tinh_phi_o(), 400000)

    def test_doi_len_may_lanh_tang_phi(self):
        p = self.ql.doi_loai("A101", "maylanh")
        self.assertIsInstance(p, PhongMayLanh)
        self.assertEqual(p.tinh_phi_o(), 400000 + config.PHU_THU_MAY_LANH)

    def test_doi_loai_la(self):
        with self.assertRaises(InvalidDataError):
            self.ql.doi_loai("A101", "vip")
        self.assertIsInstance(self.ql.tim_theo_ma("A101"), PhongThuong)

    def test_doi_loai_phong_khong_co(self):
        with self.assertRaises(NotFoundError):
            self.ql.doi_loai("Z999", "thuong")

    def test_doi_loai_duoc_ghi_vao_file(self):
        self.ql.doi_loai("A101", "maylanh")
        self.assertIsInstance(QuanLyPhong(self.storage()).tim_theo_ma("A101"), PhongMayLanh)

    def test_doi_loai_loi_ghi_file_thi_hoan_tac(self):
        self.st.ghi_loi = True
        with self.assertRaises(StorageError):
            self.ql.doi_loai("A101", "maylanh")
        self.assertIsInstance(self.ql.tim_theo_ma("A101"), PhongThuong)

    # ---- thống kê ----
    def test_thong_ke(self):
        self.assertEqual(self.ql.thong_ke_phong(), {
            "tong_phong": 3, "tong_cho": 6, "dang_o": 3, "cho_trong": 3,
            "so_phong_trong": 1, "so_phong_day": 1})

    def test_thong_ke_rong(self):
        ql = QuanLyPhong(self.storage("khac.json"))
        self.assertEqual(ql.thong_ke_phong(), {
            "tong_phong": 0, "tong_cho": 0, "dang_o": 0, "cho_trong": 0,
            "so_phong_trong": 0, "so_phong_day": 0})

    def test_sua_so_cho_khong_duoc_thap_hon_nguoi_o(self):
        with self.assertRaises(InvalidDataError):
            self.ql.sua("B201", so_cho=1)
        self.assertEqual(self.ql.tim_theo_ma("B201").so_cho, 2)


if __name__ == "__main__":
    import unittest
    unittest.main(verbosity=2)