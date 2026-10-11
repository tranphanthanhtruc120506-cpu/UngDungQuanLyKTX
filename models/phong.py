import config
from exceptions import InvalidDataError

# ==========================================
# LỚP CHA: Tính kế thừa
# ==========================================
class Phong:
    def __init__(self, ma_phong, so_cho, gia_co_ban):
        self.__ma_phong = ma_phong      
        self.__so_cho = so_cho
        self.__gia_co_ban = gia_co_ban
        self.__danh_sach_sv = []        # Lưu mã các sinh viên đang ở trong phòng

    @property
    def ma_phong(self): return self.__ma_phong

    @property
    def so_cho(self): return self.__so_cho

    @property
    def gia_co_ban(self): return self.__gia_co_ban

    @property
    def danh_sach_sv(self): return self.__danh_sach_sv

    def them_sv(self, ma_sv):
        # Kiểm tra logic nghiệp vụ trước khi thêm
        if len(self.__danh_sach_sv) >= self.__so_cho:
            raise InvalidDataError("Phòng đã hết chỗ!")
        if ma_sv in self.__danh_sach_sv:
            raise InvalidDataError("Sinh viên đã ở trong phòng!")
        self.__danh_sach_sv.append(ma_sv)

    def bo_sv(self, ma_sv):
        if ma_sv in self.__danh_sach_sv:
            self.__danh_sach_sv.remove(ma_sv)
        else:
            raise InvalidDataError("Không tìm thấy sinh viên trong phòng!")

    # TÍNH ĐA HÌNH: Hàm này sẽ được ghi đè ở lớp con
    def tinh_phi_o(self):
        return self.__gia_co_ban

    def to_dict(self):
        return {
            "ma_phong": self.__ma_phong,
            "loai": config.LOAI_THUONG,
            "so_cho": self.__so_cho,
            "gia_co_ban": self.__gia_co_ban,
            "danh_sach_sv": self.__danh_sach_sv
        }

# ==========================================
# LỚP CON: Phòng Máy Lạnh kế thừa từ lớp Phong
# ==========================================
class PhongMayLanh(Phong):
    def __init__(self, ma_phong, so_cho, gia_co_ban):
        # Gọi lại hàm khởi tạo của lớp cha
        super().__init__(ma_phong, so_cho, gia_co_ban)

    # TÍNH ĐA HÌNH: Ghi đè (Override) hàm tính phí ở để cộng thêm phụ thu
    def tinh_phi_o(self):
        return self.gia_co_ban + config.PHU_THU_MAY_LANH

    def to_dict(self):
        # Tái sử dụng code của lớp cha và sửa lại trường "loai"
        data = super().to_dict()
        data["loai"] = config.LOAI_MAY_LANH
        return data