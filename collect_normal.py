import subprocess
import csv
import time

# 수집 횟수
TOTAL_RUNS = 1000
# 파일명
output_file = "normal_hpc_data.csv"

# HPC 지표 설정
events = "cycles,instructions,cache-misses,branch-misses"

print(f"정상 데이터 수집 시작... {TOTAL_RUNS}회 실행 예정...")

with open(output_file, mode='w', newline='') as f:
    writer = csv.writer(f)
    # 헤더는 [지표 이름 + 라벨] 으로 구성됨.
    writer.writerow(["cycles", "instructions", "cache_misses", "branch_misses", "label"])

    for i in range(1, TOTAL_RUNS + 1):
        # perf stat 실행 csv 형태로 출력
        cmd = f"perf stat -e {events} -x, sleep 0.1 2>&1"
        result = subprocess.check_output(cmd, shell=True).decode('utf-8')

        # 파싱
        rows = result.strip().split('\n')
        data = []
        for row in rows:
            parts = row.split(',')
            if len(parts) > 0 and parts[0].isdigit():
                data.append(parts[0])

        # 지표가 모두 수집되었는지 확인 후 저장 (Label 0: Normal)
        if len(data) == 4:
            writer.writerow(data + ["0"])
            
        if i % 100 == 0:
            print(f"{i}/{TOTAL_RUNS} 완료...")

print(f"수집끝 '{output_file}' 파일 생성")