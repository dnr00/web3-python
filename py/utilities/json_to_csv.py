import csv
import json

# JSON 데이터 파일을 읽어들입니다.
input_filename = 'accounts.json'  # 입력 파일명 (JSON 형식)
output_filename = 'private_keys.csv'  # 출력 파일명 (CSV 형식)

# JSON 파일에서 데이터 로드
with open(input_filename, 'r') as infile:
    data = json.load(infile)

# private_key만 추출
private_keys = [entry["private_key"] for entry in data]

# CSV 파일로 저장
with open(output_filename, mode='w', newline='') as outfile:
    writer = csv.writer(outfile)
    writer.writerow(["private_key"])  # CSV 헤더
    for key in private_keys:
        writer.writerow([key])

print(f"CSV file saved as {output_filename}")
