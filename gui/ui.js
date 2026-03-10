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
    let activeDuties = ['위병부조장', '식기', '불침번', '초병 (선임/후임)', 'CCTV'];
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