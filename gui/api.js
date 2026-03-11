// api.js

/**
 * [Backend API Communication Logic]
 * 역할: UI 입력값 수집, 파일 업로드, 엔진 가동 요청 및 결과 다운로드
 */

// 1. UI의 문자열을 백엔드가 인식하는 숫자(Enum)로 매핑하는 객체
const DutyEnumMap = {
    '위병부조장': 0, 
    '식기': 1,
    '불침번': 2,
    '초병 (선임/후임)': 3,     
    'CCTV': 4       
};

// 2. 상태 텍스트 업데이트 (기존 logWindow 대체)
function updateStatus(message, isError = false) {
    const statusText = document.querySelector('.form-actions .status-text');
    if (statusText) {
        statusText.textContent = message;
        statusText.style.color = isError ? '#DC2626' : '#2563EB'; // 에러면 빨간색, 정상은 파란색
    }
    console.log(`[System]: ${message}`);
}

// 3. 파일을 텍스트(UTF-8)로 읽어오는 비동기 함수
const readFileAsText = (file) => new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (e) => resolve(e.target.result);
    reader.onerror = (e) => reject(e);
    reader.readAsText(file);
});

// 4. 메인 파이프라인 가동 함수
async function runPipeline() {
    updateStatus("🚀 파이프라인 가동을 시작합니다...");

    try {
        const workerFile = document.getElementById('workerFile').files[0];
        const exceptionFile = document.getElementById('exceptionFile').files[0];
        const holidayFile = document.getElementById('holidayFile').files[0];
        
        // ui.js에서 관리하는 현재 근무 순서를 가져와 숫자로 변환
        const currentOrderStrings = window.getCurrentDutyOrder();
        const eventArr = currentOrderStrings.map(name => DutyEnumMap[name]);

        const payload = {
            startDate: document.getElementById('startDate').value,
            endDate: document.getElementById('endDate').value,
            ldDate: document.getElementById('ldDate').value,
            // pxDate: document.getElementById('pxDate').value, // 추가된 PX병 일정
            lastWorkers: {
                sub: document.getElementById('lastSub').value,
                dish: document.getElementById('lastDish').value,
                night: document.getElementById('lastNight').value,
                sr: document.getElementById('lastSr').value,
                jr: document.getElementById('lastJr').value,
                cctv: document.getElementById('lastCctv').value
            },
            eventArr: eventArr 
        };

        // 유효성 검사 (입력값 누락 방지 가드 루틴)
        if (!payload.startDate || !payload.endDate || !payload.ldDate) {
            updateStatus("❌ 날짜 설정이 누락되었습니다.", true);
            alert("기본 배정 기간 날짜를 모두 입력해 주세요.");
            return;
        }

        // 파일 업로드 단계 (Data Synchronization)
        if (workerFile) {
            updateStatus(`전송 중: ${workerFile.name}...`);
            const content = await readFileAsText(workerFile);
            await fetch('/upload', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ fileName: '용사명단.csv', content: content })
            });
        }

        if (exceptionFile) {
            updateStatus(`전송 중: ${exceptionFile.name}...`);
            const content = await readFileAsText(exceptionFile);
            await fetch('/upload', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ fileName: '열외일정.csv', content: content })
            });
        }

        if (holidayFile) {
            updateStatus(`전송 중: ${holidayFile.name}...`);
            const content = await readFileAsText(holidayFile);
            await fetch('/upload', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ fileName: '공휴일.csv', content: content })
            });
        }

        updateStatus("⚙️ 데이터 전송 완료. 근무 배정 연산을 시작합니다...");

        // 엔진 가동 요청 (Core Engine Execution)
        const response = await fetch('/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const result = await response.json();

        if (response.ok && result.status === "success") {
            updateStatus("✅ 배정 완료! 결과 파일을 다운로드합니다.");
        
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
        
            // 서버가 보내준 파일 다운로드
            if (result.files && result.files.result) {
                download(result.files.result, `근무공정표.csv`);
            }
        
            setTimeout(() => alert("🎉 근무표 생성이 완료되었습니다!"), 500);
        } else {
            throw new Error(result.message || "서버 연산 중 오류가 발생했습니다.");
        }

    } catch (err) {
        updateStatus(`❌ 런타임 에러 발생: ${err.message}`, true);
        alert("시스템 오류: " + err.message);
    }
}

// DOM이 모두 로드된 후 버튼에 이벤트 바인딩
document.addEventListener('DOMContentLoaded', () => {
    const runButton = document.getElementById('runButton');
    if(runButton) {
        runButton.addEventListener('click', runPipeline);
    }
});