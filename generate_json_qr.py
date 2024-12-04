import qrcode
import json

# QRコードに含めるデータ（例: 社員番号）
data = {
    "emp_id": "001"  # emp_idを含むJSON形式
}

# JSON形式にエンコード
data_json = json.dumps(data)

# QRコード生成
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)
qr.add_data(data_json)  # JSONデータをQRコードに追加
qr.make(fit=True)

# 画像ファイルとして保存
img = qr.make_image(fill_color="black", back_color="white")
img.save("001_qr.png")
print("QRコードを生成しました。")
