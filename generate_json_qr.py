import qrcode

# 埋め込むuser_id
user_id = "satou minori"

# QRコードの作成
qr = qrcode.QRCode(version=1, box_size=10, border=5)
qr.add_data(user_id)
qr.make(fit=True)

# 画像の作成
img = qr.make_image(fill='black', back_color='white')

# QRコードを保存
img.save(f"{user_id}_qr_code.png")