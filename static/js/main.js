/* ================================================================
   PARADISE BARBER SHOP — Interactions & Animations
   ================================================================ */

document.addEventListener('DOMContentLoaded', () => {

    // ────────────────────────────────────────────────────────────
    // 1. REVEAL ANIMATIONS (with stagger support)
    // ────────────────────────────────────────────────────────────
    const revealSelectors = '.reveal, .reveal-left, .reveal-right, .reveal-scale';
    const revealItems = document.querySelectorAll(revealSelectors);

    if ('IntersectionObserver' in window) {
        const revealObserver = new IntersectionObserver((entries, obs) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    const delay = parseInt(entry.target.dataset.delay || 0, 10);
                    setTimeout(() => {
                        entry.target.classList.add('is-visible');
                    }, delay);
                    obs.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.12,
            rootMargin: '0px 0px -8% 0px',
        });

        revealItems.forEach((item) => revealObserver.observe(item));
    } else {
        // Fallback: show everything immediately
        revealItems.forEach((item) => item.classList.add('is-visible'));
    }

    // ────────────────────────────────────────────────────────────
    // 2. HEADER — Solid on scroll
    // ────────────────────────────────────────────────────────────
    const header = document.getElementById('site-header');
    if (header) {
        const onScroll = () => {
            header.classList.toggle('header-scrolled', window.scrollY > 60);
        };
        window.addEventListener('scroll', onScroll, { passive: true });
        onScroll(); // initial check
    }

    // ────────────────────────────────────────────────────────────
    // 3. MOBILE NAV — Hamburger toggle
    // ────────────────────────────────────────────────────────────
    const navToggle = document.getElementById('nav-toggle');
    const mobileNav = document.getElementById('mobile-nav');

    if (navToggle && mobileNav) {
        navToggle.addEventListener('click', () => {
            const isOpen = navToggle.classList.toggle('is-open');
            mobileNav.classList.toggle('is-open', isOpen);
            navToggle.setAttribute('aria-expanded', isOpen);
            document.body.style.overflow = isOpen ? 'hidden' : '';
        });

        // Close mobile nav when a link is clicked
        mobileNav.querySelectorAll('a').forEach((link) => {
            link.addEventListener('click', () => {
                navToggle.classList.remove('is-open');
                mobileNav.classList.remove('is-open');
                navToggle.setAttribute('aria-expanded', 'false');
                document.body.style.overflow = '';
            });
        });
    }

    // ────────────────────────────────────────────────────────────
    // 4. ACTIVE NAV LINK — Scroll spy
    // ────────────────────────────────────────────────────────────
    const navLinks = document.querySelectorAll('.nav-links a');
    const sections = [];

    navLinks.forEach((link) => {
        const href = link.getAttribute('href') || '';
        const hashIndex = href.indexOf('#');
        if (hashIndex !== -1) {
            const id = href.slice(hashIndex + 1);
            if (id && id !== 'top') {
                const section = document.getElementById(id);
                if (section) sections.push({ el: section, link });
            }
        }
    });

    if (sections.length > 0 && 'IntersectionObserver' in window) {
        const spyObserver = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    navLinks.forEach((l) => l.classList.remove('active'));
                    const match = sections.find((s) => s.el === entry.target);
                    if (match) match.link.classList.add('active');
                }
            });
        }, {
            threshold: 0,
            rootMargin: '-20% 0px -60% 0px',
        });

        sections.forEach((s) => spyObserver.observe(s.el));
    }

    // ────────────────────────────────────────────────────────────
    // 5. ANIMATED COUNTERS — Stats section
    // ────────────────────────────────────────────────────────────
    const counters = document.querySelectorAll('[data-count]');

    if (counters.length > 0 && 'IntersectionObserver' in window) {
        const counterObserver = new IntersectionObserver((entries, obs) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    animateCounter(entry.target);
                    obs.unobserve(entry.target);
                }
            });
        }, { threshold: 0.5 });

        counters.forEach((el) => counterObserver.observe(el));
    }

    function animateCounter(el) {
        const target = parseFloat(el.dataset.count);
        if (isNaN(target)) return;

        const decimals = parseInt(el.dataset.decimals || 0, 10);
        const duration = 1800;
        const startTime = performance.now();

        function update(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);

            // Ease-out cubic
            const eased = 1 - Math.pow(1 - progress, 3);
            const current = eased * target;

            if (decimals > 0) {
                el.textContent = current.toFixed(decimals);
            } else {
                el.textContent = Math.floor(current) + '+';
            }

            if (progress < 1) {
                requestAnimationFrame(update);
            } else {
                // Final value
                if (decimals > 0) {
                    el.textContent = target.toFixed(decimals);
                } else {
                    el.textContent = target + '+';
                }
            }
        }

        requestAnimationFrame(update);
    }

    // ────────────────────────────────────────────────────────────
    // 6. SMOOTH SCROLL — For anchor links
    // ────────────────────────────────────────────────────────────
    document.querySelectorAll('a[href*="#"]').forEach((anchor) => {
        anchor.addEventListener('click', (e) => {
            const href = anchor.getAttribute('href') || '';
            const hashIndex = href.indexOf('#');
            if (hashIndex === -1) return;

            const targetPath = href.slice(0, hashIndex);
            const targetId = href.slice(hashIndex);

            // Only smooth scroll if on current page
            if (targetPath && targetPath !== window.location.pathname && targetPath !== '/') return;
            if (targetId === '#' || targetId === '#top') {
                if (targetId === '#top') {
                    e.preventDefault();
                    window.scrollTo({ top: 0, behavior: 'smooth' });
                }
                return;
            }

            try {
                const targetEl = document.querySelector(targetId);
                if (targetEl) {
                    e.preventDefault();
                    const headerHeight = header ? header.offsetHeight : 0;
                    const top = targetEl.getBoundingClientRect().top + window.scrollY - headerHeight - 16;

                    window.scrollTo({
                        top,
                        behavior: 'smooth',
                    });
                }
            } catch (err) {
                // Ignore invalid CSS selector
            }
        });
    });

});