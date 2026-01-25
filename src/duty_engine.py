import csv
import calendar
from enum import IntEnum
from datetime import datetime
from src.data_structures import ChainingHashTable, Circular_List, List_Pointer
from src.filter import task_filter
# --- [전역 매핑 변수] ---
worker_info_map = ChainingHashTable(100)

# --- [근무 인덱스 enum] --- 
class DUTY_ENUM(IntEnum):
    SUB_GUARD = 0
    DISH = 1
    NIGHT = 2
    SENTINEL = 3
    CCTV = 4

# --- [로직 보조 함수] ---

def get_start_index(c_list, last_sn):
    if not last_sn: return 0
    for i in range(c_list.length()):
        if c_list.get_at(i) == last_sn: return i + 1
    return 0

def get_next_available(ptr, assigned_set, duty_type):
    while True:
        sn = ptr.get_val()
        if sn in assigned_set or task_filter(sn, duty_type, worker_info_map):
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


def get_all_exp(exceptions):
    exp_set = set()
    for e in exceptions: exp_set.add(e['사유'])
    return list(exp_set)



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

# --- [출력 함수] ---

def export_results(date_list, date_hash, worker_data, duty_types):
    # 1. 날짜별
    with open("result_by_date.csv", 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(["날짜"] + duty_types)
        for day in date_list:
            res = date_hash.get(day)
            row = [day] + [get_names(res.get(h)) for h in duty_types]
            writer.writerow(row)
    # 2. 인원별
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
