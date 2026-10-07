"""

Hai nhóm hàm với hai quy ước khác nhau:

1. hop_le_*  : nhận MỌI kiểu dữ liệu, trả về bool, KHÔNG BAO GIỜ ném lỗi.
               Dùng để kiểm tra nhanh (ví dụ tô đỏ ô nhập).
2. Còn lại   : chuan_hoa_ma, chuan_hoa_sdt, doc_ngay, dinh_dang_ngay,
               doc_so_nguyen, yeu_cau_chuoi. Dữ liệu sai -> ném
               InvalidDataError(thong_bao, truong); đúng -> trả giá trị
               đã chuẩn hóa.

Lưu ý Regex: dùng fullmatch (khớp trọn chuỗi) và [0-9] thay cho ^...$ và \\d.
  - '$' chấp nhận một ký tự xuống dòng ở cuối chuỗi.
  - '\\d' chấp nhận cả chữ số Unicode như '１' (full-width).
"""

import re
import unicodedata
from datetime import date, datetime

from exceptions import InvalidDataError

# ---------------------------------------------------------------- Regex
# SĐT: 10 số bắt đầu bằng 0, hoặc +84 rồi 9 số (nhập +84 thì lưu thành 0...)
MAU_SDT = re.compile(r"(?:0|\+84)[0-9]{9}")
# Email: phần trước @ gồm chữ, số, . _ % + -; tên miền có ít nhất một dấu chấm
MAU_EMAIL = re.compile(
    r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}"
)
MAU_MA_SV = re.compile(r"[0-9]{10}")        
MAU_MA_PHONG = re.compile(r"[A-D][0-9]{3}")  # ví dụ A101 (dãy A-D)
MAU_MA_HD = re.compile(r"HD[0-9]{4,}")       # ví dụ HD0001
MAU_MA_VP = re.compile(r"VP[0-9]{4,}")       # ví dụ VP0001
MAU_USERNAME = re.compile(r"[a-z0-9_]{3,20}")
MAU_NGAY = re.compile(r"[0-9]{2}/[0-9]{2}/[0-9]{4}")   # dd/mm/yyyy
MAU_THANG = re.compile(r"(?:0[1-9]|1[0-2])/[0-9]{4}")  # mm/yyyy

EMAIL_TOI_DA = 254
HO_TEN_TOI_THIEU = 2
HO_TEN_TOI_DA = 100


# ------------------------------------------------------- hàm dùng nội bộ
def _la_chuoi(x):
    return isinstance(x, str)


def _khop(mau, x, in_hoa=False):
    """True nếu x là chuỗi và (sau strip) khớp trọn mẫu. Không ném lỗi."""
    if not _la_chuoi(x):
        return False
    s = x.strip()
    if in_hoa:
        s = s.upper()
    return mau.fullmatch(s) is not None


def _chuan_hoa_ten(x):
    """Gộp khoảng trắng thừa, đưa về dạng NFC (chữ có dấu viết liền)."""
    return " ".join(unicodedata.normalize("NFC", x).split())


# ===================================================== NHÓM 1: hop_le_*
def hop_le_sdt(s):
    """SĐT 10 số bắt đầu bằng 0, hoặc dạng +84 + 9 số."""
    return _khop(MAU_SDT, s)


def hop_le_email(s):
    """Email đúng định dạng, tối đa 254 ký tự."""
    return _la_chuoi(s) and len(s.strip()) <= EMAIL_TOI_DA and _khop(MAU_EMAIL, s)


def hop_le_ma_sv(s):
    """Mã sinh viên: đúng 10 chữ số."""
    return _khop(MAU_MA_SV, s)


def hop_le_ma_phong(s):
    """Mã phòng: một chữ A-D và 3 chữ số (không phân biệt hoa thường)."""
    return _khop(MAU_MA_PHONG, s, in_hoa=True)


def hop_le_ma_hd(s):
    """Mã hợp đồng: HD + ít nhất 4 chữ số."""
    return _khop(MAU_MA_HD, s, in_hoa=True)


def hop_le_ma_vp(s):
    """Mã vi phạm: VP + ít nhất 4 chữ số."""
    return _khop(MAU_MA_VP, s, in_hoa=True)


def hop_le_ho_ten(s):
    """Họ tên 2-100 ký tự, chỉ gồm chữ cái (có dấu) và khoảng trắng."""
    if not _la_chuoi(s):
        return False
    ten = _chuan_hoa_ten(s)
    if not HO_TEN_TOI_THIEU <= len(ten) <= HO_TEN_TOI_DA:
        return False
    return all(c.isalpha() or c == " " for c in ten)


def hop_le_username(s):
    """Username 3-20 ký tự gồm a-z, 0-9, gạch dưới (không phân biệt hoa thường)."""
    return _khop(MAU_USERNAME, s.lower() if _la_chuoi(s) else s)


def hop_le_ngay(s):
    """Định dạng dd/mm/yyyy và là ngày có thật (30/02/2026 là sai)."""
    if not _khop(MAU_NGAY, s):
        return False
    try:
        datetime.strptime(s.strip(), "%d/%m/%Y")
        return True
    except ValueError:
        return False


def hop_le_thang(s):
    """Tháng dạng mm/yyyy, mm từ 01 đến 12."""
    return _khop(MAU_THANG, s)


# ============================================ NHÓM 2: chuẩn hóa / đọc
def yeu_cau_chuoi(gia_tri, truong="", toi_da=None):
    """Bắt buộc là chuỗi không rỗng (sau strip), không dài quá toi_da.

    Trả về: chuỗi đã strip.
    Ném lỗi: InvalidDataError nếu không phải chuỗi, rỗng, hoặc quá dài.
    """
    if not _la_chuoi(gia_tri):
        raise InvalidDataError("Giá trị phải là chuỗi ký tự", truong or None)
    s = gia_tri.strip()
    if not s:
        raise InvalidDataError("Không được để trống", truong or None)
    if toi_da is not None and len(s) > toi_da:
        raise InvalidDataError(f"Không được dài quá {toi_da} ký tự", truong or None)
    return s


def chuan_hoa_ma(ma, truong="ma"):
    """Chuẩn hóa mã: strip + IN HOA. Rỗng hoặc không phải chuỗi -> InvalidDataError."""
    if not _la_chuoi(ma) or not ma.strip():
        raise InvalidDataError("Mã không được để trống", truong)
    return ma.strip().upper()


def chuan_hoa_sdt(s, truong="so_dien_thoai"):
    """Kiểm tra SĐT và đưa về dạng 0xxxxxxxxx (+84912345678 -> 0912345678)."""
    if not hop_le_sdt(s):
        raise InvalidDataError(
            "Số điện thoại phải gồm 10 số bắt đầu bằng 0 (hoặc +84)", truong
        )
    s = s.strip()
    return "0" + s[3:] if s.startswith("+84") else s


def chuan_hoa_ho_ten(s, truong="ho_ten"):
    """Kiểm tra họ tên, trả về chuỗi đã gộp khoảng trắng thừa (giữ hoa/thường)."""
    if not hop_le_ho_ten(s):
        raise InvalidDataError(
            f"Họ tên gồm {HO_TEN_TOI_THIEU}-{HO_TEN_TOI_DA} ký tự, "
            "chỉ chứa chữ cái và khoảng trắng",
            truong,
        )
    return _chuan_hoa_ten(s)


def doc_ngay(gia_tri, truong="ngay"):
    """Nhận 'dd/mm/yyyy' hoặc date/datetime, trả về datetime.date.

    Ném lỗi: InvalidDataError nếu sai kiểu, sai định dạng, hoặc ngày không có thật.
    """
    if isinstance(gia_tri, datetime):
        return gia_tri.date()
    if isinstance(gia_tri, date):
        return gia_tri
    if not hop_le_ngay(gia_tri):
        raise InvalidDataError("Ngày phải đúng dạng dd/mm/yyyy và có thật", truong)
    return datetime.strptime(gia_tri.strip(), "%d/%m/%Y").date()


def dinh_dang_ngay(d):
    """datetime.date -> 'dd/mm/yyyy'. Sai kiểu -> InvalidDataError."""
    if not isinstance(d, date):
        raise InvalidDataError("Cần một giá trị ngày", "ngay")
    return f"{d.day:02d}/{d.month:02d}/{d.year:04d}"


def doc_so_nguyen(gia_tri, truong="", toi_thieu=None, toi_da=None):
    """Đọc số nguyên từ ô nhập (chuỗi thô) hoặc int. 'abc' -> InvalidDataError.

    Không nhận bool, float, hay chuỗi như '12.5'. Có thể giới hạn khoảng
    [toi_thieu, toi_da]. Giao diện đưa chuỗi thô vào đây, không tự gọi int().
    """
    ten = truong or None
    if isinstance(gia_tri, bool):
        raise InvalidDataError("Giá trị phải là số nguyên", ten)
    if isinstance(gia_tri, int):
        so = gia_tri
    elif _la_chuoi(gia_tri) and re.fullmatch(r"[+-]?[0-9]+", gia_tri.strip()):
        so = int(gia_tri.strip())
    else:
        raise InvalidDataError("Giá trị phải là số nguyên", ten)
    if toi_thieu is not None and so < toi_thieu:
        raise InvalidDataError(f"Giá trị phải từ {toi_thieu} trở lên", ten)
    if toi_da is not None and so > toi_da:
        raise InvalidDataError(f"Giá trị không được vượt quá {toi_da}", ten)
    return so