/**
 * [Admin Duty System Logic]
 * 역할: UI 입력값 수집, 파일 업로드, 엔진 가동 요청 및 로그 출력
 */

const Duty = Object.freeze({
    SUB_GUARDIAN: 0, 
    DISHWASHER: 1,
    NIGHT_WATCH: 2,
    SENTINEL: 3,     
    CCTV_MONITOR: 4       
});

let clickState = new Bitmask5()
let eventList = new LinkedList()


// 로그 창에 텍스트를 출력하는 유틸리티 함수 (시스템 모니터링용)
function log(message) {
    const logWindow = document.getElementById('logWindow');
    const now = new Date().toLocaleTimeString();
    logWindow.innerHTML += `<div>[${now}] ${message}</div>`;
    logWindow.scrollTop = logWindow.scrollHeight; // 최신 로그로 스크롤
}

// 파일을 텍스트(UTF-8)로 읽어오는 비동기 함수
const readFileAsText = (file) => new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (e) => resolve(e.target.result);
    reader.onerror = (e) => reject(e);
    reader.readAsText(file);
});

function registerOrDelte(targetButton, eventType) {
    if (clickState.isSet(eventType)) {
        targetButton.style.backgroundColor = ""; // 원래대로
        eventList.remove(eventType)
    }    
    else {
        targetButton.style.backgroundColor = "yellow"; // 누른 채로 저장되는 느낌
        eventList.append(eventType)
    }
    clickState.toggle(eventType)
    console.log("현재 순서:", eventList.toArray());
}


async function runPipeline() {
    log("🚀 파이프라인 가동 시작...");

    try {
        // 1. DOM 데이터 캡처 (데이터 패킷 조립)
        const workerFile = document.getElementById('workerFile').files[0];
        const exceptionFile = document.getElementById('exceptionFile').files[0];
        
        const payload = {
            startDate: document.getElementById('startDate').value,
            endDate: document.getElementById('endDate').value,
            ldDate: document.getElementById('ldDate').value,
            lastWorkers: {
                sub: document.getElementById('lastSub').value,
                dish: document.getElementById('lastDish').value,
                night: document.getElementById('lastNight').value,
                sr: document.getElementById('lastSr').value,
                jr: document.getElementById('lastJr').value,
                cctv: document.getElementById('lastCctv').value
            },
            eventArr: eventList.toArray() 
        };

        // 2. 유효성 검사 (입력값 누락 방지 가드 루틴)
        if (!payload.startDate || !payload.endDate || !payload.ldDate) {
            alert("❌ 날짜 설정이 누락되었습니다.");
            log("⚠️ 에러: 필수 날짜 데이터 누락");
            return;
        }

        // 3. 파일 업로드 단계 (Data Synchronization)
        if (workerFile) {
            log(`파일 전송 중: ${workerFile.name}...`);
            const content = await readFileAsText(workerFile);
            await fetch('/upload', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ fileName: 'worker_list.csv', content: content })
            });
            log("✅ 병사 명단 동기화 완료.");
        }

        if (exceptionFile) {
            log(`파일 전송 중: ${exceptionFile.name}...`);
            const content = await readFileAsText(exceptionFile);
            await fetch('/upload', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ fileName: 'exception_list.csv', content: content })
            });
            log("✅ 열외 일정 동기화 완료.");
        }

        // 4. 엔진 가동 요청 (Core Engine Execution)
        log("⚙️ 근무 배정 엔진 연산 시작...");
        const response = await fetch('/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const result = await response.json();

        if (response.ok && result.status === "success") {
            log("✅ 배정 완료! 파일 다운로드를 시작합니다.");
        
            const download = (content, filename) => {
                const blob = new Blob([content], { type: 'text/csv;charset=utf-8;' });
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
            };
        
            // 서버가 보내준 두 파일을 각각 다운로드
            if (result.files.byDate) download(result.files.byDate, `근무표_날짜별.csv`);
            if (result.files.byPerson) download(result.files.byPerson, `근무표_인원별.csv`);
        
            alert("🎉 생성이 완료되었습니다! '다운로드' 폴더를 확인하세요.");
        } else {
            throw new Error(result.message);
        }

    } catch (err) {
        log(`❌ 런타임 에러 발생: ${err.message}`);
        alert("시스템 오류: " + err.message);
    }
}

// 버튼에 이벤트 리스너 바인딩 (Trigger 설정)
document.getElementById('runButton').addEventListener('click', runPipeline);
