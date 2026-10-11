"""managers/quan_ly_phong.py - QuanLyPhong (việc A7).

Kế thừa QuanLyCoSo (thêm, xóa, sửa, tìm, lấy tất cả, __len__, lưu file...) và bổ sung:
tìm theo trạng thái, xếp / trả chỗ trong phòng (kiểm tra chỗ), đổi loại phòng, thống kê.

Lưu ý phân tầng (HOPDONG_LOI mục 6): them_sv_vao_phong chỉ kiểm tra CHỖ.
Việc "SV có tồn tại không, có hợp đồng không" thuộc DichVuKtx.xep_phong.
"""
import copy

from exceptions import InvalidDataError
from managers.co_so import QuanLyCoSo
from models.phong import Phong, tao_phong

TRANG_THAI_PHONG = ("trong", "con_cho", "day")


class QuanLyPhong(QuanLyCoSo):
    LOP_DOI_TUONG = Phong
    TEN_DOI_TUONG = "phòng"
    TRUONG_MA = "ma_phong"

    def _truoc_khi_xoa(self, phong):
        if len(phong) > 0:
            raise InvalidDataError(
                f"Phòng {phong.ma_phong} còn {len(phong)} người, không thể xóa", "ma_phong")

    # ---------- tìm ----------
    def tim_theo_trang_thai(self, trang_thai):
        """'trong' (0 người) | 'con_cho' (có người, còn chỗ) | 'day'."""
        if trang_thai not in TRANG_THAI_PHONG:
            raise InvalidDataError(
                f"Trạng thái phòng chỉ có thể là: {', '.join(TRANG_THAI_PHONG)}", "trang_thai")
        if trang_thai == "trong":
            return [p for p in self._ds.values() if len(p) == 0]
        if trang_thai == "day":
            return [p for p in self._ds.values() if p.da_day()]
        return [p for p in self._ds.values() if len(p) > 0 and not p.da_day()]

    def phong_con_cho(self):
        """Trống + còn chỗ, sắp theo mã."""
        return sorted((p for p in self._ds.values() if not p.da_day()),
                      key=lambda p: p.ma_phong)

    def tim_phong_cua_sv(self, ma_sv):
        """Ngoại lệ có chủ đích: trả None nếu SV chưa ở phòng nào (không ném NotFoundError)."""
        for p in self._ds.values():
            if p.co_sv(ma_sv):
                return p
        return None

    # ---------- xếp / trả chỗ (làm trên bản sao, ghi lỗi thì hoàn tác) ----------
    def them_sv_vao_phong(self, ma_phong, ma_sv):
        """NotFound(phòng) · InvalidData(mã SV) · Duplicate · RoomFull · Storage."""
        goc = self.tim_theo_ma(ma_phong)
        ban_sao = copy.deepcopy(goc)
        ban_sao.them_sv(ma_sv)
        return self._thay_the(ban_sao)

    def bo_sv_khoi_phong(self, ma_phong, ma_sv):
        """NotFound (phòng, hoặc SV không ở phòng đó) · Storage."""
        goc = self.tim_theo_ma(ma_phong)
        ban_sao = copy.deepcopy(goc)
        ban_sao.bo_sv(ma_sv)
        return self._thay_the(ban_sao)

    # ---------- đổi loại / thống kê ----------
    def doi_loai(self, ma_phong, loai_moi):
        """Dựng lớp con mới (thuong <-> maylanh), giữ nguyên mã, số chỗ, giá và danh sách SV."""
        goc = self.tim_theo_ma(ma_phong)
        du_lieu = goc.to_dict()
        du_lieu["loai"] = loai_moi
        return self._thay_the(tao_phong(du_lieu))   # loại lạ -> InvalidDataError

    def thong_ke_phong(self):
        ds = list(self._ds.values())
        tong_cho = sum(p.so_cho for p in ds)
        dang_o = sum(len(p) for p in ds)
        return {
            "tong_phong": len(ds),
            "tong_cho": tong_cho,
            "dang_o": dang_o,
            "cho_trong": tong_cho - dang_o,
            "so_phong_trong": sum(1 for p in ds if len(p) == 0),
            "so_phong_day": sum(1 for p in ds if p.da_day()),
        }