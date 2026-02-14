import src.main_data_loaders as md 
from .date import *
from .sub_logic import *
from .filter import global_filter
import csv

class Manager:
    def get_assigned_today(self, day)->set:
        assigned_today = set()
        for h_key in (md.all_duty_keys+md.all_exp_keys): # 'all_duty_keys, exp_keys' from 'main_data file'
            for w in md.date_event_hash.get(day).get(h_key):
                assigned_today.add(w)
        return assigned_today

class ExpManager(Manager):
    def runManage(self):
        global_filter(md.date_event_hash, md.date_list, md.exp_list)


class SubGuardManager(Manager):
    def __init__(self):
        self.c_list: Circular_List = md.worker_list #worker_list from main_data file

    def runManage(self, last_run)->None:
        ptr_sub_guard = List_Pointer(self.c_list, get_start_index(self.c_list, last_run))
        
        for day in md.date_list:
            event_hash: ChainingHashTable = md.date_event_hash.get(day)
            assigned_today: set = self.get_assigned_today(day)
            event_hash.get(md.sb_guard_key).append(get_next_available(ptr_sub_guard, assigned_today, DUTY_ENUM.SUB_GUARD))

class DishManager(Manager):
    def __init__(self):
        self.c_list: Circular_List = md.worker_list #worker_list from main_data file

    def runManage(self, last_run, ld_date)->None:
        ptr_dish = List_Pointer(self.c_list, get_start_index(self.c_list, last_run))
        for day in md.date_list:
            event_hash: ChainingHashTable = md.date_event_hash.get(day)
            assigned_today: set = self.get_assigned_today(day)
            
            if get_date_diff(day, ld_date) % 5 == 0:
                event_hash.get(md.dish_key).append('72사단')
            else:
                for _ in range(3):
                    event_hash.get(md.dish_key).append(get_next_available(ptr_dish, assigned_today, DUTY_ENUM.DISH))

class NightManager(Manager):
    def __init__(self):
        self.c_list: Circular_List = md.worker_list #worker_list from main_data file

    def runManage(self, last_run)->None:
        ptr_night = List_Pointer(self.c_list, get_start_index(self.c_list, last_run))
        for day in md.date_list:
            event_hash: ChainingHashTable = md.date_event_hash.get(day)
            assigned_today: set = self.get_assigned_today(day)

            for n_key in md.night_watch_keys:
                event_hash.get(n_key).append(get_next_available(ptr_night, assigned_today, DUTY_ENUM.NIGHT))

class CCTVManager(Manager):
    def __init__(self):
        self.c_list: Circular_List = md.worker_list #worker_list from main_data file

    def runManage(self, last_run)->None:
        ptr_cctv = List_Pointer(self.c_list, get_start_index(self.c_list, last_run))
        for day in md.date_list:
            event_hash: ChainingHashTable = md.date_event_hash.get(day)
            assigned_today: set = self.get_assigned_today(day)

            for c_key in md.cctv_keys:
                for _ in range(3):
                    event_hash.get(c_key).append(get_next_available(ptr_cctv, assigned_today, DUTY_ENUM.NIGHT))

class SentinelManager(Manager):
    def __init__(self):
        length = md.worker_list.length()
        mid = md.worker_list.length() // 2
        self.c_list_sr = Circular_List(md.worker_list.get_slice_list(0, mid))
        self.c_list_jr = Circular_List(md.worker_list.get_slice_list(mid, length))

    def runManage(self, last_sr_run, last_jr_run)->None:
        ptr_sr_sentinel = List_Pointer(self.c_list_sr, get_start_index(self.c_list_sr, last_sr_run))
        ptr_jr_sentinel = List_Pointer(self.c_list_jr, get_start_index(self.c_list_jr, last_jr_run))
        for day in md.date_list:
            event_hash: ChainingHashTable = md.date_event_hash.get(day)
            assigned_today: set =self.get_assigned_today(day)

            for s_key in md.sentinel_keys:
                w1 = get_next_available(ptr_sr_sentinel, assigned_today, DUTY_ENUM.SENTINEL)
                w2 = get_next_available(ptr_jr_sentinel, assigned_today, DUTY_ENUM.SENTINEL)
                event_hash.get(s_key).append(w1)
                event_hash.get(s_key).append(w2)



class MainEngine:
    def __init__(self, date_range, worker_data, exp_data):
        md.load_all_data(date_range, worker_data, exp_data)
        self.exp_manager = ExpManager()
        self.sg_manager = SubGuardManager()
        self.dish_manager = DishManager()
        self.night_manager = NightManager()
        self.cctv_manager = CCTVManager()
        self.st_manager = SentinelManager()


    def reset_all_event(self):
        self.exp_manager.delManage()
        self.sg_manager.delManage()
        self.dish_manager.delManage()
        self.night_manager.delManage()
        self.cctv_manager.delManage()
        self.st_manager.delManage()

    def __get_hash_to_matrix_type1(self)->list:
            # matrix 가로 길이는 (날짜 수 + 이름 컬럼 1개)
            num_dates = len(md.date_list)
            num_workers = md.worker_list.length()
            matrix = [[' '] * (num_dates + 1) for _ in range(num_workers)]
            
            for i in range(num_workers):
                worker_id = md.worker_list.get_at(i)
                matrix[i][0] = md.worker_info_map.get(worker_id)['군번']
                for j in range(num_dates):
                    day = md.date_list[j]
                    day_hash = md.date_event_hash.get(day)
                    for event in (md.all_duty_keys + md.all_exp_keys):
                        run_worker_list = day_hash.get(event)
                        if worker_id in run_worker_list:
                            matrix[i][j+1] = event
            return matrix

    def export_result_as_file(self, file_name):
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(["이름"] + md.date_list)
            matrix = self.__get_hash_to_matrix_type1()
            for row in matrix:
                writer.writerow(row)
                

