# 📅 당직마스터 (Dangjik-Master)

군 부대 특성을 반영한 **로컬 웹 기반 근무 자동 편성 프로그램**입니다.
복잡한 부대 규정, 열외(휴가/파견/전역 등) 일정, 그리고 특수 보직(1호차 운전병 등)의 예외적인 스케줄을 모두 고려하여 공정하고 연속적인 근무표를 자동으로 생성합니다.

---

## 1. 주요 기능
- **근무자 자동 배정:** 용사 명단과 우선순위를 바탕으로 불침번, 초병, 식기, CCTV 등 각종 근무 자동 편성
- **정교한 열외 처리:** 휴가, 파견, 전역 및 전역 대기자를 달력에서 자동으로 필터링
- **특수 보직 맞춤형 알고리즘:** '1호차 운전병' 등 요일과 공휴일 여부에 따라 근무 조건이 달라지는 특수 행마법 완벽 지원
- **사용자 친화적 GUI:** 로컬 브라우저 환경에서 직관적인 날짜/우선순위 설정 가능
- **엑셀(CSV) 다운로드:** 한글 깨짐 방지 처리가 된 CSV 파일 자동 생성 및 다운로드

---

## 2. 시스템 아키텍처 및 폴더 구조

본 시스템은 외부 인터넷 연결이 불가능한 인트라넷 환경을 고려하여, **Python 기본 라이브러리만을 활용한 로컬 서버-클라이언트 구조**로 개발되었습니다.

```text
📦 dangjik-master
 ┣ 📂 data/          # 배정을 위한 기초 데이터 (용사명단, 열외일정, 공휴일 CSV)
 ┣ 📂 gui/           # 프론트엔드 (HTML, CSS, JS) - 사용자와 상호작용
 ┣ 📂 src/           # 백엔드 핵심 엔진 (근무 배정 알고리즘)
 ┃ ┣ 📜 main_controller.py # 데이터 로드 및 전체 엔진 가동 (컨트롤 타워)
 ┃ ┣ 📜 duty_engine.py     # ⭐️ 핵심 규칙 엔진 (자격 검증, 특수 보직 필터링)
 ┃ ┣ 📜 duty_managers.py   # 각 근무별(불침번, 초병 등) 배정 로직 수행
 ┃ ┣ 📜 data_store.py      # 전역 데이터 상태 관리
 ┃ ┣ 📜 data_structures.py # 자료구조 (원형 연결 리스트, 해시테이블 등)
 ┃ ┗ 📜 ... 
 ┣ 📜 server.py      # HTTP 로컬 서버 (GUI와 엔진 간의 통신 담당)
 ┗ 📜 dangjik-master.bat # 원클릭 실행 배치 파일
```

### 데이터 처리 흐름 (Workflow)
1. **[사용자]** 웹 GUI에서 날짜/근무 순서를 설정하고 '가동' 클릭 (`gui/api.js`)
2. **[서버]** `server.py`가 데이터를 JSON으로 받아 `main_controller.py`의 `duty_generator` 호출
3. **[엔진]** 휴가자/열외자를 우선 제외한 뒤, 각 근무 Manager들이 엔진(`duty_engine.py`)의 자격 검증을 거쳐 근무자 선발
4. **[출력]** 생성된 근무표를 CSV 포맷의 텍스트로 변환하여 브라우저로 반환, 자동 다운로드

---

## 3. 향후 유지보수 가이드 (For Future Developers)

부대 사정에 따라 새로운 특수 보직이 생기거나, 근무 규칙이 변경될 경우 아래의 가이드를 참고하여 코드를 수정하세요.

### Q1. 새로운 특수 보직을 추가하려면?
기존의 핵심 배정 로직을 건드릴 필요 없이, **`src/duty_engine.py`** 파일만 수정하면 됩니다. 이 프로그램은 **라우터(Router) 패턴**을 사용하여 보직별 규칙을 독립적으로 관리합니다.

**수정 방법:**
1. `duty_engine.py` 상단에 새 보직을 위한 필터 함수를 만듭니다. (반환값이 `True`면 배정 가능, `False`면 배정 불가)
```python
def OO_filter(target_date, next_date, duty_type):
    pass
```
2. 같은 파일에 있는 `special_role_filter` 함수(라우터)에 조건을 추가합니다.
```python
def special_role_filter(sn, day_str, duty_type):
    worker = ds.worker_info_map.get(sn)
    role = worker.get('비고')
    
    if role == '1호차 운전병':
        return commander_driver_filter(target_date, next_date, duty_type)
    elif role == 'OO병':               # <--- 이 부분 추가!
        return OO_filter(target_date, next_date, duty_type)  # <--- 이 부분 추가!
```

### Q2. 새로운 종류의 근무가 생겼다면?
1. `src/constants.py` 에 새로운 근무 상수를 추가합니다.
2. `src/duty_managers.py` 에 기존 `Manager` 클래스를 상속받는 `OOO`를 새로 작성합니다.
3. `src/main_controller.py` 의 배정 실행 루프에 해당 매니저를 추가합니다.

---
## 📄 4. 라이선스 (License)

이 프로젝트는 **MIT License**를 따릅니다. 
누구나 무료로 자유롭게 사용, 수정, 배포할 수 있으며, 군 부대 내 공개 SW 반입 규정에 적합하게 설계되었습니다. 자세한 내용은 `LICENSE` 파일을 참고하세요.
