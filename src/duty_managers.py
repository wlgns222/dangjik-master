import src.data_store as ds 
from .data_structures import *
from .date import is_weekend, get_date_diff
from .duty_engine import global_filter, get_start_index, get_next_available
from .constants import (DUTY_ENUM, ALL_DUTY_KEYS, SB_GUARD_KEY, DISH_KEY, 
                        NIGHT_WATCH_KEYS, CCTV_KEYS, SENTINEL_KEYS)
import csv

# ==========================================
# 1. 매니저 부모 클래스 (공통 로직)
# ==========================================
class Manager:
    def get_assigned_today(self, day) -> set:
        assigned_today = set()
        # 모든 근무 키와 열외(전역/전대기 포함) 키를 합쳐서 순회
        for h_key in (ALL_DUTY_KEYS + ds.all_exp_keys): 
            workers = ds.date_event_hash.get(day).get(h_key)
            if workers:  # None 방어
                for w in workers:
                    assigned_today.add(w)
        return assigned_today

    def delManage(self):
        pass

# ==========================================
# 2. 열외 관리 매니저
# ==========================================
class ExpManager(Manager):
    def runManage(self):
        global_filter()

# ==========================================
# 3. 개별 근무 배정 매니저들
# ==========================================
class SubGuardManager(Manager):
    def __init__(self):
        self.c_list = ds.worker_list 

    def runManage(self, last_run) -> None:
        ptr_sub_guard = List_Pointer(self.c_list, get_start_index(self.c_list, last_run))
        
        for day in ds.date_list:
            event_hash = ds.date_event_hash.get(day)
            assigned_today = self.get_assigned_today(day)
            
            next_worker = get_next_available(ptr_sub_guard, assigned_today, DUTY_ENUM.SUB_GUARD)
            event_hash.get(SB_GUARD_KEY).append(next_worker)

class DishManager(Manager):
    def __init__(self):
        self.c_list = ds.worker_list 

    def runManage(self, last_run, ld_date) -> None: # ld_date(주말 식기 등 특수 규칙용)
        ptr_dish = List_Pointer(self.c_list, get_start_index(self.c_list, last_run))
        
        for day in ds.date_list:
            event_hash = ds.date_event_hash.get(day)
            assigned_today = self.get_assigned_today(day)

            if get_date_diff(day, ld_date) % 5 == 0 :
                event_hash.get(DISH_KEY).append('72사단')
            else :
                for _ in range(3) :
                    next_worker = get_next_available(ptr_dish, assigned_today, DUTY_ENUM.DISH)
                    event_hash.get(DISH_KEY).append(next_worker)

class NightManager(Manager):
    def __init__(self):
        self.c_list = ds.worker_list 

    def runManage(self, last_run) -> None:
        ptr_night = List_Pointer(self.c_list, get_start_index(self.c_list, last_run))
        
        for day in ds.date_list:
            event_hash = ds.date_event_hash.get(day)
            for key in NIGHT_WATCH_KEYS:
                assigned_today = self.get_assigned_today(day)
                next_worker = get_next_available(ptr_night, assigned_today, DUTY_ENUM.NIGHT)
                event_hash.get(key).append(next_worker)

class CCTVManager(Manager):
    def __init__(self):
        self.c_list = ds.worker_list 

    def runManage(self, last_run) -> None:
        ptr_cctv = List_Pointer(self.c_list, get_start_index(self.c_list, last_run))
        
        for day in ds.date_list:
            event_hash = ds.date_event_hash.get(day)
            for key in CCTV_KEYS:
                assigned_today = self.get_assigned_today(day)
                
                for _ in range(3) :
                    next_worker = get_next_available(ptr_cctv, assigned_today, DUTY_ENUM.CCTV)
                    event_hash.get(key).append(next_worker)

class SentinelManager(Manager):
    def __init__(self):
        length = ds.worker_list.length()
        mid = length // 2
        
        self.c_list_sr = Circular_List(ds.worker_list.get_slice_list(0, mid))
        self.c_list_jr = Circular_List(ds.worker_list.get_slice_list(mid, length))

    def runManage(self, last_run_sr, last_run_jr) -> None:
        ptr_st_sr = List_Pointer(self.c_list_sr, get_start_index(self.c_list_sr, last_run_sr))
        ptr_st_jr = List_Pointer(self.c_list_jr, get_start_index(self.c_list_jr, last_run_jr))

        for day in ds.date_list:
            if not is_weekend(day):
                event_hash = ds.date_event_hash.get(day)
                assigned_today = self.get_assigned_today(day)
                
                for key in SENTINEL_KEYS:
                    if "선임" in key:
                        next_worker = get_next_available(ptr_st_sr, assigned_today, DUTY_ENUM.SENTINEL)
                        event_hash.get(key).append(next_worker)
                    elif "후임" in key:
                        next_worker = get_next_available(ptr_st_jr, assigned_today, DUTY_ENUM.SENTINEL)
                        event_hash.get(key).append(next_worker)

# ==========================================
# 4. 전체 총괄 엔진 (메인 컨트롤러 연결부)
# ==========================================
class MainEngine:
    def __init__(self, date_range, worker_data, exceptions):
        # 1. ds(data_store)의 초기화 함수들을 일괄 호출하여 메모리에 데이터 적재
        ds.load_date_list(date_range[0], date_range[1])
        ds.load_all_exp_keys(exceptions)
        ds.load_exp_list(exceptions)
        ds.load_worker_list(worker_data)
        ds.load_worker_info_map(worker_data)
        ds.init_date_event_hash()
        
        # 2. 매니저들 초기화
        self.exp_manager = ExpManager()
        self.sg_manager = SubGuardManager()
        self.dish_manager = DishManager()
        self.night_manager = NightManager()
        self.cctv_manager = CCTVManager()
        self.st_manager = SentinelManager()

    def reset_all_event(self):
        # 부모 클래스의 delManage가 호출되므로 안전하게 동작
        self.exp_manager.delManage()
        self.sg_manager.delManage()
        self.dish_manager.delManage()
        self.night_manager.delManage()
        self.cctv_manager.delManage()
        self.st_manager.delManage()

    def __get_hash_to_matrix_type1(self) -> list:
        # CSV 내보내기를 위한 2차원 배열 변환
        num_dates = len(ds.date_list)
        num_workers = ds.worker_list.length()
        matrix = [[' '] * (num_dates + 2) for _ in range(num_workers)]
        
        for i in range(num_workers):
            worker_id = ds.worker_list.get_at(i)
            worker_info = ds.worker_info_map.get(worker_id)
            matrix[i][0] = worker_info['군번']
            matrix[i][1] = worker_info.get('이름', '알수없음')
            for j in range(num_dates):
                day = ds.date_list[j]
                day_hash = ds.date_event_hash.get(day)
                
                for event in (ALL_DUTY_KEYS + ds.all_exp_keys):
                    run_worker_list = day_hash.get(event)
                    if run_worker_list and worker_id in run_worker_list:
                        matrix[i][j+2] = event
        return matrix

    def export_result_as_file(self, file_name):
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            header = ['군번', '이름'] + ds.date_list
            writer.writerow(header)
            
            for row in self.__get_hash_to_matrix_type1():
                writer.writerow(row)