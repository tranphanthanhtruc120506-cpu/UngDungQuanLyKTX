import copy
import json
import os
import shutil

import config
from exceptions import StorageError


class JsonStorage:
    def __init__(self, duong_dan, mac_dinh=None, thu_muc_backup=None):
        self.duong_dan = duong_dan                       # đường dẫn file chính
        self.mac_dinh = mac_dinh if mac_dinh is not None else []
        self.thu_muc_backup = thu_muc_backup or config.BACKUP_DIR

    # ------------------------------------------------------------------
    # Hàm công khai
    # ------------------------------------------------------------------
    def doc(self):
        """Trả về list dữ liệu (bản sao riêng, sửa thoải mái)."""
        if not os.path.exists(self.duong_dan):           # file chưa có
            self.ghi(self.mac_dinh)
            return copy.deepcopy(self.mac_dinh)

        du_lieu = self._doc_file(self.duong_dan)
        if du_lieu is None:                              # hỏng hoặc sai kiểu
            return self._khoi_phuc()
        return du_lieu

    def ghi(self, du_lieu):
        """Ghi list xuống file. Lỗi hệ thống -> StorageError."""
        try:
            os.makedirs(os.path.dirname(self.duong_dan) or ".", exist_ok=True)
            self._sao_luu()
            duong_dan_tam = self.duong_dan + ".tmp"
            with open(duong_dan_tam, "w", encoding="utf-8") as f:
                json.dump(du_lieu, f, ensure_ascii=False, indent=2)
            os.replace(duong_dan_tam, self.duong_dan)    # đổi tên nguyên tử
        except (OSError, TypeError, ValueError) as e:
            # OSError: đầy đĩa/khóa file/không quyền; TypeError, ValueError: dữ liệu
            # không chuyển được thành JSON
            raise StorageError(f"Không ghi được file dữ liệu: {e}") from e

    # ------------------------------------------------------------------
    # Hàm nội bộ
    # ------------------------------------------------------------------
    def _doc_file(self, duong_dan):
        """Đọc một file JSON.
        Trả về: list (file rỗng thì trả bản sao mặc định); None nếu hỏng / sai kiểu.
        'utf-8-sig' đọc được cả file lưu từ Notepad kiểu 'UTF-8 with BOM'."""
        try:
            with open(duong_dan, "r", encoding="utf-8-sig") as f:
                noi_dung = f.read().strip()
            if not noi_dung:                              # file rỗng
                return copy.deepcopy(self.mac_dinh)
            du_lieu = json.loads(noi_dung)
        except FileNotFoundError:                         # file biến mất giữa chừng
            return None
        except json.JSONDecodeError:                      # sai cú pháp JSON
            return None
        except UnicodeDecodeError:                        # sai bảng mã (không phải UTF-8)
            return None
        except OSError:                                   # không mở được (quyền, khóa...)
            return None
        if not isinstance(du_lieu, list):                 # JSON đúng nhưng gốc không phải list
            return None
        return du_lieu

    def _duong_dan_backup(self):
        ten_file = os.path.basename(self.duong_dan) + ".bak"
        return os.path.join(self.thu_muc_backup, ten_file)

    def _sao_luu(self):
        """Chép file chính sang backup, NHƯNG chỉ khi file chính còn đọc được.
        Nếu không, bản hỏng sẽ đè mất bản backup tốt."""
        if os.path.exists(self.duong_dan) and self._doc_file(self.duong_dan) is not None:
            os.makedirs(self.thu_muc_backup, exist_ok=True)
            shutil.copy2(self.duong_dan, self._duong_dan_backup())

    def _khoi_phuc(self):
        """File chính hỏng: giữ bản hỏng, lấy từ backup (hoặc mặc định), ghi lại file chính."""
        try:
            os.replace(self.duong_dan, self.duong_dan + ".loi")
        except OSError:
            pass                                          # không đổi tên được cũng không sao
        du_lieu = None
        if os.path.exists(self._duong_dan_backup()):
            du_lieu = self._doc_file(self._duong_dan_backup())
        if du_lieu is None:                               # không có backup dùng được
            du_lieu = copy.deepcopy(self.mac_dinh)
        self.ghi(du_lieu)
        return du_lieu