import os
import csv
from .duty_managers import MainEngine
from .constants import DUTY_ENUM

def load_data(worker_file, exception_file):
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
            
    return worker_data, exceptions


def duty_generator(start_date, end_date, ld_date, last_workers, event_list):
    # 경로 설정
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_path = os.path.dirname(current_dir)

    worker_path = os.path.join(root_path, "data", "worker_list.csv")
    exception_path = os.path.join(root_path, "data", "exception_list.csv")
    output_path = os.path.join(root_path, "data", "근무공정표.csv")

    # 1. 데이터 읽어오기
    try:
        worker_data, exceptions = load_data(worker_path, exception_path)
    except FileNotFoundError:
        raise ValueError("업로드된 명단 파일을 찾을 수 없습니다.")

    # 2. 메인 엔진 가동 (데이터 스토어 적재 및 매니저 초기화 일괄 수행)
    date_range = (start_date, end_date)
    engine = MainEngine(date_range, worker_data, exceptions)
    
    # 3. 달력에 전역자, 열외자 도장 먼저 찍기 (가장 중요!)
    engine.exp_manager.runManage()

    # 4. 프론트엔드(UI)에서 전달받은 우선순위(event_list)에 따라 배정 실행
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
            
    # 5. 모든 배정이 끝난 달력을 CSV 엑셀 파일로 출력
    engine.export_result_as_file(output_path)
    
    # 생성된 파일의 절대 경로를 반환 (server.py에서 다운로드할 수 있도록)
    return output_path