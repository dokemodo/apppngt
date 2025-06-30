import requests
from bs4 import BeautifulSoup
from PIL import Image
import pytesseract
import io
import base64
import re

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux; rv:109.0) Gecko/20100101 Firefox/114.0"
}

def get_captcha(session):
    url = "https://www.csgt.vn/tra-cuu-phuong-tien-vi-pham.html"
    try:
        r = session.get(url, headers=headers, timeout=10)
        r.raise_for_status()
    except requests.exceptions.RequestException:
        raise Exception("Không thể truy cập trang CSGT.")

    soup = BeautifulSoup(r.text, "html.parser")
    captcha_img = soup.find("img", {"id": "captcha-img"})
    if not captcha_img or "src" not in captcha_img.attrs:
        raise Exception("Không tìm thấy ảnh captcha.")

    base64_img = captcha_img["src"].split(",")[1]
    img_bytes = base64.b64decode(base64_img)
    image = Image.open(io.BytesIO(img_bytes))

    captcha_text = pytesseract.image_to_string(image, config='--psm 7').strip()
    captcha_text = re.sub(r'\W+', '', captcha_text)
    return captcha_text, r.text

def tra_cuu(bien_so, loai_xe="Ô tô", max_retry=3):
    session = requests.Session()

    for attempt in range(1, max_retry + 1):
        try:
            captcha_text, page_html = get_captcha(session)

            soup = BeautifulSoup(page_html, "html.parser")
            token = soup.find("input", {"name": "__RequestVerificationToken"})
            if not token:
                raise Exception("Không lấy được CSRF token.")
            csrf_token = token["value"]

            payload = {
                "__RequestVerificationToken": csrf_token,
                "plateNumber": bien_so,
                "vehicleType": loai_xe,
                "captcha": captcha_text
            }

            post_url = "https://www.csgt.vn/tra-cuu-phuong-tien-vi-pham.html"
            r = session.post(post_url, data=payload, headers=headers, timeout=10)
            r.raise_for_status()

            soup = BeautifulSoup(r.text, "html.parser")
            error_div = soup.find("div", class_="xe_texterror")
            if error_div and "mã xác nhận sai" in error_div.text.lower():
                print(f"[Lần {attempt}] Captcha sai. Thử lại...")
                continue

            rows = soup.select("#resultTable tbody tr")
            results = []
            for row in rows:
                cols = row.find_all("td")
                if len(cols) >= 4:
                    results.append({
                        "thoi_gian": cols[1].text.strip(),
                        "dia_diem": cols[2].text.strip(),
                        "loi_vi_pham": cols[3].text.strip(),
                    })

            return results

        except Exception:
            print(f"[Lần {attempt}] Lỗi, thử lại...")

    raise Exception("Có lỗi trong quá trình tra cứu, vui lòng thử lại sau.")