class KtxError(Exception):
    """Lớp cha của mọi lỗi nghiệp vụ trong ứng dụng ký túc xá."""

    def __init__(self, thong_bao, truong=None):
        super().__init__(thong_bao)
        self.thong_bao = thong_bao
        self.truong = truong


class InvalidDataError(KtxError):
    """Dữ liệu sai: trống, sai định dạng, ngoài khoảng, vi phạm ràng buộc."""


class DuplicateIdError(KtxError):
    """Mã (ma_sv, ma_phong, ma_hd, ...) đã tồn tại."""


class NotFoundError(KtxError):
    """Không tìm thấy đối tượng theo mã."""


class RoomFullError(KtxError):
    """Phòng đã hết chỗ."""


# --- Hai lỗi mở rộng cho đăng nhập/phân quyền và ghi file ---
class AuthenticationError(KtxError):
    """Sai tên đăng nhập hoặc mật khẩu (không tiết lộ sai cái nào)."""


class PermissionDeniedError(KtxError):
    """Vai trò hiện tại không được dùng chức năng này."""


class StorageError(KtxError):
    """Không ghi được file dữ liệu (đầy đĩa, không có quyền, file đang bị khóa)."""