import calendar
from data_structures import Circular_List, List_Pointer, ChainingHashTable
from duty_engine import (
    load_all_data, get_start_index, get_next_available, 
    is_date_in_range, export_results, worker_info_map
)

def main():
    # 1. 데이터 로드
    # worker_list.csv: 군번,이름,전입일,전역일,고정제외보직
    # exception_list.csv: 군번,시작일,종료일,사유
    try:
        worker_data, exceptions = load_all_data('./worker_list.csv', './exception_list.csv')
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

    ptr_sub_guard = List_Pointer(c_list_all, get_start_index(c_list_all, last_sub))
    ptr_dish = List_Pointer(c_list_all, get_start_index(c_list_all, last_dish))
    ptr_night = List_Pointer(c_list_all, get_start_index(c_list_all, last_night))
    ptr_sr_sentinel = List_Pointer(c_list_sr, get_start_index(c_list_sr, last_sr))
    ptr_jr_sentinel = List_Pointer(c_list_jr, get_start_index(c_list_jr, last_jr))
    ptr_cctv = List_Pointer(c_list_all, get_start_index(c_list_all, last_cctv))

    # 4. 배정 년/월 및 날짜 리스트 생성
    print("\n배정 년/월 입력 (예: 2026 1):")
    year, month = map(int, input().split())
    date_list = [day.strftime("%m-%d") for week in calendar.Calendar().monthdatescalendar(year, month) 
                 for day in week if day.month == month]

    duty_types = ["위병부조장", "식기"] + [f"불침번{i}" for i in range(1,6)] + ["초병_1조", "초병_2조"] + [f"CCTV{i}" for i in range(1,7)]
    date_hash = ChainingHashTable(40)

    # 5. 배정 시작
    dish_skip_count = 0
    for day in date_list:
        today_duty = ChainingHashTable(20)
        for d in duty_types + ["열외"]: today_duty.set(d, [])
        
        # 열외자 등록
        assigned_today = set()
        for ex in exceptions:
            if is_date_in_range(day, ex['시작일'], ex['종료일']):
                today_duty.get("열외").append(ex['군번'])
                assigned_today.add(ex['군번'])
        
        # --- 배정 순서 반영 ---
        
        # 1. 위병부조장
        today_duty.get("위병부조장").append(get_next_available(ptr_sub_guard, assigned_today, "위병부조장"))
        
        # 2. 식기
        dish_skip_count += 1
        if dish_skip_count % 5 == 0:
            today_duty.get("식기").append('72사단')
        else:
            for _ in range(3):
                today_duty.get("식기").append(get_next_available(ptr_dish, assigned_today, "식기"))

        # 3. 불침번
        for i in range(1, 6):
            today_duty.get(f"불침번{i}").append(get_next_available(ptr_night, assigned_today, "불침번"))

        # 4. 초병 (1조, 2조)
        for t in ["초병_1조", "초병_2조"]:
            today_duty.get(t).append(get_next_available(ptr_sr_sentinel, assigned_today, "초병"))
            today_duty.get(t).append(get_next_available(ptr_jr_sentinel, assigned_today, "초병"))

        # 5. CCTV
        for i in range(1, 7):
            for _ in range(3):
                today_duty.get(f"CCTV{i}").append(get_next_available(ptr_cctv, assigned_today, "CCTV"))

        date_hash.set(day, today_duty)

    # 6. 결과 출력
    export_results(date_list, date_hash, worker_data, duty_types)

    print("\n" + "="*40)
    print("✅ 근무표 생성 및 파일 저장 완료!")
    print("="*40)

if __name__ == "__main__":
    main()