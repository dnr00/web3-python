import csv
from eth_account import Account

# 입력 CSV 파일 (각 줄에 private key가 있음)
input_file = "private_keys.csv"
# 결과를 저장할 출력 CSV 파일 (public address만 저장)
output_file = "public_addresses.csv"

# CSV 파일에서 private key 목록 읽기
with open(input_file, 'r') as f:
    private_keys = [line.strip() for line in f if line.strip()]

# 각 private key에 대해 public address 추출
public_addresses = []
for pk in private_keys:
    try:
        account = Account.from_key(pk)
        public_addresses.append(account.address)
    except Exception as e:
        print(f"Error processing key {pk}: {e}")

# 추출된 public address를 CSV 파일에 저장 (한 줄에 하나씩)
with open(output_file, 'w', newline='') as f:
    writer = csv.writer(f)
    for address in public_addresses:
        writer.writerow([address])

print(f"Public address 추출이 완료되었습니다. 결과는 '{output_file}' 파일을 확인하세요.")
