"""Kiểm thử managers/co_so.py (qua QuanLyPhong, một lớp con cụ thể).
    python -m unittest tests.test_co_so -v
"""
import json

from exceptions import (InvalidDataError, DuplicateIdError, NotFoundError, StorageError)
from managers.quan_ly_phong import QuanLyPhong
from models.phong import PhongThuong, PhongMayLanh
from tests.helpers import TestCoThuMuc


class TestCoSo(TestCoThuMuc):
    def setUp(self):
        super().setUp()
        self.st = self.storage()
        self.ql = QuanLyPhong(self.st)
        self.ql.them(PhongThuong("A101", 4, 400000))
        self.ql.them(PhongMayLanh("B202", 6, 500000))

    def _file(self):
        with open(self.st.duong_dan, encoding="utf-8") as f:
            return json.load(f)

    # ---- them ----
    def test_them_va_len(self):
        self.assertEqual(len(self.ql), 2)
        self.assertTrue(self.ql.co("a101"))

    def test_them_ghi_file(self):
        self.assertEqual([d["ma_phong"] for d in self._file()], ["A101", "B202"])

    def test_them_trung_ma(self):
        with self.assertRaises(DuplicateIdError):
            self.ql.them(PhongThuong("A101", 2, 1))
        self.assertEqual(len(self.ql), 2)

    def test_them_sai_kieu(self):
        for v in ("A101", None, {"ma_phong": "A103"}):
            with self.subTest(v=v):
                with self.assertRaises(InvalidDataError):
                    self.ql.them(v)

    def test_them_loi_ghi_file_thi_hoan_tac(self):
        self.st.ghi_loi = True
        with self.assertRaises(StorageError):
            self.ql.them(PhongThuong("C303", 4, 1))
        self.assertEqual(len(self.ql), 2)
        self.assertFalse(self.ql.co("C303"))

    # ---- tim ----
    def test_tim_theo_ma_khong_phan_biet_hoa_thuong(self):
        self.assertEqual(self.ql.tim_theo_ma(" a101 ").ma_phong, "A101")

    def test_tim_theo_ma_khong_co(self):
        with self.assertRaises(NotFoundError):
            self.ql.tim_theo_ma("Z999")

    def test_tim_theo_ma_rong_hoac_sai_kieu(self):
        for v in ("", "  ", None, 5):
            with self.subTest(v=v):
                with self.assertRaises(InvalidDataError):
                    self.ql.tim_theo_ma(v)

    def test_co_khong_nem_loi(self):
        self.assertFalse(self.ql.co(None))
        self.assertFalse(self.ql.co("Z999"))

    def test_tim_theo_tieu_chi_chuoi_la_chua_chuoi_con(self):
        self.assertEqual([p.ma_phong for p in self.ql.tim_theo_tieu_chi(loai="MAY")], ["B202"])

    def test_tim_theo_tieu_chi_so_la_bang(self):
        self.assertEqual([p.ma_phong for p in self.ql.tim_theo_tieu_chi(so_cho=4)], ["A101"])

    def test_tim_nhieu_tieu_chi_la_AND(self):
        self.assertEqual(self.ql.tim_theo_tieu_chi(loai="maylanh", so_cho=4), [])
        self.assertEqual(len(self.ql.tim_theo_tieu_chi(loai="maylanh", so_cho=6)), 1)

    def test_tieu_chi_la_khong_phai_thuoc_tinh(self):
        for ten in ("abc", "_so_cho", "tinh_phi_o_khong_co"):
            with self.subTest(ten=ten):
                with self.assertRaises(InvalidDataError):
                    self.ql.tim_theo_tieu_chi(**{ten: 1})

    def test_tim_khong_thay_tra_list_rong(self):
        self.assertEqual(self.ql.tim_theo_tieu_chi(so_cho=99), [])

    # ---- lay_tat_ca ----
    def test_lay_tat_ca_tra_list_moi(self):
        a = self.ql.lay_tat_ca()
        a.clear()
        self.assertEqual(len(self.ql.lay_tat_ca()), 2)

    def test_sap_xep(self):
        self.assertEqual([p.ma_phong for p in self.ql.lay_tat_ca("gia_co_ban", True)],
                         ["B202", "A101"])
        self.assertEqual([p.ma_phong for p in self.ql.lay_tat_ca(dao_nguoc=True)],
                         ["B202", "A101"])

    def test_sap_xep_khoa_la(self):
        with self.assertRaises(InvalidDataError):
            self.ql.lay_tat_ca("khong_co")

    # ---- sua ----
    def test_sua_thanh_cong_ghi_file(self):
        p = self.ql.sua("A101", gia_co_ban=450000)
        self.assertEqual(p.gia_co_ban, 450000)
        self.assertEqual(self.ql.tim_theo_ma("A101").gia_co_ban, 450000)
        self.assertEqual(self._file()[0]["gia_co_ban"], 450000)

    def test_sua_sai_thi_du_lieu_cu_nguyen_ven(self):
        with self.assertRaises(InvalidDataError):
            self.ql.sua("A101", so_cho=6, gia_co_ban=-1)
        p = self.ql.tim_theo_ma("A101")
        self.assertEqual((p.so_cho, p.gia_co_ban), (4, 400000))

    def test_sua_khong_co_gi(self):
        with self.assertRaises(InvalidDataError):
            self.ql.sua("A101")

    def test_sua_doi_ma(self):
        for kw in ({"ma_phong": "A999"}, {"ma": "A999"}):
            with self.subTest(kw=kw):
                with self.assertRaises(InvalidDataError):
                    self.ql.sua("A101", **kw)

    def test_sua_truong_la(self):
        with self.assertRaises(InvalidDataError):
            self.ql.sua("A101", mau_son="xanh")

    def test_sua_khong_co_ma(self):
        with self.assertRaises(NotFoundError):
            self.ql.sua("Z999", so_cho=3)

    def test_sua_loi_ghi_file_thi_hoan_tac(self):
        self.st.ghi_loi = True
        with self.assertRaises(StorageError):
            self.ql.sua("A101", gia_co_ban=1)
        self.assertEqual(self.ql.tim_theo_ma("A101").gia_co_ban, 400000)

    # ---- xoa ----
    def test_xoa(self):
        p = self.ql.xoa("a101")
        self.assertEqual(p.ma_phong, "A101")
        self.assertEqual(len(self.ql), 1)
        self.assertEqual(len(self._file()), 1)

    def test_xoa_khong_co(self):
        with self.assertRaises(NotFoundError):
            self.ql.xoa("Z999")

    def test_xoa_ma_rong(self):
        with self.assertRaises(InvalidDataError):
            self.ql.xoa("")

    def test_xoa_loi_ghi_file_thi_hoan_tac(self):
        self.st.ghi_loi = True
        with self.assertRaises(StorageError):
            self.ql.xoa("A101")
        self.assertTrue(self.ql.co("A101"))

    # ---- tải lại từ file ----
    def test_nap_lai_tu_file_dung_lop_con(self):
        ql2 = QuanLyPhong(self.storage())
        self.assertEqual(len(ql2), 2)
        self.assertIsInstance(ql2.tim_theo_ma("B202"), PhongMayLanh)

    def test_file_co_ban_ghi_hong_va_trung_thi_bo_qua(self):
        tot = {"ma_phong": "C303", "loai": "thuong", "so_cho": 4,
               "gia_co_ban": 1, "danh_sach_sv": []}
        with open(self.st.duong_dan, "w", encoding="utf-8") as f:
            json.dump([tot, dict(tot),                          # trùng mã
                       {"ma_phong": "A1", "loai": "thuong"},   # thiếu trường + sai mã
                       {"ma_phong": "D404", "loai": "vip", "so_cho": 2, "gia_co_ban": 1},
                       "rac", None, 123], f)
        ql2 = QuanLyPhong(self.storage())
        self.assertEqual([p.ma_phong for p in ql2.lay_tat_ca()], ["C303"])
        self.assertEqual(len(ql2.ban_ghi_loi), 6)
        self.assertTrue(all("ly_do" in b for b in ql2.ban_ghi_loi))

    def test_file_hong_khong_co_backup_van_chay(self):
        import shutil
        shutil.rmtree(self.st.thu_muc_backup, ignore_errors=True)
        with open(self.st.duong_dan, "w", encoding="utf-8") as f:
            f.write("{hong")
        self.assertEqual(len(QuanLyPhong(self.storage())), 0)

    def test_file_hong_co_backup_thi_khoi_phuc(self):
        with open(self.st.duong_dan, "w", encoding="utf-8") as f:
            f.write("{hong")
        self.assertEqual(len(QuanLyPhong(self.storage())), 1)   # backup là lần ghi trước đó

    def test_file_bi_xoa_van_chay(self):
        import os
        os.remove(self.st.duong_dan)
        self.assertEqual(len(QuanLyPhong(self.storage())), 0)