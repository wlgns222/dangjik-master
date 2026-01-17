import csv
import calendar
from datetime import date

# --- [자료구조 정의] ---
class Circular_List:
    def __init__(self):
        self.__c_list = []
    def append(self, x):
        self.__c_list.append(x)
    def get_at(self, idx):
        if len(self.__c_list) == 0: return None
        return self.__c_list[idx % len(self.__c_list)]
    def length(self):
        return len(self.__c_list)

class List_Pointer:
    def __init__(self, p_list, idx):
        self.__idx = idx
        self.__p_list = p_list
    def get_val(self):
        temp = self.__p_list.get_at(self.__idx)
        self.__idx += 1
        return temp

class ChainingHashTable:
    def __init__(self, size=10):
        self.size = size
        self.table = [[] for _ in range(self.size)]
    def _hash_function(self, key):
        return hash(key) % self.size
    def set(self, key, value):
        index = self._hash_function(key)
        for i, (k, v) in enumerate(self.table[index]):
            if k == key:
                self.table[index][i] = (key, value)
                return
        self.table[index].append((key, value))
    def get(self, key):
        index = self._hash_function(key)
        for k, v in self.table[index]:
            if k == key: return v
        return None

# --- [로직 보조 함수] ---
def get_start_index(c_list, last_sn):
    if not last_sn: return 0
    for i in range(c_list.length()):
        if c_list.get_at(i) == last_sn: return i + 1
    return 0

def get_next_available(ptr, assigned_set):
    while True:
        sn = ptr.get_val()
        if sn not in assigned_set:
            assigned_set.add(sn)
            return sn

def is_date_in_range(target, start, end):
    return (start <= target) and (target <= end)

def get_name(sn):
    if not sn: return ""
    if isinstance(sn, list):
        if not sn: return ""
        sn = sn[0]
    if sn == "72사단": return sn
    info = worker_info_map.get(sn)
    return info['이름'] if info else sn

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

# --- [메인 로직 실행] ---

# 1. 데이터 로드
worker_data = []
worker_info_map = ChainingHashTable(100)
with open('./database.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        worker_data.append(row)
        worker_info_map.set(row['군번'], row)

# 2. 인원 분류 및 원형 리스트 생성
worker_data.sort(key=lambda x: x['전입일'])
mid = len(worker_data) // 2
c_list_all = Circular_List()
for w in worker_data: c_list_all.append(w['군번'])
c_list_sr = Circular_List()
for w in worker_data[:mid]: c_list_sr.append(w['군번'])
c_list_jr = Circular_List()
for w in worker_data[mid:]: c_list_jr.append(w['군번'])

# 3. 마지막 근무자 입력 및 포인터 설정
print("--- 마지막 근무자 군번을 입력하세요 (없으면 엔터) ---")
last_sub = input("위병부조장 마지막 인원: ")
last_cctv = input("CCTV 마지막 인원: ")
last_night = input("불침번 마지막 인원: ")
last_sr = input("선임초병 마지막 인원: ")
last_jr = input("후임초병 마지막 인원: ")
last_dish = input("식기 마지막 인원 (3명 중 가장 마지막): ")

ptr_sub_guard = List_Pointer(c_list_all, get_start_index(c_list_all, last_sub))
ptr_cctv = List_Pointer(c_list_all, get_start_index(c_list_all, last_cctv))
ptr_night = List_Pointer(c_list_all, get_start_index(c_list_all, last_night))
ptr_sr_sentinel = List_Pointer(c_list_sr, get_start_index(c_list_sr, last_sr))
ptr_jr_sentinel = List_Pointer(c_list_jr, get_start_index(c_list_jr, last_jr))
ptr_dish = List_Pointer(c_list_all, get_start_index(c_list_all, last_dish))

# 4. 배정 시작
print("\n배정 년/월 입력 (예: 2026 1):")
year, month = map(int, input().split())
date_list = [day.strftime("%m-%d") for week in calendar.Calendar().monthdatescalendar(year, month) for day in week if day.month == month]

date_hash = ChainingHashTable(40)
duty_types = ["위병부조장"] + [f"CCTV{i}" for i in range(1,7)] + [f"불침번{i}" for i in range(1,6)] + ["초병_1조", "초병_2조", "식기"]

# 날짜별 초기화 및 열외자 등록
for day in date_list:
    today_duty = ChainingHashTable(20)
    today_duty.set("열외", [])
    for worker in worker_data:
        if worker['열외일정'] != 'None':
            start, end = worker['열외일정'].split('~')
            if is_date_in_range(day, start, end):
                today_duty.get("열외").append(worker['군번'])
    date_hash.set(day, today_duty)

dish_skip_count = 0
for day in date_list:
    today_duty = date_hash.get(day)
    assigned_today = set(today_duty.get('열외'))

    # 1. 위병부조장 (1명)
    today_duty.set("위병부조장", [get_next_available(ptr_sub_guard, assigned_today)])
    
    # 2. CCTV (1~6번초, 각 3명)
    for i in range(1, 7):
        today_duty.set(f"CCTV{i}", [get_next_available(ptr_cctv, assigned_today) for _ in range(3)])

    # 3. 불침번 (1~5번초, 각 1명)
    for i in range(1, 6):
        today_duty.set(f"불침번{i}", [get_next_available(ptr_night, assigned_today)])

    # 4. 초병 (1조, 2조)
    today_duty.set("초병_1조", [get_next_available(ptr_sr_sentinel, assigned_today), get_next_available(ptr_jr_sentinel, assigned_today)])
    today_duty.set("초병_2조", [get_next_available(ptr_sr_sentinel, assigned_today), get_next_available(ptr_jr_sentinel, assigned_today)])
    
    # 5. 식기 (5일 주기)
    dish_skip_count += 1
    if dish_skip_count % 5 == 0:
        today_duty.set("식기", ['72사단'])
    else:
        today_duty.set("식기", [get_next_available(ptr_dish, assigned_today) for _ in range(3)])

# 5. 출력 함수 정의
def export_by_date(date_list, date_hash, filename="result_by_date.csv"):
    headers = ["날짜"] + duty_types
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for day in date_list:
            res = date_hash.get(day)
            row = [day] + [get_names(res.get(h)) for h in duty_types]
            writer.writerow(row)

def export_by_person(date_list, date_hash, worker_data, filename="result_by_person.csv"):
    headers = ["이름"] + date_list
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for worker in worker_data:
            sn = worker['군번']
            row = [worker['이름']]
            for day in date_list:
                today_res = date_hash.get(day)
                my_duty = ""
                for k in duty_types:
                    val = today_res.get(k)
                    if val and sn in val:
                        my_duty = k
                        break
                row.append(my_duty)
            writer.writerow(row)

def export_by_duty(date_list, date_hash, filename="result_by_duty.csv"):
    headers = ["근무항목"] + date_list
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for duty in duty_types:
            row = [duty]
            for day in date_list:
                today_res = date_hash.get(day)
                val = today_res.get(duty)
                row.append(get_names(val))
            writer.writerow(row)

# 6. 실행
export_by_date(date_list, date_hash)
export_by_person(date_list, date_hash, worker_data)
export_by_duty(date_list, date_hash)

print("\n" + "="*40)
print("✅ 근무표 생성 완료!")
print("1. result_by_date.csv")
print("2. result_by_person.csv")
print("3. result_by_duty.csv")
print("="*40)
