const hero = document.querySelector('[data-hero]');

const updatePosition = (x, y) => {
    const xPercent = Math.round((x / window.innerWidth) * 100);
    const yPercent = Math.round((y / window.innerHeight) * 100);

    gsap.to(hero, {
        '--x': `${xPercent}%`,
        '--y': `${yPercent}%`,
        duration: 0.3,
        ease: 'sine.out',
    });
}

window.addEventListener('mousemove', (e) => {
    e.preventDefault();
    const { clientX, clientY } = e;
    updatePosition(clientX, clientY);
});

window.addEventListener('touchmove', (e) => {
    e.preventDefault();
    if (e.touches.length > 0) {
        const { clientX, clientY } = e.touches[0];
        updatePosition(clientX, clientY);
    }
});

const buttons = document.querySelectorAll('.btn');
const overlay = document.createElement('div');
overlay.className = 'transition-overlay';
document.body.appendChild(overlay);

buttons.forEach(button => {
    button.addEventListener('click', (e) => {
        if (button.href) {
            e.preventDefault();
            const { clientX, clientY } = e;
            overlay.style.left = `${clientX}px`;
            overlay.style.top = `${clientY}px`;
            overlay.classList.add('expand');

            setTimeout(() => {
                window.location.href = button.href;
            }, 1000); // 전환 시간과 일치하도록 설정

            /* 
            ---------------------------------------
            just to reset without having to refresh..
            --------------------------------*/
            setTimeout(() => { overlay.classList.remove('expand'); }, 1500);
        }
    });
});