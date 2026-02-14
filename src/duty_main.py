import os
from .event_managers import *

def load_data(worker_file, exception_file):
    worker_data = []
    
    # 1. 인명부 로드
    with open(worker_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            worker_data.append(row)
            
    # 2. 열외 명단 로드 (데이터 로직 내에서 활용하기 위해 리스트화)
    exceptions = []
    with open(exception_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            exceptions.append(row)
            
    return worker_data, exceptions

def duty_generator(start_date, end_date, ld_date, last_workers, event_list):
    # server.py와 동일한 절대 경로 로직 사용
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_path = os.path.dirname(current_dir)

    worker_path = os.path.join(root_path, "data", "worker_list.csv")
    exception_path = os.path.join(root_path, "data", "exception_list.csv")

    try:
        worker_data, exceptions = load_data(worker_path, exception_path)
    except FileNotFoundError:
        raise ValueError("업로드된 명단 파일을 찾을 수 없습니다.")

    date_range = (start_date, end_date)
    engine = MainEngine(date_range, worker_data, exceptions)
    engine.exp_manager.runManage()

    for event in event_list:
        if event == DUTY_ENUM.SUB_GUARD:
            engine.sg_manager.runManage(last_workers.get('sub'))
        elif event == DUTY_ENUM.DISH:
            engine.dish_manager.runManage(last_workers.get('dish'), ld_date)
        elif event == DUTY_ENUM.NIGHT:
            engine.night_manager.runManage(last_workers.get('night'))
        elif event == DUTY_ENUM.SENTINEL:
            engine.st_manager.runManage(last_workers.get('sr'), last_workers.get('jr'))
        elif event == DUTY_ENUM.CCTV:
            engine.cctv_manager.runManage(last_workers.get('cctv'))       

    engine.export_result_as_file('result_file.csv')

    return "SUCCESS: 근무표 생성이 완료되었습니다."