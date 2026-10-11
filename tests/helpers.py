"""Hàm dùng chung cho các test của managers (thư mục tạm, storage giả bị lỗi)."""
import os
import tempfile
import unittest

from exceptions import StorageError
from storage.json_storage import JsonStorage


class LoiStorage(JsonStorage):
    """JsonStorage thật, nhưng có thể bật chế độ ghi lỗi để thử hoàn tác."""
    ghi_loi = False

    def ghi(self, du_lieu):
        if self.ghi_loi:
            raise StorageError("Giả lập ghi file lỗi")
        super().ghi(du_lieu)


class TestCoThuMuc(unittest.TestCase):
    """Lớp nền cho test: mỗi test có một thư mục tạm riêng."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = tmp.name

    def storage(self, ten="du_lieu.json"):
        return LoiStorage(os.path.join(self.dir, ten), mac_dinh=[],
                          thu_muc_backup=os.path.join(self.dir, "backup"))