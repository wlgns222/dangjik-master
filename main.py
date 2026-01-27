from src.data_structures import Circular_List, List_Pointer, ChainingHashTable
from src.date import is_date_in_range, get_date_list
from src.filter import global_filter, task_filter
from src.duty_engine import (
    load_all_data, get_start_index, get_next_available, 
    export_results, worker_info_map, get_all_exp, DUTY_ENUM
)

def main():
    # 1. 데이터 로드
    # worker_list.csv
    # exception_list.csv
    try:
        worker_data, exceptions = load_all_data('./data/worker_list.csv', './data/exception_list.csv')
    except FileNotFoundError as e:
        print(f"파일을 찾을 수 없습니다: {e}")
        return

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
    last_dish = input("식기 마지막 인원: ")
    last_night = input("불침번 마지막 인원: ")
    last_sr = input("선임초병 마지막 인원: ")
    last_jr = input("후임초병 마지막 인원: ")
    last_cctv = input("CCTV 마지막 인원: ")
    ld_y, ld_m, ld_d = map(int, input("식기 마지막 날 (예: 2026 01 05): ").split())
    
    ld_date = get_formatted_date(ld_y, ld_m, ld_d)
    
    ptr_sub_guard = List_Pointer(c_list_all, get_start_index(c_list_all, last_sub))
    ptr_dish = List_Pointer(c_list_all, get_start_index(c_list_all, last_dish))
    ptr_night = List_Pointer(c_list_all, get_start_index(c_list_all, last_night))
    ptr_sr_sentinel = List_Pointer(c_list_sr, get_start_index(c_list_sr, last_sr))
    ptr_jr_sentinel = List_Pointer(c_list_jr, get_start_index(c_list_jr, last_jr))
    ptr_cctv = List_Pointer(c_list_all, get_start_index(c_list_all, last_cctv))

    # 4. 배정 년/월 및 날짜 리스트 생성
    print("\n배정 년/월 입력 (예: 2026 1):")
    year, month = map(int, input().split())
    date_list = get_date_list(year, month)

    duty_types = ["위병부조장", "식기"] + [f"불침번{i}" for i in range(1,6)] + ["초병_1조", "초병_2조"] + [f"CCTV{i}" for i in range(1,7)]
    exp_types = get_all_exp(exceptions)
    
    date_hash = ChainingHashTable(40)
 
    for day in date_list:
        today_duty = ChainingHashTable(20)
        for e in exp_types : today_duty.set(e, [])
        for d in duty_types : today_duty.set(d, [])
        date_hash.set(day, today_duty)

    # 해시테이블에 예외 인원들 미리 작성
    global_filter(date_hash, date_list, exceptions)

    # 5. 배정 시작
    for day in date_list:
        today_duty = date_hash.get(day)
        
        assigned_today = set()
        
        # 당일 예외인원들 집합에 추가
        for e in exp_types:
            for exp_worker in today_duty.get(e): 
                assigned_today.add(exp_worker)

        # --- 배정 ---
        
        # 1. 위병부조장
        
        today_duty.get("위병부조장").append(get_next_available(ptr_sub_guard, assigned_today, DUTY_ENUM.SUB_GUARD))
        
        # 2. 식기
        if get_date_diff(day, ld_date) % 5 == 0:
            today_duty.get("식기").append('72사단')
        else:
            for _ in range(3):
                today_duty.get("식기").append(get_next_available(ptr_dish, assigned_today, DUTY_ENUM.DISH))

        # 3. 불침번
        for i in range(1, 6):
            today_duty.get(f"불침번{i}").append(get_next_available(ptr_night, assigned_today, DUTY_ENUM.NIGHT))

        # 4. 초병 (1조, 2조)
        for t in ["초병_1조", "초병_2조"]:
            today_duty.get(t).append(get_next_available(ptr_sr_sentinel, assigned_today, DUTY_ENUM.SENTINEL))
            today_duty.get(t).append(get_next_available(ptr_jr_sentinel, assigned_today, DUTY_ENUM.SENTINEL))

        # 5. CCTV
        for i in range(1, 7):
            for _ in range(3):
                today_duty.get(f"CCTV{i}").append(get_next_available(ptr_cctv, assigned_today, DUTY_ENUM.CCTV))

        date_hash.set(day, today_duty)

    # 6. 결과 출력
    export_results(date_list, date_hash, worker_data, duty_types+exp_types)

    print("\n" + "="*40)
    print("✅ 근무표 생성 및 파일 저장 완료!")
    print("="*40)

if __name__ == "__main__":
    main()
