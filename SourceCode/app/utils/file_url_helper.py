import urllib.parse
from pathlib import Path
import requests
from markitdown import MarkItDown
import os
import re

def check_file(file_path):
    """
    Kiểm tra xem file có tồn tại không

    Args:
        file_path (str): Đường dẫn đến file

    Returns:
        bool: True nếu file tồn tại, False nếu không
    """
    try:
        path = Path(file_path)
        return path.exists() and path.is_file()
    except Exception:
        return False

def check_url(url):
    """
    Kiểm tra xem URL có accessible không

    Args:
        url (str): URL cần kiểm tra

    Returns:
        bool: True nếu URL accessible, False nếu không
    """
    try:
        # Kiểm tra format URL
        parsed = urllib.parse.urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return False

        # Kiểm tra accessibility
        response = requests.head(url, timeout=10, allow_redirects=True)
        return response.status_code == 200

    except Exception:
        return False


def get_file_path(folder_path, file_name):
    """
    Tạo đường dẫn đầy đủ đến file trong thư mục

    Args:
        folder_path (str): Đường dẫn đến thư mục
        file_name (str): Tên file

    Returns:
        str: Đường dẫn đầy đủ đến file
    """
    return os.path.join(folder_path, file_name)

def get_filename_advanced(file_path, remove_special_chars=False):
    """
    Version nâng cao: Lấy tên file và có thể loại bỏ ký tự đặc biệt

    Args:
        file_path (str): Đường dẫn hoặc tên file đầy đủ
        remove_special_chars (bool): Có loại bỏ ký tự đặc biệt không

    Returns:
        str: Tên file đã được xử lý
    """

    # Lấy tên file từ đường dẫn
    filename = os.path.basename(file_path)

    # Bỏ extension
    name_without_extension = os.path.splitext(filename)[0]

    if remove_special_chars:
        # Loại bỏ ký tự đặc biệt, chỉ giữ chữ cái, số và khoảng trắng
        name_without_extension = re.sub(r'[^\w\s]', '', name_without_extension)
        # Loại bỏ khoảng trắng thừa
        name_without_extension = re.sub(r'\s+', ' ', name_without_extension).strip()

    return name_without_extension