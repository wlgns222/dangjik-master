import os
import csv
import src.data_store as ds 
from .duty_managers import MainEngine
from .constants import DUTY_ENUM

def load_data(worker_file, exception_file, holiday_file):
    worker_data = []
    # 1. 인명부 로드
    with open(worker_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            worker_data.append(row)
            
    # 2. 열외 명단 로드
    exceptions = []
    with open(exception_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            exceptions.append(row)

    # 3. 공휴일 명단 로드
    holiday_data = []
    with open(holiday_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            holiday_data.append(row)
            
    return worker_data, exceptions, holiday_data


def duty_generator(start_date, end_date, ld_date, last_workers, event_list):
    # 경로 설정
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_path = os.path.dirname(current_dir)

    worker_path = os.path.join(root_path, "data", "용사명단.csv")
    exception_path = os.path.join(root_path, "data", "열외일정.csv")
    holiday_path = os.path.join(root_path, "data", "공휴일.csv")
    output_path = os.path.join(root_path, "data", "근무공정표.csv")
    #downloads = os.path.join(os.path.expanduser('~'), 'Downloads')
    #download_path = os.path.join(downloads, "근무공정표.csv")

    # 1. 데이터 읽어오기
    try:
        worker_data, exceptions, holiday_data = load_data(worker_path, exception_path, holiday_path)
    except FileNotFoundError:
        raise ValueError("업로드된 명단 파일을 찾을 수 없습니다.")

    ds.load_holiday(holiday_data)

    # 2. 메인 엔진 가동 (데이터 스토어 적재 및 매니저 초기화 일괄 수행)
    date_range = (start_date, end_date)
    engine = MainEngine(date_range, worker_data, exceptions)
    
    # 3. 달력에 전역자, 열외자 도장 먼저 찍기 (가장 중요!)
    engine.exp_manager.runManage()

    # 4. 우선순위에 따라 배정 실행
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
            
    # 5. CSV 파일 출력
    engine.export_result_as_file(output_path)
    #engine.export_result_as_file(download_path)

    # 생성된 파일의 절대 경로를 반환 (server.py에서 다운로드할 수 있도록)
    return output_path