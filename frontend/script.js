document.addEventListener('DOMContentLoaded', () => {
    // 1. Initialize Icons
    lucide.createIcons();

    // 2. Sticky Navbar Glassmorphism
    const navbar = document.getElementById('navbar');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });

    // 3. Mobile Menu Toggle
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const closeMenuBtn = document.getElementById('closeMenuBtn');
    const mobileMenu = document.getElementById('mobileMenu');
    const mobileLinks = document.querySelectorAll('.mobile-nav-links a');

    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', () => mobileMenu.classList.add('active'));
    }
    if (closeMenuBtn) {
        closeMenuBtn.addEventListener('click', () => mobileMenu.classList.remove('active'));
    }
    mobileLinks.forEach(link => {
        link.addEventListener('click', () => mobileMenu.classList.remove('active'));
    });

    // 4. Scroll Animations (Fade Up Staggered)
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, observerOptions);

    document.querySelectorAll('.fade-up').forEach(el => observer.observe(el));

    // 5. Stat Counter Animation
    const statElements = document.querySelectorAll('.stat-value');
    let counted = false;

    const startCounting = () => {
        statElements.forEach(el => {
            const target = parseFloat(el.getAttribute('data-target'));
            const duration = 2000; // ms
            const stepTime = 20;
            const steps = duration / stepTime;
            const increment = target / steps;
            let current = 0;
            const prefix = el.classList.contains('prefix') ? '$' : '';
            const suffix = el.getAttribute('data-suffix') || '';

            const timer = setInterval(() => {
                current += increment;
                if (current >= target) {
                    current = target;
                    clearInterval(timer);
                    // Format appropriately (number or whole)
                    let displayVal = target % 1 === 0 ? target.toLocaleString() : target.toFixed(1);
                    el.textContent = `${prefix}${displayVal}${suffix}`;
                } else {
                    let displayVal = target % 1 === 0 ? Math.floor(current).toLocaleString() : current.toFixed(1);
                    el.textContent = `${prefix}${displayVal}${suffix}`;
                }
            }, stepTime);
        });
    };

    // Only count when stats bar comes into view
    const statsObserver = new IntersectionObserver((entries) => {
        if (entries[0].isIntersecting && !counted) {
            startCounting();
            counted = true;
        }
    });

    const statsBar = document.querySelector('.stats-bar');
    if (statsBar) statsObserver.observe(statsBar);

    // 6. How It Works Logic (Scroll based connecting line)
    const steps = document.querySelectorAll('.step');
    const flowProgress = document.getElementById('flowProgress');

    if (steps.length > 0 && flowProgress) {
        window.addEventListener('scroll', () => {
            // Find which step is currently active roughly based on scroll
            // For a simpler effect without pinning, we can just highlight on hover or interval
            // Here we implement an auto-playing sequence for the visual effect
        });

        let currentStep = 1;
        setInterval(() => {
            steps.forEach(s => s.classList.remove('step-active'));
            // position progress dot
            const positions = ['0%', '25%', '50%', '75%', '100%'];
            flowProgress.style.left = positions[currentStep - 1];

            document.querySelector(`.step[data-step="${currentStep}"]`).classList.add('step-active');

            currentStep = currentStep >= 5 ? 1 : currentStep + 1;
        }, 3000);
    }

    // 7. Mockup Tab Switcher
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Remove active from all
            tabBtns.forEach(b => b.classList.remove('active'));
            tabPanes.forEach(p => p.classList.remove('active'));

            // Add active to clicked
            btn.classList.add('active');
            const targetId = btn.getAttribute('data-target');
            document.getElementById(targetId).classList.add('active');
        });
    });
});
