import os
from .data_structures import Circular_List, List_Pointer, ChainingHashTable
from .date import get_date_diff, get_custom_date_list
from .filter import global_filter
from .duty_engine import (
    load_all_data, get_start_index, get_next_available, 
    export_results, get_all_exp, DUTY_ENUM
)

def duty_generator(start_date, end_date, ld_date, last_workers):
    # server.py와 동일한 절대 경로 로직 사용
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_path = os.path.dirname(current_dir)

    worker_path = os.path.join(root_path, "data", "worker_list.csv")
    exception_path = os.path.join(root_path, "data", "exception_list.csv")

    try:
        worker_data, exceptions = load_all_data(worker_path, exception_path)
    except FileNotFoundError:
        raise ValueError("업로드된 명단 파일을 찾을 수 없습니다.")

    # 2. 인원 분류 및 Circular Queue 최적화
    worker_data.sort(key=lambda x: x['전입일'])
    mid = len(worker_data) // 2
    
    c_list_all = Circular_List()
    for w in worker_data: c_list_all.append(w['군번'])
    
    c_list_sr = Circular_List()
    for w in worker_data[:mid]: c_list_sr.append(w['군번'])
    
    c_list_jr = Circular_List()
    for w in worker_data[mid:]: c_list_jr.append(w['군번'])

    # 3. GUI에서 넘어온 마지막 근무자 데이터를 포인터에 바인딩
    ptr_sub_guard = List_Pointer(c_list_all, get_start_index(c_list_all, last_workers.get('sub')))
    ptr_dish = List_Pointer(c_list_all, get_start_index(c_list_all, last_workers.get('dish')))
    ptr_night = List_Pointer(c_list_all, get_start_index(c_list_all, last_workers.get('night')))
    ptr_sr_sentinel = List_Pointer(c_list_sr, get_start_index(c_list_sr, last_workers.get('sr')))
    ptr_jr_sentinel = List_Pointer(c_list_jr, get_start_index(c_list_jr, last_workers.get('jr')))
    ptr_cctv = List_Pointer(c_list_all, get_start_index(c_list_all, last_workers.get('cctv')))

    # 4. 배정 데이터 구조(HashTable) 초기화
    date_list = get_custom_date_list(start_date, end_date)
    duty_types = ["위병부조장", "식기"] + [f"불침번{i}" for i in range(1,6)] + ["초병_1조", "초병_2조"] + [f"CCTV{i}" for i in range(1,7)]
    exp_types = get_all_exp(exceptions)
    
    date_hash = ChainingHashTable(len(date_list) * 2)
    for day in date_list:
        today_duty = ChainingHashTable(30)
        for e in exp_types : today_duty.set(e, [])
        for d in duty_types : today_duty.set(d, [])
        date_hash.set(day, today_duty)

    # 5. 전역 필터 적용 (휴가/열외자 선배정)
    global_filter(date_hash, date_list, exceptions)

    # 6. 메인 배정 루프
    for day in date_list:
        today_duty = date_hash.get(day)
        assigned_today = set()
        
        # 열외 인원 사전 점유
        for e in exp_types:
            for exp_worker in today_duty.get(e): 
                assigned_today.add(exp_worker)

        # 각 보직별 순차 배정 로직 (기존 알고리즘 유지)
        today_duty.get("위병부조장").append(get_next_available(ptr_sub_guard, assigned_today, DUTY_ENUM.SUB_GUARD))
        
        if get_date_diff(day, ld_date) % 5 == 0:
            today_duty.get("식기").append('72사단')
        else:
            for _ in range(3):
                today_duty.get("식기").append(get_next_available(ptr_dish, assigned_today, DUTY_ENUM.DISH))

        for i in range(1, 6):
            today_duty.get(f"불침번{i}").append(get_next_available(ptr_night, assigned_today, DUTY_ENUM.NIGHT))

        for t in ["초병_1조", "초병_2조"]:
            today_duty.get(t).append(get_next_available(ptr_sr_sentinel, assigned_today, DUTY_ENUM.SENTINEL))
            today_duty.get(t).append(get_next_available(ptr_jr_sentinel, assigned_today, DUTY_ENUM.SENTINEL))

        for i in range(1, 7):
            for _ in range(3):
                today_duty.get(f"CCTV{i}").append(get_next_available(ptr_cctv, assigned_today, DUTY_ENUM.CCTV))

    # 7. 결과 익스포트 및 성공 신호 반환
    export_results(date_list, date_hash, worker_data, duty_types+exp_types)
    return "SUCCESS: 근무표 생성이 완료되었습니다."