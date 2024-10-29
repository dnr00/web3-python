import csv
import json

def csv_to_json(csv_file_path, json_file_path):
    # 결과를 저장할 리스트
    data = []

    # CSV 파일 읽기
    with open(csv_file_path, mode='r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        
        # 각 행을 딕셔너리로 변환하여 리스트에 추가
        for row in csv_reader:
            data.append(row)

    # JSON 파일로 저장
    with open(json_file_path, mode='w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=4)

    print(f"CSV 파일이 성공적으로 JSON 파일로 변환되었습니다: {json_file_path}")

# 함수 사용
csv_to_json('beta3_interaction.csv', 'accounts.json')