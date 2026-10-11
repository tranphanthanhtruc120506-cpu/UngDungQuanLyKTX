"""Đăng ký, đăng nhập, đổi mật khẩu và phân quyền (phần B4, mục 7 của Hợp đồng).

Lưu ý quan trọng: QuanLy* và DichVuKtx KHÔNG tự kiểm tra quyền. Giao diện phải
(1) ẩn/vô hiệu hóa nút bằng co_quyen() và (2) gọi yeu_cau_quyen() trong hàm
xử lý nút TRƯỚC khi gọi lớp quản lý.
"""
import logging

import config
from exceptions import (AuthenticationError, DuplicateIdError, InvalidDataError,
                        PermissionDeniedError, StorageError)
from models.tai_khoan import TaiKhoan, VAI_TRO_ADMIN, VAI_TRO_USER
from storage.json_storage import JsonStorage

logger = logging.getLogger(__name__)

# Tài khoản admin đầu tiên (GIẢ ĐỊNH của bài tập, phải ghi vào phần Hạn chế của
# báo cáo và nên đổi mật khẩu ngay sau lần đăng nhập đầu).
ADMIN_MAC_DINH = "admin"
MAT_KHAU_ADMIN_MAC_DINH = "admin123"

# Ma trận quyền (mục 7). Việc "user chỉ xem hóa đơn/hồ sơ của mình" do giao diện
# lọc theo tai_khoan_hien_tai.ma_sv; ở đây chỉ quyết định có được vào chức năng hay không.
HANH_DONG_CHUNG = (
    "phong.xem", "tim_kiem", "hoadon.xem", "sinhvien.xem", "taikhoan.doi_mat_khau",
)
HANH_DONG_RIENG_ADMIN = (
    "phong.ghi", "sinhvien.ghi", "hopdong.ghi", "hoadon.ghi", "vipham.ghi",
    "xep_phong", "thongke.xem", "baocao.xuat", "dulieu.nap_mau", "crawl",
    "taikhoan.tao_admin",
)


class AuthService:
    """Quản lý danh sách tài khoản và người đang đăng nhập."""

    def __init__(self, storage=None):
        """Tham số:
            storage: đối tượng có doc() và ghi(); mặc định là
                JsonStorage(config.FILE_TAI_KHOAN). Chưa có tài khoản hợp lệ nào
                thì tự tạo admin mặc định.
        Ném lỗi:
            StorageError: không ghi được file khi tạo admin mặc định.
        """
        if storage is None:
            storage = JsonStorage(config.FILE_TAI_KHOAN, mac_dinh=[])
        self._storage = storage
        self._ds = []              # danh sách TaiKhoan
        self._hien_tai = None      # TaiKhoan đang đăng nhập (None nếu chưa)

        for ban_ghi in self._storage.doc():
            try:
                tk = TaiKhoan.tu_dict(ban_ghi)
            except InvalidDataError as loi:   # bản ghi hỏng: bỏ qua, ghi log, không sập
                logger.warning("Bỏ qua tài khoản hỏng: %s", loi.thong_bao)
                continue
            if self._tim(tk.username) is None:
                self._ds.append(tk)

        if len(self._ds) == 0:
            admin = TaiKhoan.tao(ADMIN_MAC_DINH, MAT_KHAU_ADMIN_MAC_DINH, VAI_TRO_ADMIN)
            self._ds.append(admin)
            self._luu()

    # ---------- hàm nội bộ ----------
    def _tim(self, username):
        """Tìm tài khoản theo username (không phân biệt hoa thường); không thấy thì trả None."""
        ten = username.strip().lower()
        for tk in self._ds:
            if tk.username == ten:
                return tk
        return None

    def _luu(self):
        du_lieu = []
        for tk in self._ds:
            du_lieu.append(tk.to_dict())
        self._storage.ghi(du_lieu)            # có thể ném StorageError

    # ---------- trạng thái đăng nhập ----------
    @property
    def tai_khoan_hien_tai(self):
        """TaiKhoan đang đăng nhập, hoặc None nếu chưa đăng nhập."""
        return self._hien_tai

    def dang_ky(self, username, mat_khau, vai_tro=VAI_TRO_USER, ma_sv=None,
                nguoi_thuc_hien=None):
        """Tạo tài khoản mới (chưa tự đăng nhập).

        Tham số:
            nguoi_thuc_hien: TaiKhoan của người bấm nút; bắt buộc là admin khi
                tạo tài khoản admin. Người dùng tự đăng ký (vai trò user) thì để None.
        Trả về:
            TaiKhoan vừa tạo.
        Ném lỗi:
            InvalidDataError: username sai định dạng, mật khẩu ngắn, vai trò lạ, ma_sv sai.
            PermissionDeniedError: tạo admin mà nguoi_thuc_hien không phải admin.
            DuplicateIdError: username đã có (không phân biệt hoa thường).
            StorageError: không ghi được file (dữ liệu giữ nguyên như cũ).
        """
        tk = TaiKhoan.tao(username, mat_khau, vai_tro, ma_sv)    # kiểm tra định dạng

        if tk.la_admin():
            if not isinstance(nguoi_thuc_hien, TaiKhoan) or not nguoi_thuc_hien.la_admin():
                raise PermissionDeniedError(
                    "Chỉ quản trị viên mới được tạo tài khoản quản trị", None)

        if self._tim(tk.username) is not None:
            raise DuplicateIdError("Tên đăng nhập " + tk.username + " đã tồn tại", "username")

        self._ds.append(tk)
        try:
            self._luu()
        except StorageError:
            self._ds.remove(tk)               # hoàn tác trong bộ nhớ
            raise
        return tk

    def dang_nhap(self, username, mat_khau):
        """Đăng nhập; thành công thì ghi nhận vào tai_khoan_hien_tai.

        Trả về:
            TaiKhoan vừa đăng nhập.
        Ném lỗi:
            InvalidDataError: username hoặc mật khẩu rỗng / không phải chuỗi.
            AuthenticationError: sai username hoặc sai mật khẩu. Luôn cùng một
                thông báo để không lộ username nào tồn tại.
        """
        if not isinstance(username, str) or not isinstance(mat_khau, str):
            raise InvalidDataError("Tên đăng nhập và mật khẩu phải là chuỗi", None)
        if username.strip() == "" or mat_khau == "":
            raise InvalidDataError("Vui lòng nhập tên đăng nhập và mật khẩu", None)

        tk = self._tim(username)
        if tk is None or not tk.kiem_tra_mat_khau(mat_khau):
            raise AuthenticationError("Sai tên đăng nhập hoặc mật khẩu", None)
        self._hien_tai = tk
        return tk

    def dang_xuat(self):
        """Đăng xuất (không lỗi nếu chưa đăng nhập)."""
        self._hien_tai = None

    def doi_mat_khau(self, mat_khau_cu, mat_khau_moi):
        """Đổi mật khẩu của tài khoản đang đăng nhập.

        Ném lỗi:
            PermissionDeniedError: chưa đăng nhập.
            InvalidDataError: tham số không phải chuỗi; mật khẩu mới quá ngắn
                hoặc trùng mật khẩu cũ.
            AuthenticationError: mật khẩu cũ sai.
            StorageError: không ghi được file (mật khẩu cũ vẫn dùng được).
        """
        cu = self._hien_tai
        if cu is None:
            raise PermissionDeniedError("Vui lòng đăng nhập để đổi mật khẩu", None)
        if not isinstance(mat_khau_cu, str) or not isinstance(mat_khau_moi, str):
            raise InvalidDataError("Mật khẩu phải là chuỗi", None)
        if not cu.kiem_tra_mat_khau(mat_khau_cu):
            raise AuthenticationError("Mật khẩu cũ không đúng", None)

        moi = TaiKhoan.tao(cu.username, mat_khau_moi, cu.vai_tro, cu.ma_sv)   # kiểm tra độ dài
        if cu.kiem_tra_mat_khau(mat_khau_moi):
            raise InvalidDataError("Mật khẩu mới phải khác mật khẩu cũ", "mat_khau_moi")

        vi_tri = self._ds.index(cu)
        self._ds[vi_tri] = moi
        try:
            self._luu()
        except StorageError:
            self._ds[vi_tri] = cu             # hoàn tác
            raise
        self._hien_tai = moi

    # ---------- phân quyền ----------
    def co_quyen(self, hanh_dong):
        """Người đang đăng nhập có được thực hiện hành động này không?

        Dùng để ẩn/vô hiệu hóa nút. Không bao giờ ném lỗi.

        Trả về:
            True nếu được phép; False nếu chưa đăng nhập, không đủ quyền
            hoặc hành động không có trong ma trận quyền.
        """
        if self._hien_tai is None or not isinstance(hanh_dong, str):
            return False
        if hanh_dong in HANH_DONG_CHUNG:
            return True
        if hanh_dong in HANH_DONG_RIENG_ADMIN:
            return self._hien_tai.la_admin()
        return False

    def yeu_cau_quyen(self, hanh_dong):
        """Chặn thật: gọi trong hàm xử lý nút, trước khi gọi lớp quản lý.

        Ném lỗi:
            PermissionDeniedError: chưa đăng nhập hoặc không đủ quyền.
        """
        if self._hien_tai is None:
            raise PermissionDeniedError("Vui lòng đăng nhập để thực hiện thao tác này", None)
        if not self.co_quyen(hanh_dong):
            raise PermissionDeniedError("Bạn không có quyền thực hiện thao tác này", None)