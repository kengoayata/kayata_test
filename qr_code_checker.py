import json
import boto3
import csv
import io

s3 = boto3.client('s3')

def check_payment_and_mark_attendance(user_id, bucket_name, key):
    csv_obj = s3.get_object(Bucket=bucket_name, Key=key)
    csv_content = csv_obj['Body'].read().decode('utf-8').splitlines()
    csv_reader = list(csv.reader(csv_content))
    header = csv_reader[0]

    # "出席済み" カラムがなければ追加
    #if '出席済み' not in header:
    #    header.append('出席済み')
    
    updated_csv = [header]
    payment_status = False
    already_marked = False
    user_found = False  # Track if the user is found

    for row in csv_reader[1:]:
        if row[0] == user_id:
            user_found = True  # User is found
            if row[1] == '済み':
                payment_status = True
                # 出席済みマークが既にあるか確認
                if row[header.index('出席済み')] == '〇':
                    already_marked = True
                else:
                    # 出席済みマークがない場合に追加
                    while len(row) < len(header):
                        row.append('')
                    row[header.index('出席済み')] = '〇'
        updated_csv.append(row)

    output = io.StringIO()
    csv_writer = csv.writer(output)
    csv_writer.writerows(updated_csv)
    s3.put_object(Bucket=bucket_name, Key=key, Body=output.getvalue().encode('utf-8'))
    
    return payment_status, already_marked, user_found  # Return user_found

def lambda_handler(event, context):
    try:
        # event['body'] が存在し、空でないことを確認
        if 'body' not in event or not event['body']:
            return {
                'statusCode': 400,
                'body': json.dumps({"error": "リクエストボディが空です。"}, ensure_ascii=False)
            }

        # JSONパースの試行
        body = json.loads(event['body'])
        user_id = body.get('user_id')
        print(body)

        if not user_id:
            return {
                'statusCode': 400,
                'body': json.dumps({"error": "user_id が指定されていません。"}, ensure_ascii=False)
            }

        bucket_name = 'kayata-qr'
        key = 'attendance_list.csv'

        # 支払い状況と出席済みかどうかを確認
        payment_status, already_marked, user_found = check_payment_and_mark_attendance(user_id, bucket_name, key)

        if not user_found:  # Check if user is not found
            return {
                'statusCode': 404,
                'body': json.dumps({"error": "ユーザーが見つかりません。"}, ensure_ascii=False)
            }
        elif already_marked:
            return {
                'statusCode': 200,
                'body': json.dumps({"status": "ALREADY_MARKED", "message": "既に出席済みです。"}, ensure_ascii=False)
            }
        elif payment_status:
            return {
                'statusCode': 200,
                'body': json.dumps({"status": "OK", "message": "支払い済みで出席マークを追加しました。"}, ensure_ascii=False)
            }
        else:
            return {
                'statusCode': 200,
                'body': json.dumps({"status": "STOP", "message": "支払いが完了していません。"}, ensure_ascii=False)
            }

    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'body': json.dumps({"error": "無効なJSON形式です。"}, ensure_ascii=False)
        }
