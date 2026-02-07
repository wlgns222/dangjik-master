/**
 * UI Controller
 * 역할: 전역 화면 전환 및 도움말 서브 라우팅 관리
 */

function moveStep(step) {
    const wizardForm = document.getElementById('wizardForm');
    const helpContainer = document.getElementById('helpContainer');

    // 모든 메인 콘텐츠 비활성화
    document.querySelectorAll('.step-content').forEach(el => el.classList.remove('active'));

    // 1. 도움말 모드(Context Switching)
    if (step === 'help') {
        wizardForm.style.display = 'none';
        helpContainer.style.display = 'block';
        moveHelp(0);
        return;
    }

    // 2. 운영 모드(Main Wizard)
    helpContainer.style.display = 'none';
    wizardForm.style.display = 'block';

    const target = document.getElementById('step-' + step);
    if (target) {
        target.classList.add('active');
        updateStepper(step);
    }
}

function moveHelp(hStep) {
    // 모든 도움말 콘텐츠 초기화 (중복 방지)
    document.querySelectorAll('.help-content').forEach(el => {
        el.classList.remove('active');
        el.style.display = 'none';
    });

    const targetHelp = document.getElementById('h-step-' + hStep);
    if (targetHelp) {
        targetHelp.classList.add('active');
        targetHelp.style.display = 'block';
    }
}

function exitHelp() {
    moveStep(0); // 초기 인트로 화면으로 복구
}

function updateStepper(step) {
    document.querySelectorAll('.step-dot').forEach((dot, idx) => {
        if (step > 0 && idx + 1 <= step) dot.classList.add('active');
        else dot.classList.remove('active');
    });
}