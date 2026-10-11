"""Tài khoản đăng nhập (phần B4, mục 4.7 của Hợp đồng hàm và lỗi).

Mật khẩu không bao giờ được lưu thô: chỉ lưu chuỗi băm có dạng
    pbkdf2_sha256$<số vòng>$<salt hex>$<hash hex>
TaiKhoan là đối tượng bất biến: muốn đổi mật khẩu thì tạo TaiKhoan mới
(xem AuthService.doi_mat_khau).
"""
import hashlib
import hmac
import secrets

import config
from exceptions import InvalidDataError
from utils import validators

VAI_TRO_ADMIN = "admin"   # quản trị viên
VAI_TRO_USER = "user"     # người dùng thường
DANH_SACH_VAI_TRO = (VAI_TRO_ADMIN, VAI_TRO_USER)
TIEN_TO_BAM = "pbkdf2_sha256"


class TaiKhoan:
    """Một tài khoản: username, chuỗi băm mật khẩu, vai trò, mã sinh viên (nếu có)."""

    def __init__(self, username, mat_khau_bam, vai_tro, ma_sv=None):
        """Tạo tài khoản từ chuỗi băm đã có (dùng khi đọc file). Muốn tạo từ
        mật khẩu gốc hãy dùng TaiKhoan.tao().

        Ném lỗi:
            InvalidDataError: username, chuỗi băm, vai trò hoặc ma_sv sai.
        """
        self._username = self._chuan_hoa_username(username)
        self._mat_khau_bam = self._kiem_tra_chuoi_bam(mat_khau_bam)
        self._vai_tro = self._kiem_tra_vai_tro(vai_tro)
        self._ma_sv = self._chuan_hoa_ma_sv(ma_sv)

    # ---------- các hàm kiểm tra dùng trong constructor ----------
    @staticmethod
    def _chuan_hoa_username(username):
        if not isinstance(username, str):
            raise InvalidDataError("Tên đăng nhập phải là chuỗi", "username")
        ten = username.strip().lower()           # lưu chữ thường
        if not validators.hop_le_username(ten):
            raise InvalidDataError(
                "Tên đăng nhập gồm 3-20 ký tự: chữ thường không dấu, số hoặc dấu gạch dưới",
                "username")
        return ten

    @staticmethod
    def _kiem_tra_chuoi_bam(chuoi):
        loi = InvalidDataError("Chuỗi băm mật khẩu không đúng định dạng", "mat_khau_bam")
        if not isinstance(chuoi, str):
            raise loi
        phan = chuoi.split("$")
        if len(phan) != 4 or phan[0] != TIEN_TO_BAM:
            raise loi
        try:
            so_vong = int(phan[1])
            bytes.fromhex(phan[2])
            bytes.fromhex(phan[3])
        except ValueError:
            raise loi
        if so_vong <= 0:
            raise loi
        return chuoi

    @staticmethod
    def _kiem_tra_vai_tro(vai_tro):
        if vai_tro not in DANH_SACH_VAI_TRO:
            raise InvalidDataError("Vai trò chỉ được là admin hoặc user", "vai_tro")
        return vai_tro

    @staticmethod
    def _chuan_hoa_ma_sv(ma_sv):
        if ma_sv is None:                        # admin không gắn với sinh viên nào
            return None
        if not isinstance(ma_sv, str):
            raise InvalidDataError("Mã sinh viên phải là chuỗi", "ma_sv")
        ma = ma_sv.strip().upper()
        if not validators.hop_le_ma_sv(ma):
            raise InvalidDataError("Mã sinh viên không đúng định dạng", "ma_sv")
        return ma

    # ---------- thuộc tính chỉ đọc ----------
    @property
    def username(self):
        return self._username

    @property
    def mat_khau_bam(self):
        return self._mat_khau_bam

    @property
    def vai_tro(self):
        return self._vai_tro

    @property
    def ma_sv(self):
        return self._ma_sv

    def la_admin(self):
        """Trả về True nếu là quản trị viên."""
        return self._vai_tro == VAI_TRO_ADMIN

    # ---------- băm và kiểm tra mật khẩu ----------
    @classmethod
    def tao(cls, username, mat_khau, vai_tro=VAI_TRO_USER, ma_sv=None):
        """Tạo tài khoản mới từ mật khẩu gốc (băm ngay, không giữ mật khẩu gốc).

        Trả về:
            TaiKhoan mới.
        Ném lỗi:
            InvalidDataError: mật khẩu không phải chuỗi hoặc ngắn hơn
                config.MAT_KHAU_TOI_THIEU; hoặc username, vai trò, ma_sv sai.
        """
        if not isinstance(mat_khau, str) or len(mat_khau) < config.MAT_KHAU_TOI_THIEU:
            raise InvalidDataError(
                "Mật khẩu phải có ít nhất " + str(config.MAT_KHAU_TOI_THIEU) + " ký tự",
                "mat_khau")
        salt = secrets.token_bytes(16)           # muối ngẫu nhiên 16 byte
        so_vong = config.PBKDF2_SO_VONG
        hash_bytes = hashlib.pbkdf2_hmac("sha256", mat_khau.encode("utf-8"), salt, so_vong)
        chuoi_bam = TIEN_TO_BAM + "$" + str(so_vong) + "$" + salt.hex() + "$" + hash_bytes.hex()
        return cls(username, chuoi_bam, vai_tro, ma_sv)

    def kiem_tra_mat_khau(self, mat_khau):
        """Kiểm tra mật khẩu gốc có khớp chuỗi băm đã lưu không.

        Trả về:
            True nếu đúng; False nếu sai hoặc không phải chuỗi.
            Hàm này không bao giờ ném lỗi.
        """
        if not isinstance(mat_khau, str):
            return False
        phan = self._mat_khau_bam.split("$")
        try:
            so_vong = int(phan[1])
            salt = bytes.fromhex(phan[2])
            hash_dung = bytes.fromhex(phan[3])
            hash_thu = hashlib.pbkdf2_hmac("sha256", mat_khau.encode("utf-8"), salt, so_vong)
        except (ValueError, IndexError):
            return False
        # compare_digest so sánh an toàn, tránh lộ thông tin qua thời gian so sánh
        return hmac.compare_digest(hash_thu, hash_dung)

    # ---------- chuyển qua lại với JSON ----------
    def to_dict(self):
        """Trả về dict thuần JSON (chỉ có chuỗi băm, không có mật khẩu gốc)."""
        return {
            "username": self._username,
            "mat_khau_bam": self._mat_khau_bam,
            "vai_tro": self._vai_tro,
            "ma_sv": self._ma_sv,
        }

    @classmethod
    def tu_dict(cls, d):
        """Dựng lại TaiKhoan từ dict đọc từ file.

        Ném lỗi:
            InvalidDataError: d không phải dict, thiếu trường hoặc giá trị sai.
        """
        if not isinstance(d, dict):
            raise InvalidDataError("Bản ghi tài khoản phải là một dict", None)
        for khoa in ("username", "mat_khau_bam", "vai_tro"):
            if khoa not in d:
                raise InvalidDataError("Thiếu trường " + khoa, khoa)
        return cls(d["username"], d["mat_khau_bam"], d["vai_tro"], d.get("ma_sv"))

    def __str__(self):
        return self._username + " (" + self._vai_tro + ")"