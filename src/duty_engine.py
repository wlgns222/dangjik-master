from datetime import datetime, timedelta
from .constants import WORKER_KEYS, DATE_FORMAT
from .date import is_date_in_range
import src.data_store as ds

# ==========================================
# 1. 열외 필터링
# ==========================================
def global_filter():
    """
    달력을 순회하며 휴가, 전역, 전대기 인원을 해시테이블에 미리 기록합니다.
    """
    worker_list = ds.worker_list
    worker_info_map = ds.worker_info_map

    for day in ds.date_list:
        today_duty = ds.date_event_hash.get(day)
        current_day_dt = datetime.strptime(day, DATE_FORMAT)

        # 1-1. 전역 및 전대기 판단 (인원 전체 순회)
        for i in range(worker_list.length()):
            sn = worker_list.get_at(i)
            worker = worker_info_map.get(sn)
            
            discharge_str = worker.get('전역일')
            if not discharge_str: continue
            
            discharge_dt = datetime.strptime(str(discharge_str).strip(), DATE_FORMAT)
            pre_discharge_dt = discharge_dt - timedelta(days=1)
            
            # 전역
            if current_day_dt >= discharge_dt:
                if today_duty.get("전역") is not None:
                    today_duty.get("전역").append(sn)
            # 전대기
            elif current_day_dt == pre_discharge_dt:
                if today_duty.get("전대기") is not None:
                    today_duty.get("전대기").append(sn)

        # 1-2. 일반 열외(휴가, 파견 등) 처리
        for e in ds.exp_list:
            if is_date_in_range(day, e['시작일'], e['종료일']):
                if today_duty.get(e['사유']) is not None:
                    today_duty.get(e['사유']).append(e['군번'])

# ==========================================
# 2. 개별 인원 자격 검증
# ==========================================
def task_filter(sn, duty_type):
    """특정 인원이 해당 근무 보직에 자격(Y)이 있는지 확인합니다."""
    worker = ds.worker_info_map.get(sn)
    if not worker: return False
    
    col_name = WORKER_KEYS.get(duty_type)
    return worker.get(col_name) == 'Y'

# ==========================================
# 3. 배정 알고리즘
# ==========================================
def get_start_index(c_list, last_sn):
    if not last_sn: return 0
    for i in range(c_list.length()):
        if c_list.get_at(i) == last_sn: return i + 1
    return 0

def get_next_available(ptr, assigned_set, duty_type):
    """
    오늘 근무가 가능하면서 자격이 있는 다음 인원을 반환합니다.
    (열외/전역자는 이미 assigned_set에 포함되어 필터링됩니다.)
    """
    max_search = ds.worker_list.length()
    count = 0
    
    while count < max_search:
        sn = ptr.get_val()
        count += 1
        
        # 1. 이미 오늘 배정됨(근무/열외/전역)  2. 자격이 없음(N)
        if sn in assigned_set or not task_filter(sn, duty_type):
            continue
            
        assigned_set.add(sn)
        return sn
        
    return "가용인원없음"