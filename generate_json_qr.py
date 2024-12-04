import qrcode
import json
import csv

# emp_id.csvファイルを開く
with open('emp_id.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        emp_id = row['emp_id']  # 各行のemp_idを取得
        name = row['name']  # 各行のnameを取得

        # QRコードに含めるデータ
        data = {
            "emp_id": emp_id,
            "name": name
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
        img.save(f"{emp_id}_qr.png")
        print(f"QRコードを生成しました: {emp_id}_qr.png")