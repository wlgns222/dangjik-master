# constants.py
from enum import IntEnum

# --- [근무 유형 인덱스] ---
class DUTY_ENUM(IntEnum):
    SUB_GUARD = 0     # 위병부조장
    DISH = 1          # 식기
    NIGHT = 2         # 불침번
    SENTINEL = 3      # 초병 (선임/후임)
    CCTV = 4          # CCTV

# --- [CSV 데이터 매핑 키] ---
WORKER_KEYS = {
    DUTY_ENUM.SUB_GUARD: "위병부조장",
    DUTY_ENUM.DISH: "식기",
    DUTY_ENUM.NIGHT: "불침번",
    DUTY_ENUM.SENTINEL: "초병",
    DUTY_ENUM.CCTV: "CCTV"
}

# --- [시스템 설정] ---
DATE_FORMAT = "%Y-%m-%d"
MAX_WORKER_COUNT = 150  # 해시테이블 초기 사이즈 등

# --- [근무 상세 키워드] ---
# 해시테이블 및 결과 파일 출력 시 사용되는 실제 근무 명칭
DISH_KEY = "식기"
SB_GUARD_KEY = "위병부조장"
CCTV_KEYS = tuple(f"CCTV{i}" for i in range(1, 7))
NIGHT_WATCH_KEYS = tuple(f"불침번{i}" for i in range(1, 6))
SENTINEL_KEYS = ("선임초병1", "후임초병1", "선임초병2", "후임초병2")

# 모든 근무 키 통합 (순회 및 초기화용)
ALL_DUTY_KEYS = (DISH_KEY, SB_GUARD_KEY) + CCTV_KEYS + NIGHT_WATCH_KEYS + SENTINEL_KEYS