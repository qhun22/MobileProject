const AUTH_VISUAL = {
    login: {
        icon: 'ri-store-2-line',
        title: 'ĐĂNG NHẬP!',
        desc: 'Đăng nhập để trải nghiệm mua sắm thông minh.',
        features: [
            { icon: 'ri-truck-line', text: 'Giao hàng toàn quốc nhanh chóng' },
            { icon: 'ri-shield-check-line', text: 'Bảo hành chính hãng 100%' },
            { icon: 'ri-exchange-line', text: 'Đổi trả dễ dàng trong 30 ngày' },
        ],
    },
    register: {
        icon: 'ri-user-add-line',
        title: 'TẠO TÀI KHOẢN!',
        desc: 'Tạo tài khoản để khám phá sản phẩm công nghệ.',
        features: [
            { icon: 'ri-vip-crown-line', text: 'Ưu đãi độc quyền thành viên' },
            { icon: 'ri-map-pin-line', text: 'Theo dõi đơn hàng thời gian thực' },
            { icon: 'ri-history-line', text: 'Lịch sử & tái đặt hàng dễ dàng' },
        ],
    },
    forgot: {
        icon: 'ri-lock-password-line',
        title: 'Khôi phục tài khoản',
        desc: 'Chỉ vài bước đơn giản để lấy lại mật khẩu của bạn.',
        features: [
            { icon: 'ri-mail-send-line', text: 'Xác thực OTP bảo mật qua email' },
            { icon: 'ri-timer-line', text: 'Mã có hiệu lực 5 phút' },
            { icon: 'ri-lock-line', text: 'Đặt mật khẩu mới an toàn' },
        ],
    },
};

function renderVisual(mode) {
    const v = AUTH_VISUAL[mode] || AUTH_VISUAL.login;
    const body = document.getElementById('authVisualBody');
    if (!body) return;
    const featureHtml = v.features.map(f =>
        `<li><i class="${f.icon}"></i> ${f.text}</li>`
    ).join('');
    body.innerHTML = `
        <i class="auth-visual-icon ${v.icon}"></i>
        <h3 class="auth-visual-title">${v.title}</h3>
        <p class="auth-visual-desc">${v.desc}</p>
        <ul class="auth-feature-list">${featureHtml}</ul>
    `;
}

let currentMode = 'login';
let isSwitching = false;

function switchAuthMode(mode, direction) {
    if (mode === currentMode || isSwitching) return;
    isSwitching = true;

    const fromPanel = document.getElementById(currentMode + 'Panel');
    const toPanel = document.getElementById(mode + 'Panel');
    if (!fromPanel || !toPanel) { isSwitching = false; return; }

    const order = ['login', 'register', 'forgot'];
    const fromIdx = order.indexOf(currentMode);
    const toIdx = order.indexOf(mode);
    const goForward = direction ? direction === 'forward' : toIdx >= fromIdx;

    fromPanel.style.transition = 'opacity 0.26s ease, transform 0.26s ease';
    fromPanel.style.opacity = '0';
    fromPanel.style.transform = goForward ? 'translateX(-28px)' : 'translateX(28px)';

    setTimeout(() => {
        fromPanel.style.display = 'none';
        fromPanel.style.transition = '';
        fromPanel.style.opacity = '';
        fromPanel.style.transform = '';
        fromPanel.classList.remove('active', 'slide-from-right');

        toPanel.style.opacity = '0';
        toPanel.style.transform = goForward ? 'translateX(28px)' : 'translateX(-28px)';
        toPanel.style.display = 'block';
        toPanel.offsetHeight;

        toPanel.style.transition = 'opacity 0.34s ease, transform 0.34s ease';
        toPanel.style.opacity = '1';
        toPanel.style.transform = 'translateX(0)';
        toPanel.classList.add('active');

        setTimeout(() => {
            toPanel.style.transition = '';
            isSwitching = false;
        }, 350);
    }, 270);

    const vb = document.getElementById('authVisualBody');
    if (vb) {
        vb.style.transition = 'opacity 0.2s ease, transform 0.2s ease';
        vb.style.opacity = '0';
        vb.style.transform = 'translateY(14px)';
        setTimeout(() => {
            renderVisual(mode);
            vb.style.opacity = '1';
            vb.style.transform = 'translateY(0)';
        }, 220);
    }

    currentMode = mode;
}

function togglePw(inputId, btn) {
    const input = document.getElementById(inputId);
    if (!input) return;
    if (input.type === 'password') {
        input.type = 'text';
        if (btn) btn.innerHTML = '<i class="ri-eye-off-line"></i>';
    } else {
        input.type = 'password';
        if (btn) btn.innerHTML = '<i class="ri-eye-line"></i>';
    }
}

function getCsrf() {
    const cookies = document.cookie.split(';');
    for (let c of cookies) {
        c = c.trim();
        if (c.startsWith('csrftoken=')) {
            return decodeURIComponent(c.substring('csrftoken='.length));
        }
    }
    return '';
}

function isValidEmail(e) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(e);
}

function initLogin() {
    const form = document.getElementById('loginForm');
    if (!form) return;
    form.addEventListener('submit', function (e) {
        const email = (document.getElementById('loginEmail') || {}).value || '';
        const password = (document.getElementById('loginPassword') || {}).value || '';
        if (!email.trim() && !password.trim()) {
            e.preventDefault();
            window.QHToast && window.QHToast.error('Vui lòng nhập email và mật khẩu!');
            return;
        }
        if (!email.trim()) {
            e.preventDefault();
            window.QHToast && window.QHToast.error('Vui lòng nhập email!');
            return;
        }
        if (!password.trim()) {
            e.preventDefault();
            window.QHToast && window.QHToast.error('Vui lòng nhập mật khẩu!');
        }
    });
}

function initRegister() {
    const emailInput = document.getElementById('regEmail');
    const otpBtn = document.getElementById('regOtpBtn');
    const regForm = document.getElementById('regForm');

    function updateOtpBtn() {
        if (!otpBtn || !emailInput) return;
        const ok = isValidEmail(emailInput.value.trim());
        otpBtn.disabled = !ok;
        otpBtn.style.opacity = ok ? '1' : '';
    }

    if (emailInput) {
        emailInput.addEventListener('input', updateOtpBtn);
        updateOtpBtn();
    }

    if (otpBtn) {
        otpBtn.addEventListener('click', function () {
            const email = emailInput.value.trim();
            if (!isValidEmail(email)) {
                window.QHToast && window.QHToast.error('Email không hợp lệ!');
                return;
            }
            otpBtn.disabled = true;
            otpBtn.textContent = 'Đang gửi...';

            fetch('/send-otp/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'X-CSRFToken': getCsrf() },
                body: 'email=' + encodeURIComponent(email),
            })
                .then(r => r.json())
                .then(data => {
                    if (data.status === 'success') {
                        window.QHToast && window.QHToast.success('Đã gửi mã OTP về email của bạn!');
                        let cd = 60;
                        const iv = setInterval(() => {
                            otpBtn.textContent = 'Gửi lại sau ' + cd + 's';
                            cd--;
                            if (cd < 0) {
                                clearInterval(iv);
                                otpBtn.textContent = 'Lấy mã';
                                updateOtpBtn();
                            }
                        }, 1000);
                    } else {
                        window.QHToast && window.QHToast.error(data.message || 'Gửi OTP thất bại!');
                        otpBtn.textContent = 'Lấy mã';
                        updateOtpBtn();
                    }
                })
                .catch(() => {
                    window.QHToast && window.QHToast.error('Lỗi kết nối server!');
                    otpBtn.textContent = 'Lấy mã';
                    updateOtpBtn();
                });
        });
    }

    if (regForm) {
        regForm.addEventListener('submit', function (e) {
            const get = n => (regForm.querySelector(`input[name="${n}"]`) || {}).value || '';
            if (!get('fullname').trim()) { e.preventDefault(); window.QHToast && window.QHToast.error('Vui lòng nhập họ tên!'); return; }
            if (!get('email').trim()) { e.preventDefault(); window.QHToast && window.QHToast.error('Vui lòng nhập email!'); return; }
            if (!get('otp').trim()) { e.preventDefault(); window.QHToast && window.QHToast.error('Vui lòng nhập mã OTP!'); return; }
            if (!get('phone').trim()) { e.preventDefault(); window.QHToast && window.QHToast.error('Vui lòng nhập số điện thoại!'); return; }
            if (!get('password').trim()) { e.preventDefault(); window.QHToast && window.QHToast.error('Vui lòng nhập mật khẩu!'); return; }
            if (!get('confirm_password').trim()) { e.preventDefault(); window.QHToast && window.QHToast.error('Vui lòng nhập lại mật khẩu!'); return; }
        });
    }
}

const FP_URL = {
    sendOtp: '/send-otp-forgot-password/',
    verifyOtp: '/verify-otp-forgot-password/',
    reset: '/reset-password/',
};
let fpTimerInterval;

function initForgot() {
    const emailInput = document.getElementById('fpEmail');
    const otpBtn = document.getElementById('fpOtpBtn');
    const verifyBtn = document.getElementById('fpVerifyBtn');
    const resetBtn = document.getElementById('fpResetBtn');
    const resendBtn = document.getElementById('fpResendBtn');

    if (emailInput && otpBtn) {
        emailInput.addEventListener('input', function () {
            otpBtn.disabled = !isValidEmail(this.value.trim());
        });
    }

    if (otpBtn) {
        otpBtn.addEventListener('click', function () {
            const email = emailInput.value.trim();
            if (!isValidEmail(email)) {
                window.QHToast && window.QHToast.error('Email không hợp lệ!');
                return;
            }
            otpBtn.disabled = true;
            otpBtn.textContent = 'Đang gửi...';

            fetch(FP_URL.sendOtp, {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'X-CSRFToken': getCsrf() },
                body: 'email=' + encodeURIComponent(email),
            })
                .then(r => r.json())
                .then(data => {
                    if (data.status === 'success') {
                        window.QHToast && window.QHToast.success('Đã gửi OTP về email của bạn!');
                        goFpStep(2, email);
                    } else {
                        window.QHToast && window.QHToast.error(data.message || 'Gửi OTP thất bại!');
                        otpBtn.disabled = false;
                        otpBtn.textContent = 'Gửi mã';
                    }
                })
                .catch(() => {
                    window.QHToast && window.QHToast.error('Lỗi kết nối!');
                    otpBtn.disabled = false;
                    otpBtn.textContent = 'Gửi mã';
                });
        });
    }

    if (verifyBtn) {
        verifyBtn.addEventListener('click', function () {
            const email = (document.getElementById('fpEmail') || {}).value || '';
            const otp = ((document.getElementById('fpOtp') || {}).value || '').trim();
            if (!otp) { window.QHToast && window.QHToast.error('Vui lòng nhập mã OTP!'); return; }

            fetch(FP_URL.verifyOtp, {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'X-CSRFToken': getCsrf() },
                body: 'email=' + encodeURIComponent(email) + '&otp=' + encodeURIComponent(otp),
            })
                .then(r => r.json())
                .then(data => {
                    if (data.status === 'success') {
                        goFpStep(3, email);
                    } else {
                        window.QHToast && window.QHToast.error(data.message || 'OTP không đúng!');
                    }
                })
                .catch(() => window.QHToast && window.QHToast.error('Lỗi kết nối!'));
        });
    }

    if (resetBtn) {
        resetBtn.addEventListener('click', function () {
            const email = (document.getElementById('fpEmail') || {}).value || '';
            const pw1 = (document.getElementById('fpNewPw') || {}).value || '';
            const pw2 = (document.getElementById('fpConfirmPw') || {}).value || '';
            if (!pw1) { window.QHToast && window.QHToast.error('Vui lòng nhập mật khẩu mới!'); return; }
            if (!pw2) { window.QHToast && window.QHToast.error('Vui lòng nhập lại mật khẩu mới!'); return; }
            if (pw1.length < 6) { window.QHToast && window.QHToast.error('Mật khẩu phải có ít nhất 6 ký tự!'); return; }
            if (pw1 !== pw2) { window.QHToast && window.QHToast.error('Mật khẩu không khớp!'); return; }

            fetch(FP_URL.reset, {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'X-CSRFToken': getCsrf() },
                body: 'email=' + encodeURIComponent(email) + '&new_password=' + encodeURIComponent(pw1),
            })
                .then(r => r.json())
                .then(data => {
                    if (data.status === 'success') {
                        window.QHToast && window.QHToast.success('Đổi mật khẩu thành công!');
                        setTimeout(() => switchAuthMode('login', 'back'), 1800);
                    } else {
                        window.QHToast && window.QHToast.error(data.message || 'Thất bại!');
                    }
                })
                .catch(() => window.QHToast && window.QHToast.error('Lỗi kết nối!'));
        });
    }

    if (resendBtn) {
        resendBtn.addEventListener('click', function () {
            const email = (document.getElementById('fpEmail') || {}).value || '';
            resendBtn.disabled = true;
            resendBtn.textContent = 'Đang gửi...';

            fetch(FP_URL.sendOtp, {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'X-CSRFToken': getCsrf() },
                body: 'email=' + encodeURIComponent(email),
            })
                .then(r => r.json())
                .then(data => {
                    if (data.status === 'success') {
                        window.QHToast && window.QHToast.success('Đã gửi lại OTP!');
                        resendBtn.textContent = 'Gửi lại mã OTP';
                        startFpTimer();
                    } else {
                        window.QHToast && window.QHToast.error(data.message || 'Gửi lại thất bại!');
                        resendBtn.disabled = false;
                        resendBtn.textContent = 'Gửi lại mã OTP';
                    }
                })
                .catch(() => {
                    window.QHToast && window.QHToast.error('Lỗi kết nối!');
                    resendBtn.disabled = false;
                    resendBtn.textContent = 'Gửi lại mã OTP';
                });
        });
    }
}

function goFpStep(step, email) {
    const forms = { 1: 'fForm1', 2: 'fForm2', 3: 'fForm3' };
    const stepEls = { 1: 'fStep1', 2: 'fStep2', 3: 'fStep3' };
    const connEls = { 1: 'fConn1', 2: 'fConn2' };

    for (let i = 1; i <= 3; i++) {
        const el = document.getElementById(forms[i]);
        if (el) el.style.display = (i === step) ? 'block' : 'none';
    }
    for (let i = 1; i <= 3; i++) {
        const s = document.getElementById(stepEls[i]);
        if (!s) continue;
        s.classList.remove('active', 'done');
        if (i < step) s.classList.add('done');
        else if (i === step) s.classList.add('active');
    }
    const c1 = document.getElementById(connEls[1]);
    const c2 = document.getElementById(connEls[2]);
    if (c1) c1.classList.toggle('done', step > 1);
    if (c2) c2.classList.toggle('done', step > 2);

    if (step === 2) {
        const info = document.getElementById('fpOtpInfo');
        if (info) { info.textContent = 'Mã OTP đã gửi đến: ' + email; info.classList.add('show'); }
        startFpTimer();
    }
    if (step !== 2 && fpTimerInterval) {
        clearInterval(fpTimerInterval);
    }
}

function startFpTimer() {
    const resendBtn = document.getElementById('fpResendBtn');
    const countEl = document.getElementById('fpCountdown');
    if (resendBtn) resendBtn.disabled = true;
    if (fpTimerInterval) clearInterval(fpTimerInterval);
    let t = 300;
    fpTimerInterval = setInterval(() => {
        const m = Math.floor(t / 60);
        const s = t % 60;
        if (countEl) countEl.textContent = m + ':' + (s < 10 ? '0' : '') + s;
        if (t <= 0) {
            clearInterval(fpTimerInterval);
            if (countEl) countEl.textContent = '0:00';
            if (resendBtn) resendBtn.disabled = false;
        }
        t--;
    }, 1000);
}

document.addEventListener('DOMContentLoaded', function () {
    const container = document.getElementById('authContainer');
    const initialMode = (container && container.dataset.initialMode) || 'login';

    const activePanel = document.getElementById(initialMode + 'Panel');
    if (activePanel) {
        activePanel.style.display = 'block';
        activePanel.style.opacity = '1';
        activePanel.classList.add('active');
    }
    currentMode = initialMode;

    renderVisual(initialMode);
    const vb = document.getElementById('authVisualBody');
    if (vb) { vb.style.opacity = '1'; vb.style.transform = 'translateY(0)'; }

    initLogin();
    initRegister();
    initForgot();
});
