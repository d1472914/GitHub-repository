/**
 * 宿舍共好 — 室友公約與噪音管理系統
 * 全站 JavaScript (main.js)
 */

document.addEventListener('DOMContentLoaded', () => {
    console.log('宿舍共好系統載入成功！');
    
    // 自動淡出警告訊息 (Alert & Flash)
    const alerts = document.querySelectorAll('.alert, .flash-message');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s ease';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });
});
