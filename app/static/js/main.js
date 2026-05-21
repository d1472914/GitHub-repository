// 宿舍共好 — 室友公約與噪音管理系統 全站 JS

document.addEventListener('DOMContentLoaded', () => {
    console.log('宿舍共好系統載入完成。');
    
    // 自動消失 Flash 訊息
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(msg => {
        setTimeout(() => {
            msg.style.opacity = '0';
            msg.style.transition = 'opacity 0.5s ease';
            setTimeout(() => msg.remove(), 500);
        }, 5000);
    });
});
