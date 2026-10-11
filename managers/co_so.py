"""managers/co_so.py - Lớp nền QuanLyCoSo cho mọi lớp QuanLy* (HOPDONG_LOI mục 5.1).

Lớp con chỉ cần khai báo:
    class QuanLyPhong(QuanLyCoSo):
        LOP_DOI_TUONG = Phong
        TEN_DOI_TUONG = "phòng"
        TRUONG_MA = "ma_phong"

Nguyên tắc chung:
  * Dữ liệu giữ trong bộ nhớ (dict mã -> đối tượng), mỗi thay đổi ghi file ngay.
  * Ghi file lỗi (StorageError) thì HOÀN TÁC bộ nhớ rồi ném lại lỗi.
  * sua() làm trên BẢN SAO rồi mới thay: sai thì dữ liệu cũ nguyên vẹn.
  * Không print, không input.
"""
import copy
import logging

from exceptions import (InvalidDataError, DuplicateIdError, NotFoundError,
                        KtxError, StorageError)
from utils.validators import chuan_hoa_ma

log = logging.getLogger(__name__)


class QuanLyCoSo:
    LOP_DOI_TUONG = None      # lớp lưu trữ, phải có tu_dict(), to_dict(), .ma, cap_nhat()
    TEN_DOI_TUONG = "đối tượng"
    TRUONG_MA = "ma"          # tên trường mã, để chặn sua(..., ma_xxx=...)

    def __init__(self, storage):
        self._storage = storage
        self._ds = {}               # mã -> đối tượng (giữ thứ tự thêm)
        self.ban_ghi_loi = []       # các bản ghi bị bỏ qua khi nạp file
        self.tai()

    # ------------------------------------------------------------ hook cho lớp con
    def _truoc_khi_them(self, doi_tuong):
        """Ném lỗi để chặn việc thêm."""

    def _truoc_khi_xoa(self, doi_tuong):
        """Ném lỗi để chặn việc xóa."""

    # ------------------------------------------------------------ lưu / tải
    def tai(self):
        """Nạp file. Bản ghi hỏng hoặc trùng mã bị bỏ qua (ghi log, lưu vào ban_ghi_loi)."""
        self._ds = {}
        self.ban_ghi_loi = []
        for ban_ghi in self._storage.doc():
            try:
                doi_tuong = self.LOP_DOI_TUONG.tu_dict(ban_ghi)
                if doi_tuong.ma in self._ds:
                    raise DuplicateIdError(f"Trùng mã {doi_tuong.ma}", self.TRUONG_MA)
            except (KtxError, TypeError, ValueError, KeyError, AttributeError) as e:
                log.warning("Bỏ qua bản ghi %s hỏng: %s", self.TEN_DOI_TUONG, e)
                self.ban_ghi_loi.append({"ban_ghi": ban_ghi, "ly_do": str(e)})
                continue
            self._ds[doi_tuong.ma] = doi_tuong

    def luu(self):
        self._storage.ghi([o.to_dict() for o in self._ds.values()])

    def _luu_hoac_hoan_tac(self, ds_truoc):
        """Ghi file; lỗi thì trả bộ nhớ về ds_truoc rồi ném lại."""
        try:
            self.luu()
        except StorageError:
            self._ds = ds_truoc
            raise

    # ------------------------------------------------------------ tra cứu
    def _chuan_hoa(self, ma):
        return chuan_hoa_ma(ma, self.TRUONG_MA)     # rỗng / sai kiểu -> InvalidDataError

    def tim_theo_ma(self, ma):
        ma = self._chuan_hoa(ma)
        if ma not in self._ds:
            raise NotFoundError(f"Không tìm thấy {self.TEN_DOI_TUONG} {ma}", self.TRUONG_MA)
        return self._ds[ma]

    def co(self, ma):
        try:
            return self._chuan_hoa(ma) in self._ds
        except InvalidDataError:
            return False

    def _kiem_tra_thuoc_tinh(self, ten):
        if (not isinstance(ten, str) or ten.startswith("_")
                or not hasattr(self.LOP_DOI_TUONG, ten)):
            raise InvalidDataError(
                f"{self.TEN_DOI_TUONG.capitalize()} không có thuộc tính {ten!r}", str(ten))

    def tim_theo_tieu_chi(self, **tc):
        """Chuỗi: chứa chuỗi con, không phân biệt hoa thường. Kiểu khác: bằng. Nhiều tiêu chí = AND."""
        for ten in tc:
            self._kiem_tra_thuoc_tinh(ten)
        ket_qua = []
        for o in self._ds.values():
            if all(self._khop(getattr(o, ten), gia_tri) for ten, gia_tri in tc.items()):
                ket_qua.append(o)
        return ket_qua

    @staticmethod
    def _khop(gia_tri_that, gia_tri_can):
        if isinstance(gia_tri_that, str) and isinstance(gia_tri_can, str):
            return gia_tri_can.strip().lower() in gia_tri_that.lower()
        return gia_tri_that == gia_tri_can

    def lay_tat_ca(self, sap_xep_theo=None, dao_nguoc=False):
        ds = list(self._ds.values())
        if sap_xep_theo is not None:
            self._kiem_tra_thuoc_tinh(sap_xep_theo)
            try:
                ds.sort(key=lambda o: getattr(o, sap_xep_theo), reverse=bool(dao_nguoc))
            except TypeError as e:
                raise InvalidDataError(
                    f"Không sắp xếp được theo {sap_xep_theo!r}: {e}", sap_xep_theo) from e
        elif dao_nguoc:
            ds.reverse()
        return ds

    def __len__(self):
        return len(self._ds)

    # ------------------------------------------------------------ thêm / xóa / sửa
    def them(self, doi_tuong):
        if not isinstance(doi_tuong, self.LOP_DOI_TUONG):
            raise InvalidDataError(
                f"Chỉ thêm được đối tượng kiểu {self.LOP_DOI_TUONG.__name__}")
        self._truoc_khi_them(doi_tuong)
        if doi_tuong.ma in self._ds:
            raise DuplicateIdError(
                f"{self.TEN_DOI_TUONG.capitalize()} {doi_tuong.ma} đã tồn tại", self.TRUONG_MA)
        truoc = dict(self._ds)
        self._ds[doi_tuong.ma] = doi_tuong
        self._luu_hoac_hoan_tac(truoc)
        return doi_tuong

    def xoa(self, ma):
        doi_tuong = self.tim_theo_ma(ma)            # mã rỗng -> Invalid, không có -> NotFound
        self._truoc_khi_xoa(doi_tuong)
        truoc = dict(self._ds)
        del self._ds[doi_tuong.ma]
        self._luu_hoac_hoan_tac(truoc)
        return doi_tuong

    def sua(self, ma, /, **thong_tin_moi):
        """ma là tham số chỉ-vị-trí để sua("A1", ma="B2") bị bắt đúng thay vì lỗi cú pháp."""
        if not thong_tin_moi:
            raise InvalidDataError("Không có thông tin nào để sửa")
        for ten in thong_tin_moi:
            if ten == self.TRUONG_MA or ten == "ma":
                raise InvalidDataError("Không được đổi mã", ten)
        goc = self.tim_theo_ma(ma)
        ban_sao = copy.deepcopy(goc)
        try:
            ban_sao.cap_nhat(**thong_tin_moi)       # sai thì ném, bản gốc không bị đụng
        except TypeError as e:                      # tên trường lạ với cap_nhat có tham số cố định
            raise InvalidDataError(f"Trường không hợp lệ: {e}") from e
        truoc = dict(self._ds)
        self._ds[goc.ma] = ban_sao
        self._luu_hoac_hoan_tac(truoc)
        return ban_sao

    def _thay_the(self, ban_moi):
        """Thay đối tượng cùng mã bằng bản mới (dùng cho thao tác nghiệp vụ trên bản sao)."""
        truoc = dict(self._ds)
        self._ds[ban_moi.ma] = ban_moi
        self._luu_hoac_hoan_tac(truoc)
        return ban_moi