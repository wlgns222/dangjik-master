import csv
from .data_structures import *
from .date import *


# 근무 키 설정
dish_key = "식기"
sb_guard_key = "위병부조장"
cctv_keys = tuple(f"CCTV{i}" for i in range(1, 7))
night_watch_keys = tuple(f"불침번{i}" for i in range(1, 6))
sentinel_keys = ("선임초병1", "후임초병1", "선임초병2", "후임초병2")

# 해시테이블의 수월한 접근을 위한 키 모음. 
all_duty_keys: tuple = (dish_key, sb_guard_key) + (cctv_keys + night_watch_keys + sentinel_keys) 
all_exp_keys: tuple = None

# 주요 자료구조 모음
date_list: list = None
exp_list: list = None 
worker_list: Circular_List = Circular_List()

worker_info_map = ChainingHashTable(150)
date_event_hash = ChainingHashTable(40)

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
    global worker_list, worker_info_map
    worker_data.sort(key=lambda x: x['전입일'])
    for w in worker_data: worker_list.append(w['군번'])

def load_worker_info_map(worker_data)->None:
    global worker_info_map
    for w in worker_data: worker_info_map.set(w['군번'], w)

def init_date_event_hash()->None:
    global date_event_hash, date_list, all_duty_keys, all_exp_keys
    for day in date_list:
        date_event_hash.set(day, ChainingHashTable(20))
        for h_key in (all_duty_keys + all_exp_keys):
            date_event_hash.get(day).set(h_key, [])

def load_all_data(date_range, worker_data, exp_data)->None:
    start_date, end_date = date_range
    load_all_exp_keys(exp_data)
    load_date_list(start_date, end_date)
    load_exp_list(exp_data)
    load_worker_list(worker_data)
    load_worker_info_map(worker_data)
    init_date_event_hash()
