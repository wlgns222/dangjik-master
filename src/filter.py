from .data_structures import ChainingHashTable
from datetime import datetime, timedelta
from .date import *

def global_filter(date_hash, date_list, exceptions):

    exception_list = []
    for e in exceptions:
        exp_info = (e['군번'], e['시작일'], e['종료일'], e['사유'])
        exception_list.append(exp_info)

    for day in date_list:
        today_duty = date_hash.get(day)
        current_day_dt = datetime.strptime(day, FORM)

        # worker_info_map 에서 전역일 체크
        from .main_data_loaders import worker_info_map, worker_list
        
        for i in range(worker_list.length()):
            sn = worker_list.get_at(i)
            worker = worker_info_map.get(sn)
            
            # CSV의 '전역일' 컬럼 데이터 가져오기
            discharge_dt = datetime.strptime(worker['전역일'], FORM)
            pre_discharge_dt = discharge_dt - timedelta(days=1) # 전역 전날
            
            # 1. 전역일 당일 이후인 경우
            if current_day_dt >= discharge_dt:
                today_duty.get("전역").append(sn)
            
            # 2. 전역일 전날인 경우
            elif current_day_dt == pre_discharge_dt:
                today_duty.get("전대기").append(sn)

        # 기존 열외(휴가 등) 처리
        for exp_worker in exception_list:
            id_tag, from_date, to_date, exp_type = exp_worker
            if is_date_in_range(day, from_date, to_date):
                today_duty.get(exp_type).append(id_tag)

def task_filter(sn, duty_type, worker_info_map, day_str=None):
    """
    특정 인원이 해당 보직을 수행할 수 있는지 'Y/N' 데이터로 판별
    반환값: True (배정 불가 / 필터링됨), False (배정 가능)
    """
    worker = worker_info_map.get(sn)
    if not worker:
        return True # 정보가 없으면 안전을 위해 배정 제외

    # DUTY_ENUM 인덱스와 CSV 헤더 매핑
    duty_map = {
        0: "위병부조장",
        1: "식기",
        2: "불침번",
        3: "초병",
        4: "CCTV"
    }
    
    col_name = duty_map.get(duty_type)
    
    if worker.get(col_name) == 'N':
        return True
        
    return False

#세부 근무 필터
"""
def commander_driver_filter(worker, duty_type, day_str, current_key):
    note = worker.get('비고', '')
    if "1호차 운전병" not in note:
        return False

    day_of_week = get_day_of_week(day_str)

    # 금요일: 초병2(퇴근), 불침번 가능
    if day_of_week == 'FRI':
        if duty_type == DUTY_ENUM.NIGHT: return False
        if duty_type == DUTY_ENUM.SENTINEL and "2" in (current_key or ""):
            return False
        return True

    # 일요일: 초병1(출근)만 가능
    elif day_of_week == 'SUN':
        if duty_type == DUTY_ENUM.SENTINEL and "1" in (current_key or ""):
            return False
        return True

    # 토요일: 프리패스
    elif day_of_week == 'SAT':
        return False

    # 평일: 불가
    return True
    """