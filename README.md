# Raspberry Pi 4 Fault Injection (Marvin-style)

## 문제 해결: Bit-flip 효과 강화

**이전 문제**: Bit-flip이 프로그램 초기(0-5K instructions)에만 발생 → 영향 거의 없음

**해결책**: 
- Instruction skip 범위: 10K~60K instructions로 확대
- 랜덤 레지스터 선택: x0~x7 중 랜덤 (이전: x1 고정)
- 프로그램 실행 중간에 bit-flip 발생 → 더 큰 영향

## Quick Start

```bash
# 1. 파일 업로드
scp -P 8000 simple_injector.c simple_runner.c Makefile collect_ptrace_normal.py collect_native_fault.py pi@182.228.51.23:~/i3months/playground/

# 2. SSH 접속
ssh pi@182.228.51.23 -p 8000

# 3. 컴파일
cd ~/i3months/playground
make all

# 4. 데이터 수집 (병렬)
nohup python3 collect_ptrace_normal.py basicmath > ptrace_normal.log 2>&1 &
nohup python3 collect_native_fault.py basicmath > ptrace_fault.log 2>&1 &

# 5. 모니터링
tail -f ptrace_normal.log
wc -l data/*.csv

# 6. 다운로드 (로컬)
scp -P 8000 'pi@182.228.51.23:~/i3months/playground/data/ptrace_normal_basicmath.csv' ./data/
scp -P 8000 'pi@182.228.51.23:~/i3months/playground/data/faulty_basicmath_native.csv' ./data/

# 7. 시각화 (로컬)
data/venv/bin/python visualize/visualize_comparison.py

# 8. ML 학습 (로컬)
data/venv/bin/python train_ml_model.py
```

## 변경 사항

### simple_injector.c
- Instruction skip: `rand() % 5000` → `10000 + (rand() % 50000)`
- Target register: `1` (고정) → `rand() % 8` (랜덤)

### simple_runner.c
- Instruction skip: `rand() % 5000` → `10000 + (rand() % 50000)`

## 예상 결과

이제 Normal vs Fault 데이터가 명확히 구분될 것입니다:
- Crash 증가 (프로그램 중간에 bit-flip)
- HPC 변화 증가 (실행 경로 변경)
- ML 모델 정확도 향상

## Files

- `simple_injector.c`: Ptrace fault injector (개선됨)
- `simple_runner.c`: Ptrace runner (개선됨)
- `collect_ptrace_normal.py`: Normal 데이터 수집
- `collect_native_fault.py`: Fault 데이터 수집
- `visualize/visualize_comparison.py`: 시각화
- `train_ml_model.py`: ML 모델 학습
