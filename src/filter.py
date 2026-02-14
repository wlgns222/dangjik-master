"""
[인계사항]
역할: 근무 배정 시 인원을 제외하는 로직 관리

1. Global Filter : 전역 또는 휴가 등의 사유로 제외되는 인원
2. Task Filter : 특정 근무를 수행할 수 없는 인원
3. Date Filter : 특정 근무가 없는 날

+ 추후 '1호차 운전병' 'PX병'등 특수하게 근무 들어가는 보직 처리
"""
from .data_structures import ChainingHashTable
from .date import is_date_in_range

def global_filter(date_hash, date_list, exceptions):
    #1. 전역자 필터링: 
    #2. 열외 명단(exception_list) 필터링:
    exception_list = []
    for e in exceptions:
        exp_info = (e['군번'], e['시작일'], e['종료일'], e['사유'])
        exception_list.append(exp_info)

    for day in date_list:
        today_duty = date_hash.get(day)
        for exp_worker in exception_list:
            id_tag, from_date, to_date, exp_type = exp_worker
            if is_date_in_range(day, from_date, to_date):
                today_duty.get(exp_type).append(id_tag)


def task_filter(sn, duty_type, worker_info_map):
    #가능근무 데이터(예: '11101') 기반 필터링:
    #순서는 위병부조장,식기,불침번,초병,CCTV로 고정
    #호출함수: get_next_available()
    work_bit = worker_info_map.get(sn)['가능근무']
    return work_bit[duty_type] == '0'

# ---------------------------------------------------------
# CASE 3. 날짜별 보직 활성화 체크
# 목적: 특정 근무가 없는 날 (식기 없는 날, 훈련) 근무 제외
# ---------------------------------------------------------

def date_duty_filter(day, duty_type):
    """
    - 근무 공정표 보니 1월에 2회 식기 없는 날 존재
    - 단체로 훈련 나가는 날 특정 근무 없음 
    """
    pass
