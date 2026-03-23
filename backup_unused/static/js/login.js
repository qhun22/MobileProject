document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('loginForm');
    if (!form) return;

    form.addEventListener('submit', function (e) {
        const email = form.querySelector('input[name="username"]').value.trim();
        const password = form.querySelector('input[name="password"]').value.trim();

        if (!email && !password) {
            e.preventDefault();
            window.QHToast && window.QHToast.error('Vui lòng nhập email và mật khẩu!');
            return;
        }
        if (!email) {
            e.preventDefault();
            window.QHToast && window.QHToast.error('Vui lòng nhập email!');
            return;
        }
        if (!password) {
            e.preventDefault();
            window.QHToast && window.QHToast.error('Vui lòng nhập mật khẩu!');
            return;
        }
    });
});
