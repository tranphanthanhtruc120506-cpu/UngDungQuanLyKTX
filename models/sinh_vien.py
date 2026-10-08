"""B2 - Lớp SinhVien (models/sinh_vien.py).

HỢP ĐỒNG (mục 4.1 và 4.3 của HOP_DONG_HAM_VA_LOI):
    SinhVien(ma_sv, ho_ten, ngay_sinh, so_dien_thoai, lop, email=None)
    .ma / .ma_sv           mã đã chuẩn hóa (IN HOA), CHỈ ĐỌC
    .to_dict()             dict thuần JSON, ngày dạng "dd/mm/yyyy"
    SinhVien.from_dict(d)  dựng lại từ dict (tu_dict là tên gọi khác của from_dict)
    .cap_nhat(**kw)        sửa thông tin, tất-cả-hoặc-không-gì
Mọi dữ liệu sai đều ném InvalidDataError(thong_bao, truong), không để
TypeError / ValueError / KeyError lọt ra ngoài.
"""
from datetime import date

from exceptions import InvalidDataError
from utils import validators as v

TUOI_TOI_THIEU = 16     # giả định của nhóm, ghi vào báo cáo
TUOI_TOI_DA = 60
LOP_TOI_DA = 20


# ---------------------------------------------------------------------
# Các hàm kiểm tra từng trường. Setter, __init__ và cap_nhat đều dùng chung
# => tạo mới và sửa luôn đi qua cùng một bộ luật.
# ---------------------------------------------------------------------
def _kiem_tra_ma_sv(gia_tri):
    if not v.hop_le_ma_sv(gia_tri):
        raise InvalidDataError("Mã sinh viên phải gồm đúng 10 chữ số", "ma_sv")
    return v.chuan_hoa_ma(gia_tri, "ma_sv")


def _tinh_tuoi(ngay_sinh, hom_nay):
    tuoi = hom_nay.year - ngay_sinh.year
    if (hom_nay.month, hom_nay.day) < (ngay_sinh.month, ngay_sinh.day):
        tuoi -= 1                                   # chưa tới sinh nhật năm nay
    return tuoi


def _kiem_tra_ngay_sinh(gia_tri, hom_nay=None):
    ngay = v.doc_ngay(gia_tri, "ngay_sinh")         # nhận "dd/mm/yyyy", date, datetime
    hom_nay = hom_nay or date.today()
    if ngay > hom_nay:
        raise InvalidDataError("Ngày sinh không được ở tương lai", "ngay_sinh")
    tuoi = _tinh_tuoi(ngay, hom_nay)
    if not TUOI_TOI_THIEU <= tuoi <= TUOI_TOI_DA:
        raise InvalidDataError(
            f"Tuổi phải từ {TUOI_TOI_THIEU} đến {TUOI_TOI_DA} (hiện là {tuoi})",
            "ngay_sinh",
        )
    return ngay


def _kiem_tra_email(gia_tri):
    """Email không bắt buộc: None hoặc chuỗi rỗng => None."""
    if gia_tri is None:
        return None
    if isinstance(gia_tri, str) and not gia_tri.strip():
        return None
    if not v.hop_le_email(gia_tri):
        raise InvalidDataError("Email không đúng định dạng", "email")
    return gia_tri.strip()


class SinhVien:
    # Các trường được phép sửa qua cap_nhat (không có ma_sv: mã không đổi)
    TRUONG_SUA_DUOC = ("ho_ten", "ngay_sinh", "so_dien_thoai", "lop", "email")

    def __init__(self, ma_sv, ho_ten, ngay_sinh, so_dien_thoai, lop, email=None):
        # Kiểm tra TẤT CẢ trước rồi mới gán: đối tượng không bao giờ ở trạng thái dở dang
        self.__ma_sv = _kiem_tra_ma_sv(ma_sv)
        self.__ho_ten = v.chuan_hoa_ho_ten(ho_ten, "ho_ten")
        self.__ngay_sinh = _kiem_tra_ngay_sinh(ngay_sinh)
        self.__so_dien_thoai = v.chuan_hoa_sdt(so_dien_thoai, "so_dien_thoai")
        self.__lop = v.yeu_cau_chuoi(lop, "lop", LOP_TOI_DA)
        self.__email = _kiem_tra_email(email)

    # ------------------------------------------------------------ property
    @property
    def ma_sv(self):
        return self.__ma_sv

    @property
    def ma(self):
        """Tên chung cho mọi lớp dữ liệu: lớp QuanLy dùng .ma để làm khóa."""
        return self.__ma_sv

    @property
    def ho_ten(self):
        return self.__ho_ten

    @ho_ten.setter
    def ho_ten(self, value):
        self.__ho_ten = v.chuan_hoa_ho_ten(value, "ho_ten")

    @property
    def ngay_sinh(self):
        return self.__ngay_sinh

    @ngay_sinh.setter
    def ngay_sinh(self, value):
        self.__ngay_sinh = _kiem_tra_ngay_sinh(value)

    @property
    def so_dien_thoai(self):
        return self.__so_dien_thoai

    @so_dien_thoai.setter
    def so_dien_thoai(self, value):
        self.__so_dien_thoai = v.chuan_hoa_sdt(value, "so_dien_thoai")

    @property
    def email(self):
        return self.__email

    @email.setter
    def email(self, value):
        self.__email = _kiem_tra_email(value)

    @property
    def lop(self):
        return self.__lop

    @lop.setter
    def lop(self, value):
        self.__lop = v.yeu_cau_chuoi(value, "lop", LOP_TOI_DA)

    # ------------------------------------------------------------ hành vi
    def cap_nhat(self, **thong_tin_moi):
        """Sửa nhiều trường cùng lúc. Một trường sai => không trường nào bị đổi."""
        for khoa in thong_tin_moi:
            if khoa not in self.TRUONG_SUA_DUOC:
                if khoa in ("ma", "ma_sv"):
                    raise InvalidDataError("Không được đổi mã sinh viên", khoa)
                raise InvalidDataError(f"Không có trường '{khoa}' để sửa", khoa)
        # Bước 1: kiểm tra hết, lưu kết quả đã chuẩn hóa vào dict tạm
        moi = {}
        if "ho_ten" in thong_tin_moi:
            moi["ho_ten"] = v.chuan_hoa_ho_ten(thong_tin_moi["ho_ten"], "ho_ten")
        if "ngay_sinh" in thong_tin_moi:
            moi["ngay_sinh"] = _kiem_tra_ngay_sinh(thong_tin_moi["ngay_sinh"])
        if "so_dien_thoai" in thong_tin_moi:
            moi["so_dien_thoai"] = v.chuan_hoa_sdt(thong_tin_moi["so_dien_thoai"], "so_dien_thoai")
        if "lop" in thong_tin_moi:
            moi["lop"] = v.yeu_cau_chuoi(thong_tin_moi["lop"], "lop", LOP_TOI_DA)
        if "email" in thong_tin_moi:
            moi["email"] = _kiem_tra_email(thong_tin_moi["email"])
        # Bước 2: không có lỗi nào => mới gán
        if "ho_ten" in moi:
            self.__ho_ten = moi["ho_ten"]
        if "ngay_sinh" in moi:
            self.__ngay_sinh = moi["ngay_sinh"]
        if "so_dien_thoai" in moi:
            self.__so_dien_thoai = moi["so_dien_thoai"]
        if "lop" in moi:
            self.__lop = moi["lop"]
        if "email" in moi:
            self.__email = moi["email"]

    # -------------------------------------------------------- JSON <-> đối tượng
    def to_dict(self):
        return {
            "ma_sv": self.__ma_sv,
            "ho_ten": self.__ho_ten,
            "ngay_sinh": v.dinh_dang_ngay(self.__ngay_sinh),
            "so_dien_thoai": self.__so_dien_thoai,
            "email": self.__email,
            "lop": self.__lop,
        }

    @classmethod
    def from_dict(cls, d):
        """Dựng lại từ dict đọc ở file JSON. Thiếu trường/sai kiểu => InvalidDataError."""
        if not isinstance(d, dict):
            raise InvalidDataError("Bản ghi sinh viên phải là một đối tượng JSON")
        for truong in ("ma_sv", "ho_ten", "ngay_sinh", "so_dien_thoai", "lop"):
            if truong not in d:
                raise InvalidDataError(f"Thiếu trường '{truong}'", truong)
        return cls(
            ma_sv=d["ma_sv"],
            ho_ten=d["ho_ten"],
            ngay_sinh=d["ngay_sinh"],
            so_dien_thoai=d["so_dien_thoai"],
            lop=d["lop"],
            email=d.get("email"),
        )

    tu_dict = from_dict      # tên theo bản hợp đồng; hai tên cùng một hàm

    def __str__(self):
        return f"{self.ma_sv} - {self.ho_ten} - {self.lop}"

    def __repr__(self):
        return f"SinhVien({self.ma_sv!r}, {self.ho_ten!r})"