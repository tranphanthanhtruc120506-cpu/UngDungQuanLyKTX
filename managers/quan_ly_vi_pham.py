"""Quản lý vi phạm của sinh viên (phần B3, mục 5.6 của Hợp đồng hàm và lỗi).

Các QuanLy* không import lẫn nhau, vì vậy QuanLyViPham nhận đối tượng
QuanLySinhVien qua tham số của constructor để kiểm tra sinh viên có tồn tại.
"""
from managers.co_so import QuanLyCoSo
from models.vi_pham import ViPham


class QuanLyViPham(QuanLyCoSo):
    """Quản lý các đối tượng ViPham, khóa chính là ma_vp."""

    LOP_DOI_TUONG = ViPham
    TEN_DOI_TUONG = "vi phạm"
    TRUONG_MA = "ma_vp"

    def __init__(self, storage, ql_sinh_vien):
        """Tham số:
            storage: JsonStorage trỏ tới vipham.json.
            ql_sinh_vien: QuanLySinhVien dùng để kiểm tra mã sinh viên.
        """
        # Gán trước khi gọi super() vì lớp nền nạp file ngay trong __init__
        self._ql_sinh_vien = ql_sinh_vien
        super().__init__(storage)

    def _truoc_khi_them(self, obj):
        """Hook của lớp nền: chặn thêm vi phạm của sinh viên không tồn tại.

        Ném lỗi:
            NotFoundError: ma_sv của vi phạm không có trong danh sách sinh viên.
        """
        self._ql_sinh_vien.tim_theo_ma(obj.ma_sv)

    def sinh_ma(self):
        """Sinh mã vi phạm kế tiếp: "VP0001", "VP0002", ...

        Lấy số lớn nhất đang có cộng 1 (không dùng số lượng, vì xóa bớt
        bản ghi giữa chừng sẽ làm mã bị trùng).

        Trả về:
            str mã mới, chưa tồn tại trong danh sách.
        """
        so_lon_nhat = 0
        for vp in self.lay_tat_ca():
            phan_so = vp.ma[2:]              # bỏ tiền tố "VP"
            try:
                so = int(phan_so)
            except ValueError:               # mã lạ, bỏ qua
                continue
            if so > so_lon_nhat:
                so_lon_nhat = so

        so_moi = str(so_lon_nhat + 1)
        while len(so_moi) < 4:               # thêm số 0 phía trước cho đủ 4 chữ số
            so_moi = "0" + so_moi
        return "VP" + so_moi

    def _sap_giam_dan_theo_ngay(self, ds):
        """Sắp xếp nổi bọt tại chỗ: ngày mới nhất lên đầu, cùng ngày thì mã lớn hơn lên trước."""
        n = len(ds)
        for i in range(n):
            for j in range(n - 1 - i):
                a = ds[j]
                b = ds[j + 1]
                if a.ngay < b.ngay or (a.ngay == b.ngay and a.ma < b.ma):
                    ds[j], ds[j + 1] = b, a  # hoán đổi hai phần tử

    def lich_su_cua_sv(self, ma_sv):
        """Lịch sử vi phạm của một sinh viên, mới nhất đứng trước.

        Trả về:
            list các ViPham sắp theo ngày giảm dần;
            list rỗng nếu sinh viên chưa vi phạm lần nào.
        Ném lỗi:
            InvalidDataError: ma_sv rỗng hoặc không phải chuỗi.
            NotFoundError: không có sinh viên mang mã này.
        """
        sv = self._ql_sinh_vien.tim_theo_ma(ma_sv)   # đã chuẩn hóa mã và kiểm tra tồn tại
        ds = []
        for vp in self.lay_tat_ca():
            if vp.ma_sv == sv.ma:
                ds.append(vp)
        self._sap_giam_dan_theo_ngay(ds)
        return ds

    def tong_phat_cua_sv(self, ma_sv):
        """Tổng tiền phạt (đồng) của một sinh viên.

        Trả về:
            int tổng muc_phat; 0 nếu chưa vi phạm hoặc chỉ bị nhắc nhở (mức 0).
        Ném lỗi:
            InvalidDataError, NotFoundError: giống lich_su_cua_sv().
        """
        tong = 0
        for vp in self.lich_su_cua_sv(ma_sv):
            tong += vp.muc_phat
        return tong