#test
import json
import requests
import os

def lambda_handler(event, context):
    emp_id = event.get('emp_id')
    if not emp_id:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "emp_id is required"})
        }

    # 環境変数からkintoneの設定を取得
    subdomain = os.getenv('KINTONE_SUBDOMAIN')  # kintone のサブドメイン
    api_key = os.getenv('KINTONE_API_KEY')  # API キー
    app_id = os.getenv('KINTONE_APP_ID')  # kintone アプリの ID

    if not subdomain or not api_key or not app_id:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": "Kintone environment variables are not set properly"})
        }

    headers = {
        "X-Cybozu-API-Token": api_key,
    }

    # クエリを指定
    params = {
        "app": app_id,
        "query": f'emp_id = "{emp_id}"',
        "fields": ["attendance", "cost", "name"]
    }

    try:
        # APIにGETリクエストを送信
        api_url = f"https://{subdomain}.cybozu.com/k/v1/records.json"
        response = requests.get(api_url, headers=headers, params=params)

        if response.status_code != 200:
            return {
                "statusCode": response.status_code,
                "body": json.dumps({
                    "message": "Error fetching data from kintone",
                    "details": response.text
                }, ensure_ascii=False)
            }

        # レスポンスの処理
        response_data = response.json()
        records = response_data.get("records", [])
        if not records:
            return {
                "statusCode": 404,
                "body": json.dumps({"message": f"参加者一覧に存在しません。 社員番号: {emp_id}"}, ensure_ascii=False)
            }

        # レコード情報の取得
        record = records[0]
        attendance = record.get("attendance", {}).get("value", "未設定")
        cost = record.get("cost", {}).get("value", "未設定")
        name = record.get("name", {}).get("value", "未設定")

        # message変数の初期化
        message_attendance = ""
        message_cost = ""

        # attendanceが未出席の場合、出席済みに変更
        if attendance == "未出席":
            # Kintoneのレコードを更新 (PUTメソッド)
            update_data = {
                "app": app_id,
                "updateKey": {
                    "field": "emp_id",  # emp_idを更新キーとして使用
                    "value": emp_id
                },
                "record": {
                    "attendance": {
                        "value": "出席済み"
                    }
                }
            }

            update_url = f"https://{subdomain}.cybozu.com/k/v1/record.json"
            update_response = requests.put(update_url, headers=headers, json=update_data)
            if update_response.status_code != 200:
                return {
                    "statusCode": update_response.status_code,
                    "body": json.dumps({
                        "message": "Error updating attendance",
                        "details": update_response.text
                    }, ensure_ascii=False)
                }
            message_attendance = "出席済みに変更しました"
        elif attendance == "出席済み":
            message_attendance = "すでに出席済みの社員です"

        # costが集金済みの場合、その旨を通知
        if cost == "集金済み":
            message_cost = "参加費を集金済みです"
        elif cost == "未集金":
            message_cost = "参加費が支払われていません"
        elif cost == "集金不要":
            message_cost = "集金不要な社員です"

        return f"名前: {name}\n社員番号: {emp_id}\n出席状況: {message_attendance}\n集金状況: {message_cost}"

    except Exception as e:
        print("Error occurred:", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"message": "An error occurred", "error": str(e)}, ensure_ascii=False)
        }
