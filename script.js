/* ============================================
   DebtMap — Orbital Animation & Scroll FX
   ============================================ */

(function () {
  'use strict';

  // ---- Orbital Canvas Animation ----
  const canvas = document.getElementById('orbital-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  let W, H, cx, cy, dpr;
  let frame = 0;

  function resize() {
    const rect = canvas.parentElement.getBoundingClientRect();
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    W = rect.width;
    H = rect.height;
    canvas.width = W * dpr;
    canvas.height = H * dpr;
    canvas.style.width = W + 'px';
    canvas.style.height = H + 'px';
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    cx = W / 2;
    cy = H / 2;
  }

  window.addEventListener('resize', resize);
  resize();

  // Orbital items - code fragments, dependency nodes, warning indicators
  const fragments = [
    { label: 'import openai', type: 'code', orbit: 0.72, speed: 0.0004, offset: 0 },
    { label: 'requests==2.28', type: 'dep', orbit: 0.78, speed: -0.0003, offset: 1.2 },
    { label: '⚠ deprecated', type: 'warn', orbit: 0.65, speed: 0.0005, offset: 2.5 },
    { label: 'urllib3<2.0', type: 'dep', orbit: 0.82, speed: 0.00035, offset: 3.8 },
    { label: 'model="davinci"', type: 'code', orbit: 0.6, speed: -0.00045, offset: 5.0 },
    { label: 'CVE-2024', type: 'warn', orbit: 0.88, speed: 0.00025, offset: 0.8 },
    { label: 'flask==1.x', type: 'dep', orbit: 0.7, speed: -0.0004, offset: 4.2 },
    { label: 'async def', type: 'code', orbit: 0.56, speed: 0.00055, offset: 1.8 },
  ];

  // Particles
  const PARTICLE_COUNT = 40;
  const particles = [];
  for (let i = 0; i < PARTICLE_COUNT; i++) {
    particles.push({
      angle: Math.random() * Math.PI * 2,
      orbit: 0.3 + Math.random() * 0.65,
      speed: (Math.random() - 0.5) * 0.0006,
      size: 1 + Math.random() * 1.5,
      alpha: 0.1 + Math.random() * 0.3,
    });
  }

  // Scanning line
  let scanAngle = 0;

  // Colors
  const COL_ACCENT = { r: 88, g: 166, b: 255 };
  const COL_WARN = { r: 210, g: 153, b: 34 };
  const COL_RED = { r: 248, g: 81, b: 73 };
  const COL_GREEN = { r: 63, g: 185, b: 80 };

  function getTypeColor(type) {
    if (type === 'warn') return COL_WARN;
    if (type === 'dep') return COL_RED;
    return COL_ACCENT;
  }

  function draw() {
    frame++;
    ctx.clearRect(0, 0, W, H);

    const minDim = Math.min(W, H);

    // Draw orbit rings (very subtle)
    const rings = [0.56, 0.65, 0.72, 0.78, 0.82, 0.88];
    rings.forEach(r => {
      ctx.beginPath();
      ctx.arc(cx, cy, r * minDim * 0.45, 0, Math.PI * 2);
      ctx.strokeStyle = 'rgba(48, 54, 61, 0.25)';
      ctx.lineWidth = 0.5;
      ctx.stroke();
    });

    // Scanning sweep (subtle)
    scanAngle += 0.003;
    const sweepGrad = ctx.createConicGradient(scanAngle, cx, cy);
    sweepGrad.addColorStop(0, 'rgba(88, 166, 255, 0.04)');
    sweepGrad.addColorStop(0.08, 'rgba(88, 166, 255, 0)');
    sweepGrad.addColorStop(1, 'rgba(88, 166, 255, 0)');
    ctx.beginPath();
    ctx.arc(cx, cy, minDim * 0.42, 0, Math.PI * 2);
    ctx.fillStyle = sweepGrad;
    ctx.fill();

    // Draw particles
    particles.forEach(p => {
      p.angle += p.speed;
      const r = p.orbit * minDim * 0.45;
      const px = cx + Math.cos(p.angle) * r;
      const py = cy + Math.sin(p.angle) * r;
      ctx.beginPath();
      ctx.arc(px, py, p.size, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(88, 166, 255, ${p.alpha})`;
      ctx.fill();
    });

    // Draw connections between nearby fragments
    for (let i = 0; i < fragments.length; i++) {
      for (let j = i + 1; j < fragments.length; j++) {
        const fi = fragments[i];
        const fj = fragments[j];
        const ri = fi.orbit * minDim * 0.45;
        const rj = fj.orbit * minDim * 0.45;
        const ai = fi.offset + frame * fi.speed;
        const aj = fj.offset + frame * fj.speed;
        const x1 = cx + Math.cos(ai) * ri;
        const y1 = cy + Math.sin(ai) * ri;
        const x2 = cx + Math.cos(aj) * rj;
        const y2 = cy + Math.sin(aj) * rj;
        const dist = Math.hypot(x2 - x1, y2 - y1);
        if (dist < minDim * 0.25) {
          const alpha = (1 - dist / (minDim * 0.25)) * 0.12;
          ctx.beginPath();
          ctx.moveTo(x1, y1);
          ctx.lineTo(x2, y2);
          ctx.strokeStyle = `rgba(88, 166, 255, ${alpha})`;
          ctx.lineWidth = 0.6;
          ctx.stroke();
        }
      }
    }

    // Draw orbital fragments
    fragments.forEach(f => {
      const angle = f.offset + frame * f.speed;
      const r = f.orbit * minDim * 0.45;
      const fx = cx + Math.cos(angle) * r;
      const fy = cy + Math.sin(angle) * r;
      const col = getTypeColor(f.type);

      // Glow
      const glow = ctx.createRadialGradient(fx, fy, 0, fx, fy, 20);
      glow.addColorStop(0, `rgba(${col.r}, ${col.g}, ${col.b}, 0.2)`);
      glow.addColorStop(1, `rgba(${col.r}, ${col.g}, ${col.b}, 0)`);
      ctx.beginPath();
      ctx.arc(fx, fy, 20, 0, Math.PI * 2);
      ctx.fillStyle = glow;
      ctx.fill();

      // Node dot
      ctx.beginPath();
      ctx.arc(fx, fy, 3, 0, Math.PI * 2);
      ctx.fillStyle = `rgb(${col.r}, ${col.g}, ${col.b})`;
      ctx.fill();

      // Label
      ctx.font = '10px "JetBrains Mono", monospace';
      ctx.fillStyle = `rgba(${col.r}, ${col.g}, ${col.b}, 0.7)`;
      ctx.textAlign = 'center';
      ctx.fillText(f.label, fx, fy - 10);
    });

    // Center glow
    const centerGlow = ctx.createRadialGradient(cx, cy, 0, cx, cy, minDim * 0.15);
    centerGlow.addColorStop(0, 'rgba(88, 166, 255, 0.04)');
    centerGlow.addColorStop(1, 'transparent');
    ctx.beginPath();
    ctx.arc(cx, cy, minDim * 0.15, 0, Math.PI * 2);
    ctx.fillStyle = centerGlow;
    ctx.fill();

    requestAnimationFrame(draw);
  }

  requestAnimationFrame(draw);

  // ---- Scroll Reveal ----
  const revealTargets = [
    'hero-badge', 'hero-heading', 'hero-sub', 'hero-ctas', 'hero-trust',
    'hero-right',
    'steps-label', 'steps-title', 'steps-desc',
    'step-1', 'step-2', 'step-3',
    'features-label', 'features-title', 'features-desc',
    'feature-1', 'feature-2', 'feature-3', 'feature-4',
    'preview-label', 'preview-title', 'preview-desc',
    'preview-container', 'preview-meta',
    'cta-box',
  ];

  // Add fade-up class to all targets
  revealTargets.forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      el.classList.add('fade-up');
    }
  });

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          // Stagger siblings
          const el = entry.target;
          const siblings = el.parentElement.querySelectorAll('.fade-up:not(.visible)');
          let delay = 0;
          siblings.forEach(s => {
            if (s === el || isInViewport(s)) {
              setTimeout(() => s.classList.add('visible'), delay);
              delay += 80;
            }
          });
          el.classList.add('visible');
          observer.unobserve(el);
        }
      });
    },
    { threshold: 0.15, rootMargin: '0px 0px -40px 0px' }
  );

  function isInViewport(el) {
    const rect = el.getBoundingClientRect();
    return rect.top < window.innerHeight && rect.bottom > 0;
  }

  revealTargets.forEach(id => {
    const el = document.getElementById(id);
    if (el) observer.observe(el);
  });

  // ---- Smooth scroll for anchor links ----
  document.querySelectorAll('a[href^="#"]').forEach(link => {
    link.addEventListener('click', e => {
      const target = document.querySelector(link.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  // ---- Nav background on scroll ----
  const nav = document.getElementById('main-nav');
  let ticking = false;
  window.addEventListener('scroll', () => {
    if (!ticking) {
      requestAnimationFrame(() => {
        if (window.scrollY > 20) {
          nav.style.borderBottomColor = 'rgba(48, 54, 61, 0.6)';
        } else {
          nav.style.borderBottomColor = 'rgba(33, 38, 45, 1)';
        }
        ticking = false;
      });
      ticking = true;
    }
  });

  // ---- Typing effect on viz-center-card ----
  const oldCode = document.querySelector('#viz-label-old code');
  const newCode = document.querySelector('#viz-label-new code');

  if (oldCode && newCode) {
    const oldText = oldCode.textContent;
    const newText = newCode.textContent;

    // Cycle animation: show old → transform → show new → pause → reset
    function runTransformCycle() {
      // Phase 1: type old code
      oldCode.textContent = '';
      newCode.textContent = '';
      oldCode.parentElement.style.opacity = '1';
      newCode.parentElement.style.opacity = '0.3';
      document.getElementById('viz-arrow').style.opacity = '0.3';

      let i = 0;
      const typeOld = setInterval(() => {
        if (i < oldText.length) {
          oldCode.textContent += oldText[i];
          i++;
        } else {
          clearInterval(typeOld);
          // Phase 2: pause then transform
          setTimeout(() => {
            document.getElementById('viz-arrow').style.opacity = '1';
            newCode.parentElement.style.opacity = '1';
            let j = 0;
            const typeNew = setInterval(() => {
              if (j < newText.length) {
                newCode.textContent += newText[j];
                j++;
              } else {
                clearInterval(typeNew);
                // Phase 3: hold then restart
                setTimeout(runTransformCycle, 5000);
              }
            }, 30);
          }, 1200);
        }
      }, 40);
    }

    // Start after initial load
    setTimeout(runTransformCycle, 1500);
  }

  // ---- Dashboard Integration & Mode Toggle ----
  const ctaAnalyzeBtns = document.querySelectorAll('#cta-analyze, #cta-final');
  const modal = document.getElementById('analyze-modal');
  const modalClose = document.getElementById('modal-close');
  const btnSubmitCode = document.getElementById('btn-submit-code');
  const analysisResult = document.getElementById('analysis-result');
  const dashboardStatus = document.getElementById('dashboard-status');
  const inputContainer = document.getElementById('input-container');
  const modeBtns = document.querySelectorAll('.mode-btn');

  let currentMode = 'code';

  if (ctaAnalyzeBtns.length > 0 && modal) {
    // Mode Switching
    modeBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        const mode = btn.dataset.mode;
        if (mode === currentMode) return;

        currentMode = mode;
        modeBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        if (mode === 'code') {
          inputContainer.innerHTML = '<textarea id="code-input" placeholder="Paste your legacy code here... (e.g. import openai...)"></textarea>';
        } else {
          inputContainer.innerHTML = '<input type="text" id="repo-input" placeholder="https://github.com/username/repository">';
        }
      });
    });

    ctaAnalyzeBtns.forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        modal.style.display = 'block';
        document.body.style.overflow = 'hidden';
      });
    });

    modalClose.addEventListener('click', () => {
      modal.style.display = 'none';
      document.body.style.overflow = 'auto';
    });

    // Ripple effect helper
    function createRipple(event, button) {
      const ripple = document.createElement("span");
      ripple.classList.add("ripple");
      const rect = button.getBoundingClientRect();
      const size = Math.max(rect.width, rect.height);
      const x = event.clientX - rect.left - size / 2;
      const y = event.clientY - rect.top - size / 2;
      ripple.style.width = ripple.style.height = `${size}px`;
      ripple.style.left = `${x}px`;
      ripple.style.top = `${y}px`;
      button.appendChild(ripple);
      setTimeout(() => ripple.remove(), 600);
    }

    btnSubmitCode.addEventListener('click', async (e) => {
      createRipple(e, btnSubmitCode);

      let payload = {};
      const codeInput = document.getElementById('code-input');
      const repoInput = document.getElementById('repo-input');

      if (currentMode === 'code') {
        const code = codeInput ? codeInput.value : '';
        if (!code.trim()) return;
        payload = { code: code };
      } else {
        const url = repoInput ? repoInput.value : '';
        if (!url.trim()) return;
        payload = { repo_url: url };
      }

      // UI Loading State
      btnSubmitCode.classList.add('loading');
      btnSubmitCode.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" class="scanning-pulse"><path d="M21 12a9 9 0 1 1-6.219-8.56" /></svg>`;

      dashboardStatus.textContent = currentMode === 'repo' ? "Initializing Pipeline..." : "Analyzing AST...";
      dashboardStatus.className = "status-badge status-scanning";

      analysisResult.classList.remove('visible');
      analysisResult.innerHTML = `
        <div class="empty-state" style="padding: 40px; width: 100%;">
          <div class="skeleton-shimmer" style="width: 100%; height: 120px; border-radius: 16px; margin-bottom: 24px;"></div>
          <div class="skeleton-shimmer" style="width: 80%; height: 20px; border-radius: 4px; margin-bottom: 12px;"></div>
          <div class="skeleton-shimmer" style="width: 60%; height: 20px; border-radius: 4px;"></div>
          <p style="margin-top: 32px; font-weight: 500; color: var(--text-muted); text-align: center;">Analyzing codebase patterns...</p>
        </div>
      `;

      try {
        const response = await fetch('http://localhost:5000/analyze', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (data.status === "no_issues") {
          dashboardStatus.textContent = "Clean";
          dashboardStatus.className = "status-badge status-success";
          analysisResult.innerHTML = `
            <div class="empty-state">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="color: var(--green);"><path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
              <p style="color: var(--green);">No deprecated APIs found. Your codebase is up to date!</p>
            </div>
          `;
          return;
        }

        if (data.status === "error") {
          throw new Error(data.message);
        }
        const results = data.all_results || [data.scan_result];
        dashboardStatus.textContent = `${results.length} Issues Found`;
        dashboardStatus.className = "status-badge status-idle";
        dashboardStatus.style.color = "var(--yellow)";

        // CALCULATE SUMMARY METRICS
        let totalCost = 0;
        let effortMap = { 'low': 1, 'medium': 2, 'high': 3 };
        let highestEffortValue = 0;
        let highestEffortLabel = 'Low';
        let uniqueFiles = new Set();

        results.forEach(r => {
          totalCost += (r.estimated_cost || 0);
          uniqueFiles.add(r.file);
          const eff = (r.effort || 'low').toLowerCase();
          if (effortMap[eff] > highestEffortValue) {
            highestEffortValue = effortMap[eff];
            highestEffortLabel = r.effort;
          }
        });

        // Show Summary HUD
        const summaryBox = document.getElementById('migration-summary');
        summaryBox.style.display = 'flex';

        // Animate Numbers
        animateValue("total-cost", 0, totalCost, 1000, "$");
        animateValue("total-files", 0, uniqueFiles.size, 1000, "");
        document.getElementById('total-effort').textContent = highestEffortLabel;

        analysisResult.innerHTML = ''; // Clear empty state

        results.forEach((scan, index) => {
          let diffHtml = '';
          let originalText = '';
          let suggestedText = '';

          if (scan.occurrences && scan.occurrences.length > 0) {
            const occ = scan.occurrences[0];
            originalText = occ.original_code;
            suggestedText = occ.suggested_code;

            if (originalText) diffHtml += `<div class="diff-line removed">- ${originalText.trim()}</div>`;
            if (suggestedText) diffHtml += `<div class="diff-line added">+ ${suggestedText.trim()}</div>`;
          }

          const card = document.createElement('div');
          card.className = 'result-card';
          card.style.animationDelay = `${index * 0.1}s`;
          card.innerHTML = `
                ${scan.file ? `<div class="file-path-badge">${scan.file}</div>` : ''}
                <div class="result-header">
                  <h4 class="api-name">⚠ ${scan.api_name || 'Deprecated API'}</h4>
                  <div class="metrics">
                    <span class="badge effort-${(scan.effort || 'medium').toLowerCase()}">${scan.effort || 'Medium'} Effort</span>
                    <span class="badge cost">${scan.estimated_cost || 0}</span>
                  </div>
                </div>
                <p class="reason">${scan.reason || 'Consider updating this to a modern equivalent.'}</p>
                
                ${diffHtml ? `
                <div class="diff-view">
                  ${diffHtml}
                </div>` : ''}

                <div class="manual-steps">
                  <h5>AI Implementation Guide</h5>
                  <div class="steps-content">${scan.manual_steps || '1. Replace usage manually.'}</div>
                </div>
                
                <div class="action-buttons">
                  <button class="btn btn-secondary btn-apply-fix" 
                    data-orig="${originalText.replace(/"/g, '&quot;')}" 
                    data-sugg="${suggestedText.replace(/"/g, '&quot;')}"
                    data-full="${(scan.full_content || '').replace(/"/g, '&quot;')}">
                    ${currentMode === 'repo' ? '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right:8px;"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg> View in Editor' : 'Apply Fix Automatically'}
                  </button>
                </div>
            `;

          analysisResult.appendChild(card);
        });

        // Bind View / Fix Buttons
        document.querySelectorAll('.btn-apply-fix').forEach(btn => {
          btn.addEventListener('click', () => {
            const orig = btn.dataset.orig;
            const sugg = btn.dataset.sugg;
            const fullContent = btn.dataset.full;

            // State: Viewing a repo file
            if (currentMode === 'repo' && fullContent) {
              const codeBtn = document.querySelector('.mode-btn[data-mode="code"]');
              codeBtn.click();

              setTimeout(() => {
                const codeInputArea = document.getElementById('code-input');
                if (codeInputArea) {
                  codeInputArea.value = fullContent;
                  // Transform button to Fix mode
                  btn.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right:8px;"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg> Apply Fix in Editor`;
                  btn.className = "btn btn-primary btn-apply-fix";
                  btn.dataset.full = ""; // Clear so next click applies fix

                  // Visual feedback on editor
                  codeInputArea.style.boxShadow = "inset 0 0 20px rgba(88, 166, 255, 0.2)";
                  setTimeout(() => { codeInputArea.style.boxShadow = "none"; }, 1000);
                }
              }, 50);
              return;
            }

            // State: Applying a fix
            const codeInputArea = document.getElementById('code-input');
            if (codeInputArea && orig && sugg) {
              const oldCode = codeInputArea.value;
              if (oldCode.includes(orig)) {
                codeInputArea.value = oldCode.replace(orig, sugg);
                btn.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right:8px;"><polyline points="20 6 9 17 4 12"></polyline></svg> Modernized`;
                btn.classList.add('status-success');
                btn.style.background = "var(--green-dim)";
                btn.style.color = "var(--green)";
                btn.disabled = true;
              } else {
                btn.textContent = "Instance not found";
                btn.style.color = "var(--red)";
              }
            }
          });
        });

      } catch (err) {
        dashboardStatus.textContent = "Error";
        dashboardStatus.className = "status-badge status-idle";
        dashboardStatus.style.color = "var(--red)";

        analysisResult.innerHTML = `
          <div class="empty-state">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="color: var(--red);"><polygon points="7.86 2 16.14 2 22 7.86 22 16.14 16.14 22 7.86 22 2 16.14 2 7.86 7.86 2"></polygon><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
            <p style="color: var(--red);">Error: ${err.message}</p>
          </div>
        `;
      } finally {
        btnSubmitCode.classList.remove('loading');
        btnSubmitCode.classList.add('success');
        btnSubmitCode.innerHTML = `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12" /></svg>`;
        
        setTimeout(() => {
          btnSubmitCode.classList.remove('success');
          
          // DO SOMETHING USEFUL: Turn it into a Search/Filter Bar
          btnSubmitCode.classList.add('is-searching');
          btnSubmitCode.innerHTML = `
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg>
            <input type="text" id="detection-filter" placeholder="Search detections (e.g. 'escape')..." autocomplete="off">
          `;
          
          const filterInput = document.getElementById('detection-filter');
          filterInput.focus();
          
          filterInput.addEventListener('input', (e) => {
            const term = e.target.value.toLowerCase();
            const cards = document.querySelectorAll('.result-card');
            cards.forEach(card => {
              const text = card.innerText.toLowerCase();
              if (text.includes(term)) {
                card.style.display = 'block';
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
              } else {
                card.style.display = 'none';
              }
            });
          });

          // Allow clicking the icon to reset for a new scan
          btnSubmitCode.querySelector('svg').addEventListener('click', (e) => {
             e.stopPropagation();
             btnSubmitCode.classList.remove('is-searching');
             btnSubmitCode.innerHTML = 'Analyze Codebase';
          });

        }, 2000);

        // TRIGGER STAGGERED REVEAL
        setTimeout(() => {
          analysisResult.classList.add('visible');
        }, 100);
      }
    });
  }

  // Helper: Animate Value
  function animateValue(id, start, end, duration, prefix) {
    const obj = document.getElementById(id);
    let startTimestamp = null;
    const step = (timestamp) => {
      if (!startTimestamp) startTimestamp = timestamp;
      const progress = Math.min((timestamp - startTimestamp) / duration, 1);
      obj.innerHTML = prefix + Math.floor(progress * (end - start) + start);
      if (progress < 1) {
        window.requestAnimationFrame(step);
      }
    };
    window.requestAnimationFrame(step);
  }

  // ---- Navigation Fixes ----
  document.querySelectorAll('a.nav-link, a.btn, a.nav-cta').forEach(link => {
    link.addEventListener('click', (e) => {
      const href = link.getAttribute('href');
      if (href && href.startsWith('#') && href.length > 1) {
        const target = document.querySelector(href);
        if (target) {
          e.preventDefault();
          target.scrollIntoView({ behavior: 'smooth' });
        }
      }
    });
  });

})();
