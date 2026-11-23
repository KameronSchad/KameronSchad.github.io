/* Shared site behavior. All content works without JavaScript. */
(() => {
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    /* Reveal cards as they enter the viewport. */
    if (!reduceMotion && 'IntersectionObserver' in window) {
        document.documentElement.classList.add('js');
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('in-view');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.05, rootMargin: '0px 0px 35px 0px' });
        document.querySelectorAll('.reveal').forEach(el => observer.observe(el));
    }

    /* Accessible, automatically advancing carousel on the homepage. */
    const carousel = document.querySelector('[data-carousel]');
    if (carousel) {
        const slides = [...carousel.querySelectorAll('[data-feature-slide]')];
        const dotsContainer = document.querySelector('[data-carousel-dots]');
        const prev = document.querySelector('[data-carousel-prev]');
        const next = document.querySelector('[data-carousel-next]');
        let current = 0;
        let interval;

        if (slides.length > 0 && dotsContainer && prev && next) {
            slides.forEach((slide, index) => {
                const dot = document.createElement('button');
                dot.type = 'button';
                dot.setAttribute('aria-label', `Show project ${index + 1}`);
                dot.addEventListener('click', () => { show(index); start(); });
                dotsContainer.appendChild(dot);
            });
            const dots = [...dotsContainer.querySelectorAll('button')];

            function show(index) {
                current = (index + slides.length) % slides.length;
                slides.forEach((slide, i) => {
                    const active = i === current;
                    slide.classList.toggle('is-active', active);
                    slide.hidden = !active;
                    slide.setAttribute('aria-hidden', String(!active));
                });
                dots.forEach((dot, i) => dot.setAttribute('aria-current', String(i === current)));
            }
            function stop() {
                if (interval) clearInterval(interval);
                interval = undefined;
            }
            function start() {
                stop();
                if (!reduceMotion && !document.hidden) {
                    interval = window.setInterval(() => show(current + 1), 8000);
                }
            }
            prev.addEventListener('click', () => { show(current - 1); start(); });
            next.addEventListener('click', () => { show(current + 1); start(); });
            carousel.addEventListener('mouseenter', stop);
            carousel.addEventListener('mouseleave', start);
            carousel.addEventListener('focusin', stop);
            carousel.addEventListener('focusout', event => {
                if (!carousel.contains(event.relatedTarget)) start();
            });
            document.addEventListener('visibilitychange', () => document.hidden ? stop() : start());

            // Enable CSS carousel behavior after initial slide visibility is set.
            show(0);
            carousel.classList.add('enhanced');
            document.body.classList.add('carousel-ready');
            start();
        }
    }

    /* Click to expand uploaded CAD and stress images. Standard image links
       remain available as the fallback when <dialog> is unsupported. */
    const lightbox = document.querySelector('#image-lightbox');
    if (lightbox && typeof lightbox.showModal === 'function') {
        const picture = lightbox.querySelector('[data-lightbox-image]');
        const caption = lightbox.querySelector('[data-lightbox-caption]');
        let origin;
        document.querySelectorAll('[data-lightbox]').forEach(anchor => {
            anchor.addEventListener('click', event => {
                event.preventDefault();
                origin = anchor;
                picture.src = anchor.href;
                picture.alt = anchor.querySelector('img')?.alt || 'Expanded engineering image';
                caption.textContent = anchor.dataset.caption || picture.alt;
                lightbox.showModal();
            });
        });
        const close = () => { lightbox.close(); origin?.focus(); };
        lightbox.querySelector('[data-lightbox-close]')?.addEventListener('click', close);
        lightbox.addEventListener('click', event => {
            if (event.target === lightbox) close();
        });
    }
})();
