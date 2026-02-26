import csv
from datetime import datetime, timedelta
from .data_structures import *
from .date import *
from .constants import DATE_FORMAT, MAX_WORKER_COUNT, WORKER_KEYS, ALL_DUTY_KEYS, EVENT_HASH_SIZE

date_list: list = None
exp_list: list = None 
worker_list: Circular_List = Circular_List()

holiday_set: set = set()

worker_info_map = ChainingHashTable(MAX_WORKER_COUNT)
date_event_hash = ChainingHashTable(EVENT_HASH_SIZE)

def validate_date(date_str, field_name, row_id):
    if not date_str or not str(date_str).strip():
        raise ValueError(f"[{row_id}] 인원의 '{field_name}' 칸이 비어있습니다.")
    try:
        return datetime.strptime(str(date_str).strip(), DATE_FORMAT)
    except ValueError:
        raise ValueError(f"[{row_id}] 인원의 '{field_name}' 데이터('{date_str}') 형식이 잘못되었습니다.")

def validate_yn(val, field_name, row_id):
    clean_val = str(val).strip().upper()
    if clean_val not in ['Y', 'N']:
        raise ValueError(f"[{row_id}] 인원의 '{field_name}' 자격이 잘못되었습니다. (Y/N 입력 필요)")
    return clean_val

# 프로그램 서비스 전 전역변수 초기화
def load_all_exp_keys(exp_data)->None:
    global all_exp_keys
    exp_set = set()
    for e in exp_data: 
        exp_set.add(e['사유'])
    
    # '전역', '전대기' 사유 추가
    exp_set.add("전역")
    exp_set.add("전대기")
    all_exp_keys = tuple(exp_set)

def load_date_list(start_date, end_date)->None:
    global date_list
    print(start_date, end_date)
    date_list = get_custom_date_list(start_date, end_date)

def load_exp_list(exp_data)->None:
    global exp_list
    exp_list = []
    for e in exp_data: 
        exp_list.append(e)

def load_worker_list(worker_data)->None:
    global worker_list
    worker_list.clear()
    
    for w in worker_data:
        sn = w.get('군번', '알수없음')
        name = w.get('이름', '알수없음')
        row_id = f"{sn} {name}"

        validate_date(w.get('전입일'), '전입일', row_id)
        validate_date(w.get('전역일'), '전역일', row_id)

        for enum_val, col_name in WORKER_KEYS.items():
            w[col_name] = validate_yn(w.get(col_name), col_name, row_id)
            
    worker_data.sort(key=lambda x: datetime.strptime(str(x['전입일']).strip(), DATE_FORMAT))
    for w in worker_data: 
        worker_list.append(w['군번'])

def load_holiday(holiday_data) -> None :
    global holiday_set
    holiday_set.clear()
    for h in holiday_data:
        holiday_set.add(h['날짜'].strip())

def load_worker_info_map(worker_data)->None:
    global worker_info_map
    worker_info_map.clear()
    for w in worker_data: worker_info_map.set(w['군번'], w)

def init_date_event_hash()->None:
    global date_event_hash, date_list, all_exp_keys
    date_event_hash.clear()
    for day in date_list:
        today_hash = ChainingHashTable(40)
        for k in (ALL_DUTY_KEYS + all_exp_keys): 
            today_hash.set(k, [])
        date_event_hash.set(day, today_hash)

def load_all_data(date_range, worker_data, exp_data)->None:
    start_date, end_date = date_range
    load_all_exp_keys(exp_data)
    load_date_list(start_date, end_date)
    load_exp_list(exp_data)
    load_worker_list(worker_data)
    load_worker_info_map(worker_data)
    init_date_event_hash()
