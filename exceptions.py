class InvalidDataError(Exception):
    """Lỗi khi dữ liệu nhập vào không hợp lệ (trống, sai định dạng...)"""
    pass

class DuplicateIdError(Exception):
    """Lỗi khi mã (Mã SV, Mã Phòng, Mã Hợp Đồng...) đã tồn tại trong danh sách"""
    pass

class NotFoundError(Exception):
    """Lỗi khi tìm kiếm nhưng không thấy đối tượng"""
    pass