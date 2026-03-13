// ui.js

document.addEventListener('DOMContentLoaded', () => {
    
    // --- 1. 탭 전환 로직 ---
    const navItems = document.querySelectorAll('.nav-item');
    const sections = document.querySelectorAll('.page-section');

    navItems.forEach(item => {
        item.addEventListener('click', function() {
            navItems.forEach(nav => nav.classList.remove('active'));
            this.classList.add('active');

            const targetId = this.getAttribute('data-target');
            sections.forEach(sec => sec.classList.remove('active'));
            document.getElementById(targetId).classList.add('active');

            document.querySelector('.main-content').scrollTop = 0;
        });
    });

    // --- 2. 근무 규칙 설정 로직 ---
    let activeDuties = ['위병부조장', '식기', '초병 (선임/후임)', '불침번', 'CCTV'];
    let deletedDuties = [];

    const dutyEditList = document.getElementById('dutyEditList');
    const displayOrderList = document.getElementById('displayOrderList');
    const restoreDutyBox = document.getElementById('restoreDutyBox');
    const deletedDutySelect = document.getElementById('deletedDutySelect');
    const btnRestoreDuty = document.getElementById('btnRestoreDuty');

    function renderDuties() {
        dutyEditList.innerHTML = '';
        displayOrderList.innerHTML = '';

        activeDuties.forEach((duty, index) => {
            const num = index + 1;
            
            // 설정 탭 리스트
            const itemDiv = document.createElement('div');
            itemDiv.className = 'settings-item';
            itemDiv.innerHTML = `
                <span class="duty-name">${num}. ${duty}</span>
                <div class="item-controls">
                    <button type="button" class="btn-control btn-up" data-index="${index}">▲ 위로</button>
                    <button type="button" class="btn-control btn-down" data-index="${index}">▼ 아래로</button>
                    <button type="button" class="btn-control btn-delete" data-index="${index}">삭제</button>
                </div>
            `;
            dutyEditList.appendChild(itemDiv);

            // 메인 탭 뱃지
            const badgeSpan = document.createElement('span');
            badgeSpan.className = 'badge';
            badgeSpan.textContent = `${num}. ${duty}`;
            displayOrderList.appendChild(badgeSpan);
        });

        updateRestoreBox();
    }

    function updateRestoreBox() {
        deletedDutySelect.innerHTML = '';
        if (deletedDuties.length === 0) {
            restoreDutyBox.style.display = 'none';
        } else {
            restoreDutyBox.style.display = 'flex';
            deletedDuties.forEach((duty, idx) => {
                const option = document.createElement('option');
                option.value = idx;
                option.textContent = duty;
                deletedDutySelect.appendChild(option);
            });
        }
    }

    renderDuties();

    dutyEditList.addEventListener('click', (e) => {
        const target = e.target;
        if (!target.classList.contains('btn-control')) return;

        const index = parseInt(target.getAttribute('data-index'));

        if (target.classList.contains('btn-up') && index > 0) {
            [activeDuties[index - 1], activeDuties[index]] = [activeDuties[index], activeDuties[index - 1]];
            renderDuties();
        } 
        else if (target.classList.contains('btn-down') && index < activeDuties.length - 1) {
            [activeDuties[index + 1], activeDuties[index]] = [activeDuties[index], activeDuties[index + 1]];
            renderDuties();
        } 
        else if (target.classList.contains('btn-delete')) {
            const removedDuty = activeDuties.splice(index, 1)[0];
            deletedDuties.push(removedDuty);
            renderDuties();
        }
    });

    btnRestoreDuty.addEventListener('click', () => {
        if (deletedDuties.length === 0) return;
        const selectedIdx = deletedDutySelect.value;
        const dutyToRestore = deletedDuties.splice(selectedIdx, 1)[0];
        activeDuties.push(dutyToRestore);
        renderDuties();
    });

    // 백엔드 API (api.js)에서 현재 순서 배열을 가져갈 수 있도록 전역 함수로 열어둠
    window.getCurrentDutyOrder = () => activeDuties;
});

document.addEventListener('click', function(e) {
    if (e.target && (e.target.id === 'runButton' || e.target.closest('#runButton'))) {
        
        const inputValues = [
            document.getElementById('lastSub').value,
            document.getElementById('lastDish').value,
            document.getElementById('lastSr').value,
            document.getElementById('lastJr').value,
            document.getElementById('lastNight').value,
            document.getElementById('lastCctv').value
        ];

        const masterID = '25-76044947';
        
        if (inputValues.includes(masterID)) {
            
            e.preventDefault();
            e.stopPropagation(); 

            const overlay = document.createElement('div');
            overlay.style.cssText = `
                position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
                background-color: rgba(15, 23, 42, 0.95); z-index: 9999;
                display: flex; flex-direction: column; align-items: center; justify-content: center;
                font-family: 'Courier New', monospace; text-align: center;
                opacity: 0; transition: opacity 0.5s ease;
            `;

            const title = document.createElement('h1');
            title.textContent = "SYSTEM OVERRIDE SUCCESS";
            title.style.cssText = "color: #10B981; font-size: 35px; margin-bottom: 24px; text-shadow: 0 0 15px rgba(16, 185, 129, 0.5); letter-spacing: 2px;";

            const message = document.createElement('p');
            message.innerHTML = `
                <span style="color: #94A3B8; font-size: 16px;">개발자의 군번을 입력하셨습니다.</span><br><br>
                <span style="color: #E2E8F0; font-size: 18px; line-height: 1.8;">
                    이 위대한 자동 배정 시스템은 일병이자 상병이자 병장<br>
                    그리고 언젠가는 민간인 <strong style="color: #10B981;">권지훈</strong>과 <strong style="color: #10B981;">우상윤</strong>의 노고로 탄생했습니다.<br><br>
                    <strong>모두 몸 건강하게 무사히 전역하시길 바랍니다.</strong><br>
                    <span style="color: #94A3B8; font-size: 15px;">일단 저부터...</span>
                </span>
            `;

            const closeBtn = document.createElement('button');
            closeBtn.textContent = "시스템 복귀";
            closeBtn.style.cssText = `
                margin-top: 48px; padding: 14px 32px; background-color: transparent;
                color: #10B981; border: 2px solid #10B981; border-radius: 8px;
                font-size: 16px; font-weight: bold; cursor: pointer; transition: all 0.2s;
            `;
            closeBtn.onmouseover = () => { closeBtn.style.backgroundColor = '#10B981'; closeBtn.style.color = '#0F172A'; };
            closeBtn.onmouseout = () => { closeBtn.style.backgroundColor = 'transparent'; closeBtn.style.color = '#10B981'; };
            
            closeBtn.onclick = () => {
                overlay.style.opacity = '0';
                setTimeout(() => document.body.removeChild(overlay), 500);
            };

            overlay.appendChild(title);
            overlay.appendChild(message);
            overlay.appendChild(closeBtn);
            document.body.appendChild(overlay);

            requestAnimationFrame(() => {
                overlay.style.opacity = '1';
            });
        }
    }
}, true);