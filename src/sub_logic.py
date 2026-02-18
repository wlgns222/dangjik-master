from enum import IntEnum
from .data_structures import ChainingHashTable, Circular_List, List_Pointer
from .filter import task_filter

from .main_data_loaders import worker_info_map 

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
