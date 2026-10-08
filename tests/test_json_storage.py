import json
import os
import tempfile
import unittest

from exceptions import StorageError
from storage.json_storage import JsonStorage


class TestJsonStorage(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.p = os.path.join(self.tmp.name, "data", "x.json")   # thư mục data chưa có
        self.bk = os.path.join(self.tmp.name, "bk")
        self.s = JsonStorage(self.p, [], self.bk)

    def tearDown(self):
        self.tmp.cleanup()

    def _viet(self, noi_dung, ma="utf-8"):
        os.makedirs(os.path.dirname(self.p), exist_ok=True)
        with open(self.p, "w", encoding=ma) as f:
            f.write(noi_dung)

    def test_file_thieu_tu_tao(self):                          # test case 9
        self.assertEqual(self.s.doc(), [])
        self.assertTrue(os.path.exists(self.p))

    def test_file_rong(self):
        self._viet("")
        self.assertEqual(self.s.doc(), [])
        self._viet("   \n ")
        self.assertEqual(self.s.doc(), [])

    def test_ghi_roi_doc_lai(self):
        du_lieu = [{"ma_sv": "2100000001", "ho_ten": "Nguyễn Văn An"}]
        self.s.ghi(du_lieu)
        self.assertEqual(self.s.doc(), du_lieu)

    def test_giu_tieng_viet_trong_file(self):
        self.s.ghi([{"ten": "Trần Thị Bé"}])
        with open(self.p, encoding="utf-8") as f:
            self.assertIn("Trần Thị Bé", f.read())             # không bị \u escape

    def test_json_hong_khoi_phuc_tu_backup(self):              # test case 10
        self.s.ghi([{"a": 1}])
        self.s.ghi([{"a": 2}])                                 # backup giữ bản a=1
        self._viet('[{"a": 2} {"a": 3}]')                      # thiếu dấu phẩy
        self.assertEqual(self.s.doc(), [{"a": 1}])
        self.assertTrue(os.path.exists(self.p + ".loi"))       # bản hỏng được giữ lại
        self.assertEqual(self.s.doc(), [{"a": 1}])             # file chính đã được sửa

    def test_json_hong_khong_co_backup_dung_mac_dinh(self):
        mac_dinh = [{"ma": "MD"}]
        s = JsonStorage(self.p, mac_dinh, self.bk)
        self._viet("{hong")
        self.assertEqual(s.doc(), mac_dinh)

    def test_goc_khong_phai_list_la_hong(self):
        self._viet(json.dumps({"khong": "phai list"}))
        self.assertEqual(self.s.doc(), [])

    def test_file_sai_bang_ma(self):
        os.makedirs(os.path.dirname(self.p), exist_ok=True)
        with open(self.p, "wb") as f:
            f.write("[\"Nguyễn\"]".encode("utf-16"))           # không phải UTF-8
        self.assertEqual(self.s.doc(), [])

    def test_file_notepad_utf8_bom(self):
        self._viet('[{"ten": "An"}]', ma="utf-8-sig")          # Notepad "UTF-8 with BOM"
        self.assertEqual(self.s.doc(), [{"ten": "An"}])

    def test_ban_hong_khong_de_len_backup_tot(self):
        self.s.ghi([1])
        self.s.ghi([2])                                        # backup = [1]
        self._viet("{hong")
        self.s.ghi([3])                                        # bản hỏng KHÔNG được chép vào backup
        with open(os.path.join(self.bk, "x.json.bak"), encoding="utf-8") as f:
            self.assertEqual(json.load(f), [1])

    def test_mac_dinh_la_ban_sao(self):
        s = JsonStorage(self.p, [{"a": 1}], self.bk)
        ds = s.doc()
        ds.append({"b": 2})
        ds[0]["a"] = 99
        self.assertEqual(s.mac_dinh, [{"a": 1}])               # mặc định không bị sửa chung

    def test_ghi_khong_de_lai_file_tam(self):
        self.s.ghi([1])
        self.assertFalse(os.path.exists(self.p + ".tmp"))

    def test_ghi_loi_du_lieu_khong_serialize_duoc(self):
        self.s.ghi([1])
        with self.assertRaises(StorageError):
            self.s.ghi([object()])
        self.assertEqual(self.s.doc(), [1])                    # file cũ còn nguyên

    def test_ghi_loi_he_thong_thanh_storage_error(self):
        # duong_dan trỏ vào "thư mục" nằm dưới một FILE => không tạo được
        chan = os.path.join(self.tmp.name, "la_file")
        with open(chan, "w") as f:
            f.write("x")
        s = JsonStorage(os.path.join(chan, "con", "x.json"), [], self.bk)
        with self.assertRaises(StorageError):
            s.ghi([1])


if __name__ == "__main__":
    unittest.main()