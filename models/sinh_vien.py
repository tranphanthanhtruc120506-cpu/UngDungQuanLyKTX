from exceptions import InvalidDataError

class SinhVien:
    def __init__(self, ma_sv, ho_ten, ngay_sinh, so_dien_thoai, lop):
        # Tính đóng gói: Các thuộc tính được ẩn đi bằng hai dấu gạch dưới (private)
        self.__ma_sv = ma_sv          
        self.__ho_ten = ho_ten
        self.__ngay_sinh = ngay_sinh
        self.__so_dien_thoai = so_dien_thoai
        self.__lop = lop

    # Sử dụng @property để lấy dữ liệu (Getter)
    @property
    def ma_sv(self):
        return self.__ma_sv
    
    @property
    def ho_ten(self):
        return self.__ho_ten
        
    # Sử dụng .setter để kiểm tra dữ liệu trước khi cập nhật (Setter)
    @ho_ten.setter
    def ho_ten(self, value):
        if not value.strip():
            raise InvalidDataError("Họ tên không được để trống!")
        self.__ho_ten = value

    @property
    def ngay_sinh(self):
        return self.__ngay_sinh
        
    @property
    def so_dien_thoai(self):
        return self.__so_dien_thoai
        
    @property
    def lop(self):
        return self.__lop

    # Hàm chuyển đối tượng thành Dictionary để thư viện json có thể ghi ra file
    def to_dict(self):
        return {
            "ma_sv": self.__ma_sv,
            "ho_ten": self.__ho_ten,
            "ngay_sinh": self.__ngay_sinh,
            "so_dien_thoai": self.__so_dien_thoai,
            "lop": self.__lop
        }