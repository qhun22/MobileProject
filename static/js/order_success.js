/* ========================================================
   QHUN22 – Order Success Page JavaScript
   ======================================================== */

/* ========== Xử lý khi đã sao chép ========== */
/**
 * Xử lý sau khi sao chép mã đơn hàng
 * @param {HTMLElement} btn - Nút bấm
 */
function doCopied(btn) {
    var ic = btn.querySelector('i');
    var origText = btn.innerHTML;
    if (ic) ic.className = 'ri-check-line';
    btn.childNodes[btn.childNodes.length - 1].textContent = ' Đã sao chép!';
    btn.style.borderColor = '#b91c1c';
    btn.style.background = '#ffffff';
    btn.style.color = '#b91c1c';
    if (window.QHToast) QHToast.show('Đã sao chép mã đơn hàng!', 'success');
    setTimeout(function() {
        btn.innerHTML = origText;
        btn.style.borderColor = '';
        btn.style.background = '';
        btn.style.color = '';
    }, 2000);
}

/* ========== Hiệu ứng confetti ========== */
/**
 * Tạo hiệu ứng confetti khi trang tải xong
 */
function initConfetti() {
    var c = document.getElementById('successCard');
    if (!c) return;

    var cls = ['#b91c1c', '#991b1b', '#ef4444', '#fecaca', '#fee2e2', '#fca5a5'];

    function spawnOne() {
        var d = document.createElement('div');
        d.className = 'qh-confetti';
        d.style.left = (Math.random() * 100) + '%';
        d.style.top = '-12px';
        d.style.background = cls[Math.floor(Math.random() * cls.length)];
        d.style.animationDelay = '0s';
        d.style.animationDuration = (1.6 + Math.random() * 1.2) + 's';
        d.style.width = (5 + Math.random() * 6) + 'px';
        d.style.height = (5 + Math.random() * 6) + 'px';
        c.appendChild(d);
        setTimeout(function() { d.remove(); }, 3500);
    }

    // Burst ban đầu
    for (var i = 0; i < 20; i++) {
        setTimeout(spawnOne, i * 45);
    }

    // Rơi liên tục
    setInterval(function() {
        spawnOne();
        if (Math.random() > 0.55) spawnOne();
    }, 220);
}

// Khởi tạo confetti khi DOM đã sẵn sàng
document.addEventListener('DOMContentLoaded', function() {
    initConfetti();
});
