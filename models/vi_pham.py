"""B2 - Lớp ViPham (models/vi_pham.py).

HỢP ĐỒNG (mục 4.6):
    ViPham(ma_vp, ma_sv, noi_dung, ngay, muc_phat=0)
    .ma / .ma_vp           mã đã chuẩn hóa, CHỈ ĐỌC
    .ma_sv                 mã sinh viên bị ghi nhận, CHỈ ĐỌC
    .to_dict() / ViPham.from_dict(d) / .cap_nhat(**kw)
Việc "ma_sv có tồn tại không" do QuanLyViPham (B3) kiểm tra, không phải lớp này.
"""
from datetime import date

from exceptions import InvalidDataError
from utils import validators as v

NOI_DUNG_TOI_DA = 300


def _kiem_tra_ma_vp(gia_tri):
    if not v.hop_le_ma_vp(gia_tri):
        raise InvalidDataError("Mã vi phạm phải dạng VP + ít nhất 4 chữ số (ví dụ VP0001)", "ma_vp")
    return v.chuan_hoa_ma(gia_tri, "ma_vp")


def _kiem_tra_ma_sv(gia_tri):
    if not v.hop_le_ma_sv(gia_tri):
        raise InvalidDataError("Mã sinh viên phải gồm đúng 10 chữ số", "ma_sv")
    return v.chuan_hoa_ma(gia_tri, "ma_sv")


def _kiem_tra_noi_dung(gia_tri):
    return v.yeu_cau_chuoi(gia_tri, "noi_dung", NOI_DUNG_TOI_DA)


def _kiem_tra_ngay(gia_tri):
    ngay = v.doc_ngay(gia_tri, "ngay")
    if ngay > date.today():
        raise InvalidDataError("Ngày vi phạm không được ở tương lai", "ngay")
    return ngay


def _kiem_tra_muc_phat(gia_tri):
    """Số nguyên >= 0 (đồng). 0 nghĩa là chỉ nhắc nhở."""
    return v.doc_so_nguyen(gia_tri, "muc_phat", toi_thieu=0)


class ViPham:
    TRUONG_SUA_DUOC = ("noi_dung", "ngay", "muc_phat")

    def __init__(self, ma_vp, ma_sv, noi_dung, ngay, muc_phat=0):
        self.__ma_vp = _kiem_tra_ma_vp(ma_vp)
        self.__ma_sv = _kiem_tra_ma_sv(ma_sv)
        self.__noi_dung = _kiem_tra_noi_dung(noi_dung)
        self.__ngay = _kiem_tra_ngay(ngay)
        self.__muc_phat = _kiem_tra_muc_phat(muc_phat)

    @property
    def ma_vp(self):
        return self.__ma_vp

    @property
    def ma(self):
        return self.__ma_vp

    @property
    def ma_sv(self):
        return self.__ma_sv

    @property
    def noi_dung(self):
        return self.__noi_dung

    @noi_dung.setter
    def noi_dung(self, value):
        self.__noi_dung = _kiem_tra_noi_dung(value)

    @property
    def ngay(self):
        return self.__ngay

    @ngay.setter
    def ngay(self, value):
        self.__ngay = _kiem_tra_ngay(value)

    @property
    def muc_phat(self):
        return self.__muc_phat

    @muc_phat.setter
    def muc_phat(self, value):
        self.__muc_phat = _kiem_tra_muc_phat(value)

    def cap_nhat(self, **thong_tin_moi):
        """Sửa nhiều trường. Một trường sai => không trường nào bị đổi."""
        for khoa in thong_tin_moi:
            if khoa not in self.TRUONG_SUA_DUOC:
                if khoa in ("ma", "ma_vp", "ma_sv"):
                    raise InvalidDataError("Không được đổi mã vi phạm hoặc mã sinh viên", khoa)
                raise InvalidDataError(f"Không có trường '{khoa}' để sửa", khoa)
        moi = {}
        if "noi_dung" in thong_tin_moi:
            moi["noi_dung"] = _kiem_tra_noi_dung(thong_tin_moi["noi_dung"])
        if "ngay" in thong_tin_moi:
            moi["ngay"] = _kiem_tra_ngay(thong_tin_moi["ngay"])
        if "muc_phat" in thong_tin_moi:
            moi["muc_phat"] = _kiem_tra_muc_phat(thong_tin_moi["muc_phat"])
        if "noi_dung" in moi:
            self.__noi_dung = moi["noi_dung"]
        if "ngay" in moi:
            self.__ngay = moi["ngay"]
        if "muc_phat" in moi:
            self.__muc_phat = moi["muc_phat"]

    def to_dict(self):
        return {
            "ma_vp": self.__ma_vp,
            "ma_sv": self.__ma_sv,
            "noi_dung": self.__noi_dung,
            "ngay": v.dinh_dang_ngay(self.__ngay),
            "muc_phat": self.__muc_phat,
        }

    @classmethod
    def from_dict(cls, d):
        if not isinstance(d, dict):
            raise InvalidDataError("Bản ghi vi phạm phải là một đối tượng JSON")
        for truong in ("ma_vp", "ma_sv", "noi_dung", "ngay"):
            if truong not in d:
                raise InvalidDataError(f"Thiếu trường '{truong}'", truong)
        return cls(d["ma_vp"], d["ma_sv"], d["noi_dung"], d["ngay"], d.get("muc_phat", 0))

    tu_dict = from_dict

    def __str__(self):
        return f"{self.ma_vp} - SV {self.ma_sv} - {self.noi_dung} - phạt {self.muc_phat:,} đ"

    def __repr__(self):
        return f"ViPham({self.ma_vp!r}, {self.ma_sv!r})"