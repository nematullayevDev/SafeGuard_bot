/* ══════════════════════════════════════════════
   SafeGuard Bot — Landing Page JavaScript
   Animations | Interactivity | Effects
══════════════════════════════════════════════ */

// ── DOM tayyor bo'lgach ishga tushirish ────────
document.addEventListener('DOMContentLoaded', () => {
  initNavbar();
  initParticles();
  initCounters();
  initScrollAnimations();
  initBurgerMenu();
  initTypingEffect();
});

/* ══ 1. NAVBAR — scroll da fonli bo'ladi ═════ */
function initNavbar() {
  const navbar = document.getElementById('navbar');
  window.addEventListener('scroll', () => {
    if (window.scrollY > 50) {
      navbar.classList.add('scrolled');
    } else {
      navbar.classList.remove('scrolled');
    }
  });

  // Smooth scroll for nav links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        e.preventDefault();
        const offset = 80;
        const top = target.getBoundingClientRect().top + window.scrollY - offset;
        window.scrollTo({ top, behavior: 'smooth' });
        // Mobil menyuni yopish
        document.querySelector('.nav-links')?.classList.remove('open');
      }
    });
  });
}

/* ══ 2. PARTICLES — uchib yuruvchi nuqtalar ═══ */
function initParticles() {
  const container = document.getElementById('particles');
  if (!container) return;

  const count = 40;
  for (let i = 0; i < count; i++) {
    const p = document.createElement('div');
    p.className = 'particle';

    const size = Math.random() * 3 + 1;
    const left = Math.random() * 100;
    const duration = Math.random() * 15 + 8;
    const delay = Math.random() * 10;
    const colors = ['#00d4ff', '#00ff88', '#a855f7', '#ffffff'];
    const color = colors[Math.floor(Math.random() * colors.length)];

    p.style.cssText = `
      width: ${size}px;
      height: ${size}px;
      left: ${left}%;
      background: ${color};
      animation-duration: ${duration}s;
      animation-delay: ${delay}s;
      box-shadow: 0 0 ${size * 2}px ${color};
    `;
    container.appendChild(p);
  }
}

/* ══ 3. COUNTERS — raqamlar animatsiyasi ══════ */
function initCounters() {
  const counters = document.querySelectorAll('.counter, .hstat-num');
  let started = false;

  function startCounters() {
    if (started) return;
    started = true;

    counters.forEach(counter => {
      const target = parseInt(counter.getAttribute('data-target') || counter.textContent);
      if (isNaN(target)) return;

      let current = 0;
      const duration = 1800;
      const step = target / (duration / 16);

      const timer = setInterval(() => {
        current += step;
        if (current >= target) {
          current = target;
          clearInterval(timer);
        }
        counter.textContent = Math.floor(current);
      }, 16);
    });
  }

  // Hero stats — sahifa yuklanganda
  setTimeout(() => {
    document.querySelectorAll('.hstat-num').forEach(counter => {
      const target = parseInt(counter.getAttribute('data-target'));
      if (isNaN(target)) return;
      let current = 0;
      const step = target / (1500 / 16);
      const timer = setInterval(() => {
        current += step;
        if (current >= target) { current = target; clearInterval(timer); }
        counter.textContent = Math.floor(current);
      }, 16);
    });
  }, 800);

  // Stats section — ko'ringanda
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.querySelectorAll('.counter').forEach(counter => {
          const target = parseInt(counter.getAttribute('data-target'));
          if (isNaN(target)) return;
          let current = 0;
          const step = target / (1500 / 16);
          const timer = setInterval(() => {
            current += step;
            if (current >= target) { current = target; clearInterval(timer); }
            counter.textContent = Math.floor(current);
          }, 16);
        });
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.3 });

  const statsSection = document.querySelector('.stats-section');
  if (statsSection) observer.observe(statsSection);
}

/* ══ 4. SCROLL ANIMATIONS — elementlar paydo bo'ladi ══ */
function initScrollAnimations() {
  // Feature cards
  const featureObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const delay = parseInt(entry.target.getAttribute('data-delay') || 0);
        setTimeout(() => {
          entry.target.classList.add('visible');
        }, delay);
        featureObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('.feature-card').forEach(card => {
    featureObserver.observe(card);
  });

  // General fade-in for other sections
  const generalObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
        generalObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll(
    '.step, .stat-card, .legal-card, .tech-card'
  ).forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(20px)';
    el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
    generalObserver.observe(el);
  });
}

/* ══ 5. BURGER MENU — mobil navigatsiya ══════ */
function initBurgerMenu() {
  const burger = document.getElementById('burger');
  const navLinks = document.querySelector('.nav-links');

  if (!burger || !navLinks) return;

  burger.addEventListener('click', () => {
    navLinks.classList.toggle('open');
    const icon = burger.querySelector('i');
    if (navLinks.classList.contains('open')) {
      icon.className = 'fas fa-times';
    } else {
      icon.className = 'fas fa-bars';
    }
  });

  // Tashqariga bosilganda yopish
  document.addEventListener('click', (e) => {
    if (!burger.contains(e.target) && !navLinks.contains(e.target)) {
      navLinks.classList.remove('open');
      burger.querySelector('i').className = 'fas fa-bars';
    }
  });
}

/* ══ 6. TYPING EFFECT — phone mockup ═════════ */
function initTypingEffect() {
  const messages = [
    { type: 'bot', text: '🚨 Xavfli havola aniqlandi va bloklandi!' },
    { type: 'bot', text: '✅ Fayl tekshirildi — xavfsiz' },
    { type: 'bot', text: '⚠️ Spam xabar bloklandi!' },
    { type: 'bot', text: '🛡️ Guruh himoyada — 24/7 faol' },
    { type: 'user', text: 'https://phishing-site.uz' },
    { type: 'bot', text: '🔴 XAVFLI — VirusTotal: 23/70 antivirus topdi!' },
  ];

  const screen = document.querySelector('.phone-screen');
  if (!screen) return;

  let idx = 0;

  function addMessage() {
    // Eski xabarlar ko'p bo'lsa birinchisini o'chirish
    const existing = screen.querySelectorAll('.chat-msg');
    if (existing.length > 4) {
      existing[0].style.transition = 'opacity 0.3s';
      existing[0].style.opacity = '0';
      setTimeout(() => existing[0].remove(), 300);
    }

    const msg = messages[idx % messages.length];
    idx++;

    const div = document.createElement('div');
    div.className = `chat-msg ${msg.type}`;
    div.style.opacity = '0';
    div.style.transform = 'translateY(10px)';
    div.style.transition = 'opacity 0.4s, transform 0.4s';

    if (msg.type === 'bot') {
      div.innerHTML = `<i class="fas fa-shield-halved"></i><span>${msg.text}</span>`;
    } else {
      div.innerHTML = `<span>${msg.text}</span>`;
    }

    screen.appendChild(div);

    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        div.style.opacity = '1';
        div.style.transform = 'translateY(0)';
      });
    });
  }

  // Typing indicator
  function showTyping() {
    const typing = document.createElement('div');
    typing.className = 'chat-msg bot typing-indicator';
    typing.innerHTML = `
      <i class="fas fa-shield-halved"></i>
      <span><span class="dot"></span><span class="dot"></span><span class="dot"></span></span>
    `;
    screen.appendChild(typing);

    setTimeout(() => {
      typing.remove();
      addMessage();
    }, 1200);
  }

  // Har 3 sekundda yangi xabar
  setTimeout(() => {
    setInterval(showTyping, 3000);
  }, 2500);
}

/* ══ 7. PARALLAX — hero background ═══════════ */
window.addEventListener('scroll', () => {
  const scrollY = window.scrollY;
  const gridLines = document.querySelector('.grid-lines');
  if (gridLines) {
    gridLines.style.transform = `translateY(${scrollY * 0.1}px)`;
  }
});

/* ══ 8. CURSOR GLOW EFFECT ════════════════════ */
const glow = document.createElement('div');
glow.style.cssText = `
  position: fixed;
  width: 300px; height: 300px;
  background: radial-gradient(circle, rgba(0,212,255,0.05) 0%, transparent 70%);
  border-radius: 50%;
  pointer-events: none;
  z-index: 0;
  transition: transform 0.1s ease;
  transform: translate(-50%, -50%);
`;
document.body.appendChild(glow);

document.addEventListener('mousemove', (e) => {
  glow.style.left = e.clientX + 'px';
  glow.style.top = e.clientY + 'px';
});

/* ══ 9. ACTIVE NAV LINK — scroll da belgilash ═ */
const sections = document.querySelectorAll('section[id]');
const navLinksAll = document.querySelectorAll('.nav-links a[href^="#"]');

window.addEventListener('scroll', () => {
  let current = '';
  sections.forEach(section => {
    const top = section.getBoundingClientRect().top;
    if (top <= 100) current = section.id;
  });

  navLinksAll.forEach(link => {
    link.style.color = '';
    if (link.getAttribute('href') === `#${current}`) {
      link.style.color = 'var(--blue)';
    }
  });
});

/* ══ 10. CARD TILT EFFECT ═════════════════════ */
document.querySelectorAll('.feature-card, .stat-card').forEach(card => {
  card.addEventListener('mousemove', (e) => {
    const rect = card.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const centerX = rect.width / 2;
    const centerY = rect.height / 2;
    const rotateX = ((y - centerY) / centerY) * -5;
    const rotateY = ((x - centerX) / centerX) * 5;
    card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-6px)`;
  });
  card.addEventListener('mouseleave', () => {
    card.style.transform = '';
  });
});
