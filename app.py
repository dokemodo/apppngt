from flask import Flask, request
from tra_cuu import tra_cuu

app = Flask(__name__)

@app.route('/')
def check_phat():
    bien_so = request.args.get('bienso')
    if not bien_so:
        return "Vui lòng truy cập với định dạng: /?bienso=30A12345", 400

    try:
        results = tra_cuu(bien_so)
        if not results:
            return f"{bien_so}: Không có vi phạm nào được ghi nhận."

        output = f"{bien_so}: Có {len(results)} lỗi vi phạm như sau:\n"
        for idx, r in enumerate(results, 1):
            output += f"{idx}. Thời gian: {r['thoi_gian']}\n   Lỗi: {r['loi_vi_pham']}\n   Địa điểm: {r['dia_diem']}\n"
        return output

    except Exception:
        return "Có lỗi trong quá trình tra cứu, vui lòng thử lại sau.", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)