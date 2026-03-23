document.addEventListener('DOMContentLoaded', function () {
    const emailInput = document.getElementById('email');
    const getOtpBtn = document.getElementById('otpBtn');
    const otpMessage = document.getElementById('otpMessage');

    const regForm = document.getElementById('regForm');
    if (regForm) {
        regForm.addEventListener('submit', function (e) {
            const fullname = regForm.querySelector('input[name="fullname"]').value.trim();
            const email = regForm.querySelector('input[name="email"]').value.trim();
            const otp = regForm.querySelector('input[name="otp"]').value.trim();
            const phone = regForm.querySelector('input[name="phone"]').value.trim();
            const password = regForm.querySelector('input[name="password"]').value.trim();
            const confirmPassword = regForm.querySelector('input[name="confirm_password"]').value.trim();

            if (!fullname) {
                e.preventDefault();
                window.QHToast && window.QHToast.error('Vui lòng nhập họ tên!');
                return;
            }
            if (!email) {
                e.preventDefault();
                window.QHToast && window.QHToast.error('Vui lòng nhập email!');
                return;
            }
            if (!otp) {
                e.preventDefault();
                window.QHToast && window.QHToast.error('Vui lòng nhập mã OTP!');
                return;
            }
            if (!phone) {
                e.preventDefault();
                window.QHToast && window.QHToast.error('Vui lòng nhập số điện thoại!');
                return;
            }
            if (!password) {
                e.preventDefault();
                window.QHToast && window.QHToast.error('Vui lòng nhập mật khẩu!');
                return;
            }
            if (!confirmPassword) {
                e.preventDefault();
                window.QHToast && window.QHToast.error('Vui lòng nhập lại mật khẩu!');
                return;
            }
        });
    }

    if (emailInput && getOtpBtn) {
        function isValidEmail(email) {
            return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
        }

        function updateOtpButtonState() {
            const email = emailInput.value.trim();
            if (isValidEmail(email)) {
                getOtpBtn.disabled = false;
                getOtpBtn.style.opacity = '1';
                getOtpBtn.style.cursor = 'pointer';
            } else {
                getOtpBtn.disabled = true;
                getOtpBtn.style.opacity = '0.5';
                getOtpBtn.style.cursor = 'not-allowed';
            }
        }

        updateOtpButtonState();

        emailInput.addEventListener('input', updateOtpButtonState);

        getOtpBtn.addEventListener('click', function () {
            const email = emailInput.value.trim();

            if (!isValidEmail(email)) {
                if (window.QHToast) {
                    window.QHToast.show('Vui lòng nhập email hợp lệ!', 'error');
                }
                return;
            }

            getOtpBtn.disabled = true;
            getOtpBtn.textContent = 'Đang gửi...';

            fetch('/send-otp/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': getCsrfToken()
                },
                body: 'email=' + encodeURIComponent(email)
            })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        if (QHToast) {
                            QHToast.show('Đã gửi mã OTP về email của bạn!', 'success');
                        }
                        if (otpMessage) {
                            otpMessage.style.display = 'none';
                        }
                        let countdown = 60;
                        const interval = setInterval(function () {
                            getOtpBtn.textContent = 'Gửi lại sau ' + countdown + 's';
                            countdown--;
                            if (countdown < 0) {
                                clearInterval(interval);
                                getOtpBtn.textContent = 'Lấy mã';
                                updateOtpButtonState();
                            }
                        }, 1000);
                    } else {
                        if (QHToast) {
                            QHToast.show(data.message || 'Gửi OTP thất bại!', 'error');
                        }
                        getOtpBtn.textContent = 'Lấy mã';
                        updateOtpButtonState();
                    }
                })
                .catch(error => {
                    if (QHToast) {
                        QHToast.show('Lỗi kết nối server!', 'error');
                    }
                    getOtpBtn.textContent = 'Lấy mã';
                    updateOtpButtonState();
                });
        });
    }
});

function getCsrfToken() {
    const name = 'csrftoken';
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
