import csv
import calendar
from datetime import datetime
from data_structures import ChainingHashTable, Circular_List, List_Pointer

# --- [전역 매핑 변수] ---
worker_info_map = ChainingHashTable(100)

# --- [로직 보조 함수] ---
def is_date_in_range(target_date, start_date, end_date):
    return start_date <= target_date <= end_date

def get_start_index(c_list, last_sn):
    if not last_sn: return 0
    for i in range(c_list.length()):
        if c_list.get_at(i) == last_sn: return i + 1
    return 0

def get_next_available(ptr, assigned_set, duty_type=None):
    while True:
        sn = ptr.get_val()
        info = worker_info_map.get(sn)
        
        if sn in assigned_set:
            continue
                
        assigned_set.add(sn)
        return sn

def get_names(sn_input):
    if not sn_input: return ""
    sns = sn_input if isinstance(sn_input, list) else [sn_input]
    names = []
    for sn in sns:
        if sn == "72사단": names.append(sn)
        else:
            info = worker_info_map.get(sn)
            names.append(info['이름'] if info else sn)
    return ", ".join(names)

# --- [데이터 로드 함수] ---
def load_all_data(worker_file, exception_file):
    worker_data = []
    
    # 1. 인명부 로드
    with open(worker_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            worker_data.append(row)
            worker_info_map.set(row['군번'], row)
            
    # 2. 열외 명단 로드 (데이터 로직 내에서 활용하기 위해 리스트화)
    exceptions = []
    with open(exception_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            exceptions.append(row)
            
    return worker_data, exceptions

# --- [출력 관련 함수] ---

def export_results(date_list, date_hash, worker_data, duty_types):
    # 1. 날짜별 현황
    with open("result_by_date.csv", 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(["날짜"] + duty_types)
        for day in date_list:
            res = date_hash.get(day)
            row = [day] + [get_names(res.get(h)) for h in duty_types]
            writer.writerow(row)
    # 2. 인원별 스케줄 (행보관님 스타일)
    with open("result_by_person.csv", 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(["이름"] + date_list)
        for worker in worker_data:
            sn = worker['군번']
            row = [worker['이름']]
            for day in date_list:
                today_res = date_hash.get(day)
                my_duty = ""
                for k in duty_types:
                    if sn in today_res.get(k):
                        my_duty = k
                        break
                row.append(my_duty)
            writer.writerow(row)
