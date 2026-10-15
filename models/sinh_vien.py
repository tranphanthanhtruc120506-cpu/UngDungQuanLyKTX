from exceptions import InvalidDataError
from datetime import datetime, date

class SinhVien:
    def __init__(self, ma_sv, ho_ten, ngay_sinh, so_dien_thoai, lop):
        self.__ma_sv = ma_sv          
        self.__ho_ten = ho_ten
        self.ngay_sinh = ngay_sinh        # Gọi qua setter để kiểm tra
        self.so_dien_thoai = so_dien_thoai # Gọi qua setter để kiểm tra
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

    @ngay_sinh.setter
    def ngay_sinh(self, value):
        value = value.strip()
        try:
            # Chuyển chuỗi thành đối tượng date
            d = datetime.strptime(value, "%d/%m/%Y").date()
            # Kiểm tra không được lớn hơn ngày hiện tại
            if d > date.today():
                raise InvalidDataError("Ngày sinh không được lớn hơn ngày hiện tại!")
            # Kiểm tra tuổi tối thiểu (ví dụ phải từ 18 tuổi trở lên)
            tuoi = date.today().year - d.year
            if tuoi < 18:
                raise InvalidDataError("Sinh viên phải từ 18 tuổi trở lên!")
        except ValueError:
            raise InvalidDataError("Định dạng ngày sinh không hợp lệ (DD/MM/YYYY)!")
        self.__ngay_sinh = value
        
    @property
    def so_dien_thoai(self):
        return self.__so_dien_thoai

    @so_dien_thoai.setter
    def so_dien_thoai(self, value):
        value = str(value).strip()
        # Kiểm tra: phải đủ 10 số, toàn là chữ số và bắt đầu bằng số 0
        if not (value.isdigit() and len(value) == 10 and value.startswith('0')):
            raise InvalidDataError("Số điện thoại phải có đúng 10 chữ số và bắt đầu bằng số 0!")
        self.__so_dien_thoai = value
        
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