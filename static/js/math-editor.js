/**
 * math-editor.js — محرر المعادلات الموحّد لمنصة آمنة التعليمية
 * يستخدم MathLive للإدخال و MathJax للعرض
 * يدعم إدراج معادلات LaTeX داخل النصوص العربية (inline math)
 * يدعم رسم المعادلات باللمس وتحويلها إلى LaTeX (مثل Web Equation)
 *
 * الاستخدام:
 *   MathEditor.init()                    — تهيئة المحرر
 *   MathEditor.openFor(fieldId)          — فتح نافذة المعادلة لحقل معين
 *   MathEditor.insertSymbol(sym, fieldId) — إدراج رمز في حقل
 *   MathEditor.refreshAll()              — تحديث عرض كل المعادلات
 */

const MathEditor = (() => {
  'use strict';

  // ─── الرموز والقوالب ───
  const SYMBOLS = {
    arabic: [
      {s:'س',t:'س'},{s:'ص',t:'ص'},{s:'ع',t:'ع'},{s:'م',t:'م'},
      {s:'ن',t:'ن'},{s:'ق',t:'ق'},{s:'ك',t:'ك'},{s:'أ',t:'أ'},
      {s:'ب',t:'ب'},{s:'ج',t:'ج'},{s:'د',t:'د'},
      {s:'₁',t:'₁'},{s:'₂',t:'₂'},{s:'₃',t:'₃'}
    ],
    operators: [
      {s:'×',t:'ضرب'},{s:'÷',t:'قسمة'},{s:'±',t:'± موجب سالب'},
      {s:'≠',t:'لا يساوي'},{s:'≤',t:'أصغر أو يساوي'},{s:'≥',t:'أكبر أو يساوي'},
      {s:'≈',t:'تقريباً'},{s:'√',t:'جذر'},{s:'²',t:'تربيع'},{s:'³',t:'تكعيب'},
      {s:'½',t:'نصف'},{s:'⅓',t:'ثلث'},{s:'¼',t:'ربع'},{s:'%',t:'نسبة'},
      {s:'∞',t:'لا نهاية'}
    ],
    greek: [
      {s:'π',t:'باي'},{s:'α',t:'ألفا'},{s:'β',t:'بيتا'},{s:'γ',t:'جاما'},
      {s:'θ',t:'ثيتا'},{s:'λ',t:'لامدا'},{s:'μ',t:'ميو'},{s:'σ',t:'سيجما'},
      {s:'Σ',t:'مجموع'},{s:'Δ',t:'دلتا'},{s:'Ω',t:'أوميجا'},{s:'φ',t:'فاي'}
    ],
    geometry: [
      {s:'°',t:'درجة'},{s:'∠',t:'زاوية'},{s:'△',t:'مثلث'},{s:'□',t:'مربع'},
      {s:'⊥',t:'عمودي'},{s:'∥',t:'متوازي'},{s:'∼',t:'مشابه'},{s:'≅',t:'مطابق'},
      {s:'⊙',t:'دائرة'},{s:'∫',t:'تكامل'}
    ],
    relations: [
      {s:'∈',t:'ينتمي'},{s:'∉',t:'لا ينتمي'},{s:'⊂',t:'مجموعة جزئية'},
      {s:'∪',t:'اتحاد'},{s:'∩',t:'تقاطع'},{s:'→',t:'سهم'},{s:'←',t:'سهم يسار'},
      {s:'↔',t:'سهمين'},{s:'⇒',t:'يؤدي إلى'},{s:'⇔',t:'تكافؤ'}
    ]
  };

  const TEMPLATES = [
    {label:'كسر', latex:'\\frac{a}{b}'},
    {label:'أس', latex:'x^{2}'},
    {label:'جذر', latex:'\\sqrt{x}'},
    {label:'المعادلة التربيعية', latex:'\\frac{-b \\pm \\sqrt{b^2-4ac}}{2a}'},
    {label:'مجموع', latex:'\\sum_{i=1}^{n}'},
    {label:'تكامل', latex:'\\int_{a}^{b}'},
    {label:'متجه', latex:'\\vec{v}'},
    {label:'زاوية', latex:'\\angle ABC'},
    {label:'مثلث', latex:'\\triangle ABC'},
    {label:'مساحة دائرة', latex:'\\pi r^2'},
    {label:'مصفوفة', latex:'\\begin{pmatrix} a & b \\\\ c & d \\end{pmatrix}'},
    {label:'كسر عشري', latex:'0.\\overline{3}'},
    {label:'نسبة', latex:'a : b'},
    {label:'لوغاريتم', latex:'\\log_{a} b'}
  ];

  // ─── المتغيرات ───
  let _activeFieldId = null;
  let _modalEl = null;
  let _mlField = null;
  let _initialized = false;
  let _previewTimers = {};
  let _activeTab = 'keyboard'; // 'keyboard' | 'draw'

  // ─── متغيرات الرسم ───
  let _canvas = null;
  let _ctx = null;
  let _drawing = false;
  let _undoStack = [];
  let _redoStack = [];
  let _penSize = 3;
  let _penColor = '#1a1a2e';
  let _eraserMode = false;
  let _points = [];         // نقاط الخط الحالي
  let _recognizedLatex = '';  // نتيجة التحويل

  // ═══════════════════════════════════════════
  //  Canvas — رسم المعادلات باللمس
  // ═══════════════════════════════════════════

  function _initCanvas() {
    _canvas = document.getElementById('me-draw-canvas');
    if (!_canvas) return;
    _ctx = _canvas.getContext('2d');

    // ── منع التمرير أثناء الرسم ──
    _canvas.style.touchAction = 'none';

    // ── Pointer events (موحّد: لمس + فأرة + قلم) ──
    _canvas.addEventListener('pointerdown', _onPointerDown);
    _canvas.addEventListener('pointermove', _onPointerMove);
    _canvas.addEventListener('pointerup',   _onPointerUp);
    _canvas.addEventListener('pointerleave', _onPointerUp);
    _canvas.addEventListener('pointercancel', _onPointerUp);

    // ── ضبط الحجم ──
    _fitCanvas();
    _drawGrid();
    _saveCanvasState(); // حالة أولية (فارغة مع الشبكة)

    // ── شريط الأدوات ──
    const sizeSlider = document.getElementById('me-pen-size');
    if (sizeSlider) {
      sizeSlider.addEventListener('input', e => { _penSize = +e.target.value; });
    }
  }

  /** مطابقة حجم Canvas لأبعاد CSS (دعم Retina) */
  function _fitCanvas() {
    if (!_canvas) return;
    const rect = _canvas.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    _canvas.width  = rect.width  * dpr;
    _canvas.height = rect.height * dpr;
    _ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    _ctx.lineCap  = 'round';
    _ctx.lineJoin = 'round';
  }

  /** رسم شبكة توجيهية خفيفة */
  function _drawGrid() {
    if (!_canvas || !_ctx) return;
    const w = _canvas.getBoundingClientRect().width;
    const h = _canvas.getBoundingClientRect().height;

    // خلفية بيضاء
    _ctx.fillStyle = '#fffef8';
    _ctx.fillRect(0, 0, w, h);

    // شبكة
    _ctx.strokeStyle = '#e8e4d8';
    _ctx.lineWidth = 0.5;
    const step = 28;
    for (let x = step; x < w; x += step) {
      _ctx.beginPath(); _ctx.moveTo(x, 0); _ctx.lineTo(x, h); _ctx.stroke();
    }
    for (let y = step; y < h; y += step) {
      _ctx.beginPath(); _ctx.moveTo(0, y); _ctx.lineTo(w, y); _ctx.stroke();
    }

    // خط أساس وسطي
    _ctx.strokeStyle = '#c8d0f0';
    _ctx.lineWidth = 1;
    _ctx.setLineDash([6, 4]);
    _ctx.beginPath();
    _ctx.moveTo(0, h * 0.55);
    _ctx.lineTo(w, h * 0.55);
    _ctx.stroke();
    _ctx.setLineDash([]);
  }

  // ── أحداث الرسم ──
  function _onPointerDown(e) {
    e.preventDefault();
    _drawing = true;
    _points = [];

    const rect = _canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    _points.push({ x, y });

    _ctx.beginPath();
    _ctx.moveTo(x, y);

    if (_eraserMode) {
      _ctx.globalCompositeOperation = 'destination-out';
      _ctx.lineWidth = _penSize * 5;
    } else {
      _ctx.globalCompositeOperation = 'source-over';
      _ctx.strokeStyle = _penColor;
      _ctx.lineWidth = _penSize;
    }
  }

  function _onPointerMove(e) {
    if (!_drawing) return;
    e.preventDefault();

    const rect = _canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    _points.push({ x, y });

    // رسم سلس باستخدام quadratic curves
    if (_points.length >= 3) {
      const len = _points.length;
      const p0 = _points[len - 3];
      const p1 = _points[len - 2];
      const p2 = _points[len - 1];
      const mid = { x: (p1.x + p2.x) / 2, y: (p1.y + p2.y) / 2 };

      _ctx.beginPath();
      _ctx.moveTo((p0.x + p1.x) / 2, (p0.y + p1.y) / 2);
      _ctx.quadraticCurveTo(p1.x, p1.y, mid.x, mid.y);
      _ctx.stroke();
    } else {
      _ctx.lineTo(x, y);
      _ctx.stroke();
    }
  }

  function _onPointerUp(e) {
    if (!_drawing) return;
    _drawing = false;
    _ctx.globalCompositeOperation = 'source-over';
    _saveCanvasState();
    _redoStack = [];
    // إخفاء رسالة "ارسمي هنا"
    const hint = document.getElementById('me-draw-hint');
    if (hint && _undoStack.length > 1) hint.style.display = 'none';
  }

  // ── حفظ/استعادة الحالة ──
  function _saveCanvasState() {
    _undoStack.push(_canvas.toDataURL());
    if (_undoStack.length > 40) _undoStack.shift();
  }

  function _restoreState(dataUrl) {
    const img = new Image();
    img.onload = () => {
      _fitCanvas();
      const dpr = window.devicePixelRatio || 1;
      _ctx.drawImage(img, 0, 0, _canvas.width / dpr, _canvas.height / dpr);
    };
    img.src = dataUrl;
  }

  // ── أدوات الرسم ──
  function drawUndo() {
    if (_undoStack.length <= 1) return; // لا شيء للتراجع
    _redoStack.push(_undoStack.pop());
    _restoreState(_undoStack[_undoStack.length - 1]);
  }

  function drawRedo() {
    if (_redoStack.length === 0) return;
    const state = _redoStack.pop();
    _undoStack.push(state);
    _restoreState(state);
  }

  function drawClear() {
    _undoStack = [];
    _redoStack = [];
    _recognizedLatex = '';
    _fitCanvas();
    _drawGrid();
    _saveCanvasState();
    // إظهار رسالة "ارسمي هنا"
    const hint = document.getElementById('me-draw-hint');
    if (hint) hint.style.display = '';
    // مسح النتيجة
    const res = document.getElementById('me-draw-result');
    if (res) res.innerHTML = '';
    const btn = document.getElementById('me-draw-insert-btn');
    if (btn) btn.style.display = 'none';
  }

  function setDrawTool(tool) {
    _eraserMode = (tool === 'eraser');
    // تحديث الأزرار
    document.querySelectorAll('.me-dtool').forEach(b => b.classList.remove('active'));
    const active = document.querySelector(`.me-dtool[data-tool="${tool}"]`);
    if (active) active.classList.add('active');
  }

  // ── تحويل الرسم إلى صورة وعرض المعاينة ──
  function convertDrawing() {
    if (!_canvas) return;

    const resultEl  = document.getElementById('me-draw-result');
    const insertBtn = document.getElementById('me-draw-insert-btn');

    // رسم على canvas أبيض (بدون الشبكة) للحصول على صورة نظيفة
    const tempCanvas = document.createElement('canvas');
    const tempCtx = tempCanvas.getContext('2d');
    tempCanvas.width  = _canvas.width;
    tempCanvas.height = _canvas.height;
    tempCtx.fillStyle = '#ffffff';
    tempCtx.fillRect(0, 0, tempCanvas.width, tempCanvas.height);
    tempCtx.drawImage(_canvas, 0, 0);

    // حفظ الصورة كـ data URL
    _recognizedLatex = tempCanvas.toDataURL('image/png');

    // عرض المعاينة
    if (resultEl) {
      resultEl.innerHTML = `
        <div class="me-draw-success">
          <div class="me-draw-latex-label">معاينة الرسم:</div>
          <div style="text-align:center;padding:8px;background:#fff;border-radius:8px;border:1px solid #ddd">
            <img src="${_recognizedLatex}" style="max-width:100%;max-height:120px;image-rendering:auto" alt="رسم المعادلة">
          </div>
        </div>
      `;
    }
    if (insertBtn) insertBtn.style.display = '';
  }

  /** إدراج صورة الرسم في الحقل المستهدف */
  function insertFromDraw() {
    if (!_recognizedLatex) return;
    if (_activeFieldId) {
      const el = document.getElementById(_activeFieldId);
      if (el) {
        if (el.contentEditable === 'true') {
          // إدراج كصورة داخل المحتوى
          const img = `<img src="${_recognizedLatex}" class="math-drawn-img" style="max-height:60px;vertical-align:middle;margin:0 4px" alt="معادلة مرسومة"> `;
          el.focus();
          document.execCommand('insertHTML', false, img);
        } else {
          // حقل عادي — إدراج الـ data URL كنص (يُستخدم لاحقاً)
          const start = el.selectionStart || el.value.length;
          const end   = el.selectionEnd   || el.value.length;
          const tag = `[IMG:${_recognizedLatex}]`;
          el.value = el.value.slice(0, start) + tag + el.value.slice(end);
          el.dispatchEvent(new Event('input', { bubbles: true }));
        }
      }
    }
    close();
  }

  /** الحصول على CSRF token */
  function _getCSRF() {
    const cookie = document.cookie.split(';').find(c => c.trim().startsWith('csrftoken='));
    if (cookie) return cookie.split('=')[1];
    const meta = document.querySelector('meta[name="csrf-token"]');
    if (meta) return meta.content;
    const inp = document.querySelector('[name=csrfmiddlewaretoken]');
    if (inp) return inp.value;
    return '';
  }

  function _escHtml(s) {
    const d = document.createElement('div');
    d.textContent = s;
    return d.innerHTML;
  }

  // ── تبديل التبويبات ──
  function _switchTab(tab) {
    _activeTab = tab;
    document.querySelectorAll('.me-tab').forEach(b => b.classList.toggle('active', b.dataset.tab === tab));
    document.querySelectorAll('.me-tab-panel').forEach(p => p.classList.toggle('active', p.dataset.panel === tab));

    if (tab === 'draw') {
      // تهيئة Canvas عند أول فتح
      setTimeout(() => {
        if (!_canvas) _initCanvas();
        else { _fitCanvas(); _restoreState(_undoStack[_undoStack.length - 1]); }
      }, 100);
    } else if (tab === 'keyboard') {
      setTimeout(() => {
        const mf = document.getElementById('me-mathlive');
        if (mf && mf.focus) mf.focus();
      }, 100);
    }
  }

  // ═══════════════════════════════════════════
  //  إنشاء HTML النافذة المنبثقة
  // ═══════════════════════════════════════════

  function _buildModal() {
    if (document.getElementById('me-modal')) return;

    const modal = document.createElement('div');
    modal.id = 'me-modal';
    modal.className = 'me-modal';
    modal.innerHTML = `
      <div class="me-modal-content">

        <!-- ── Header + Tabs ── -->
        <div class="me-header">
          <div class="me-tabs-row">
            <button type="button" class="me-tab active" data-tab="keyboard"
                    onclick="MathEditor._switchTab('keyboard')">⌨️ لوحة المفاتيح</button>
            <button type="button" class="me-tab" data-tab="draw"
                    onclick="MathEditor._switchTab('draw')">✏️ رسم باللمس</button>
          </div>
          <button type="button" class="me-close" onclick="MathEditor.close()">✕</button>
        </div>

        <!-- ══ تبويب لوحة المفاتيح ══ -->
        <div class="me-tab-panel active" data-panel="keyboard">
          <div class="me-body">
            <div class="me-tips">
              💡 <strong>اختصارات:</strong>
              <code>1/2</code> → كسر &bull;
              <code>sqrt 2</code> → جذر &bull;
              <code>x^2</code> → أس &bull;
              <code>pi</code> → π &bull;
              اضغطي <kbd>Space</kbd> بعد الكتابة
            </div>

            <math-field id="me-mathlive"
                        virtual-keyboard-mode="manual"
                        style="min-height:120px;font-size:22px;border:2px solid var(--border2,#cbd5e1);border-radius:10px;padding:16px;background:white;color:#0f172a;direction:ltr">
            </math-field>

            <div class="me-section-label">قوالب سريعة:</div>
            <div class="me-tpl-grid" id="me-templates"></div>

            <div class="me-section-label">معاينة:</div>
            <div class="me-preview" id="me-live-preview">
              <span class="me-placeholder">اكتبي في المحرر أعلاه...</span>
            </div>
          </div>

          <div class="me-footer">
            <div class="me-footer-alt">
              <div class="me-section-label" style="margin:0">أو الصقي كود LaTeX:</div>
              <input type="text" id="me-latex-input" class="me-latex-input"
                     placeholder="مثال: \\\\frac{3}{4}" dir="ltr"
                     oninput="MathEditor._previewLatexInput()">
            </div>
            <div class="me-footer-btns">
              <button type="button" class="me-btn me-btn-secondary" onclick="MathEditor.close()">إلغاء</button>
              <button type="button" class="me-btn me-btn-primary" onclick="MathEditor.insert()">✅ إدراج المعادلة</button>
            </div>
          </div>
        </div>

        <!-- ══ تبويب الرسم باللمس ══ -->
        <div class="me-tab-panel" data-panel="draw">
          <div class="me-body me-draw-body">

            <!-- شريط أدوات الرسم -->
            <div class="me-draw-toolbar">
              <button type="button" class="me-dtool active" data-tool="pen"
                      onclick="MathEditor.setDrawTool('pen')" title="قلم">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 3a2.85 2.85 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/></svg>
              </button>
              <button type="button" class="me-dtool" data-tool="eraser"
                      onclick="MathEditor.setDrawTool('eraser')" title="ممحاة">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m7 21-4.3-4.3c-1-1-1-2.5 0-3.4l9.6-9.6c1-1 2.5-1 3.4 0l5.6 5.6c1 1 1 2.5 0 3.4L13 21"/><path d="M22 21H7"/><path d="m5 11 9 9"/></svg>
              </button>
              <div class="me-dtool-sep"></div>
              <button type="button" class="me-dtool" onclick="MathEditor.drawUndo()" title="تراجع">↩</button>
              <button type="button" class="me-dtool" onclick="MathEditor.drawRedo()" title="إعادة">↪</button>
              <button type="button" class="me-dtool" onclick="MathEditor.drawClear()" title="مسح الكل">🗑️</button>
              <div class="me-dtool-sep"></div>
              <label class="me-size-label" title="سمك القلم">
                <span>رفيع</span>
                <input type="range" id="me-pen-size" min="1" max="8" value="3" class="me-size-slider">
                <span>سميك</span>
              </label>
            </div>

            <!-- منطقة الرسم -->
            <div class="me-canvas-wrap">
              <canvas id="me-draw-canvas"></canvas>
              <div class="me-draw-hint" id="me-draw-hint">✏️ ارسمي المعادلة هنا بالإصبع أو القلم</div>
            </div>

            <!-- زر التحويل -->
            <div class="me-draw-actions">
              <button type="button" class="me-btn me-btn-convert" id="me-draw-convert-btn"
                      onclick="MathEditor.convertDrawing()">✅ جاهز — معاينة الرسم</button>
            </div>

            <!-- النتيجة -->
            <div id="me-draw-result"></div>
          </div>

          <div class="me-footer">
            <div class="me-footer-btns">
              <button type="button" class="me-btn me-btn-secondary" onclick="MathEditor.close()">إلغاء</button>
              <button type="button" class="me-btn me-btn-primary" id="me-draw-insert-btn"
                      style="display:none" onclick="MathEditor.insertFromDraw()">📌 إدراج الرسم</button>
            </div>
          </div>
        </div>

      </div>
    `;
    document.body.appendChild(modal);
    _modalEl = modal;

    // بناء أزرار القوالب
    const tplGrid = document.getElementById('me-templates');
    TEMPLATES.forEach(t => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'me-tpl-btn';
      btn.textContent = t.label;
      btn.onclick = () => _setMathLive(t.latex);
      tplGrid.appendChild(btn);
    });

    // ربط MathLive
    setTimeout(() => {
      _mlField = document.getElementById('me-mathlive');
      if (_mlField) {
        _mlField.addEventListener('input', _updateModalPreview);
      }
    }, 200);
  }

  // ═══════════════════════════════════════════
  //  شريط الرموز (للحقول)
  // ═══════════════════════════════════════════

  function buildSymbolBar(containerId, fieldId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const tabs = document.createElement('div');
    tabs.className = 'me-sym-tabs';
    const tabNames = [
      {key:'arabic', label:'عربية'},
      {key:'operators', label:'عمليات'},
      {key:'greek', label:'يونانية'},
      {key:'geometry', label:'هندسة'},
      {key:'relations', label:'علاقات'}
    ];

    tabNames.forEach((tn, i) => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'me-sym-tab' + (i === 0 ? ' on' : '');
      btn.textContent = tn.label;
      btn.dataset.tab = tn.key;
      btn.onclick = () => {
        container.querySelectorAll('.me-sym-tab').forEach(b => b.classList.remove('on'));
        btn.classList.add('on');
        container.querySelectorAll('.me-sym-grid').forEach(g => g.style.display = 'none');
        const grid = container.querySelector(`[data-symbols="${tn.key}"]`);
        if (grid) grid.style.display = 'flex';
      };
      tabs.appendChild(btn);
    });
    container.appendChild(tabs);

    tabNames.forEach((tn, i) => {
      const grid = document.createElement('div');
      grid.className = 'me-sym-grid';
      grid.dataset.symbols = tn.key;
      grid.style.display = i === 0 ? 'flex' : 'none';

      (SYMBOLS[tn.key] || []).forEach(sym => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'me-sym-btn' + (tn.key === 'arabic' ? ' arabic' : '');
        btn.textContent = sym.s;
        btn.title = sym.t;
        btn.onclick = () => insertSymbol(sym.s, fieldId);
        grid.appendChild(btn);
      });
      container.appendChild(grid);
    });
  }

  // ═══════════════════════════════════════════
  //  إدراج في الحقول
  // ═══════════════════════════════════════════

  function insertSymbol(sym, fieldId) {
    const el = document.getElementById(fieldId);
    if (!el) return;
    el.focus();
    document.execCommand('insertText', false, sym);
    _triggerPreview(fieldId);
  }

  function insertText(text, fieldId) {
    const el = document.getElementById(fieldId);
    if (!el) return;
    el.focus();
    if (el.contentEditable === 'true') {
      document.execCommand('insertText', false, text);
    } else {
      const start = el.selectionStart || 0;
      const end   = el.selectionEnd   || 0;
      el.value = el.value.slice(0, start) + text + el.value.slice(end);
      el.selectionStart = el.selectionEnd = start + text.length;
    }
    _triggerPreview(fieldId);
  }

  // ═══════════════════════════════════════════
  //  فتح / إغلاق / إدراج
  // ═══════════════════════════════════════════

  function openFor(fieldId) {
    // لا نمنع الفتح حتى لو MathLive لم يحمّل — النافذة تفتح مع LaTeX والرموز
    if (!customElements.get('math-field')) {
      console.warn('⏳ MathLive not loaded yet — modal will open without visual editor');
    }
    _activeFieldId = fieldId;
    _buildModal();

    // إعادة ضبط
    const ml = document.getElementById('me-mathlive');
    if (ml && ml.setValue) {
      setTimeout(() => ml.setValue(''), 50);
    }
    const li = document.getElementById('me-latex-input');
    if (li) li.value = '';
    const lp = document.getElementById('me-live-preview');
    if (lp) lp.innerHTML = '<span class="me-placeholder">اكتبي في المحرر أعلاه...</span>';

    // إعادة ضبط تبويب الرسم
    _recognizedLatex = '';
    const res = document.getElementById('me-draw-result');
    if (res) res.innerHTML = '';
    const dib = document.getElementById('me-draw-insert-btn');
    if (dib) dib.style.display = 'none';

    // فتح على تبويب لوحة المفاتيح
    _activeTab = 'keyboard';
    _switchTab('keyboard');

    // إظهار النافذة
    _modalEl.classList.add('show');

    setTimeout(() => {
      const mf = document.getElementById('me-mathlive');
      if (mf && mf.focus) mf.focus();
    }, 150);
  }

  function close() {
    if (_modalEl) _modalEl.classList.remove('show');
  }

  function insert() {
    let latex = '';
    const ml = document.getElementById('me-mathlive');
    if (ml) {
      latex = (ml.getValue && ml.getValue('latex')) || ml.value || '';
    }
    if (!latex.trim()) {
      latex = (document.getElementById('me-latex-input').value || '').trim();
    }
    if (!latex.trim()) {
      alert('اكتبي معادلة في المحرر أولاً');
      return;
    }

    const wrapped = ` $${latex}$ `;

    if (_activeFieldId) {
      const el = document.getElementById(_activeFieldId);
      if (el) {
        el.focus();
        if (el.contentEditable === 'true') {
          document.execCommand('insertText', false, wrapped);
        } else {
          const start = el.selectionStart || el.value.length;
          const end   = el.selectionEnd   || el.value.length;
          el.value = el.value.slice(0, start) + wrapped + el.value.slice(end);
          el.selectionStart = el.selectionEnd = start + wrapped.length;
          el.dispatchEvent(new Event('input', { bubbles: true }));
        }
      }
    }

    close();
    _triggerPreview(_activeFieldId);
  }

  // ═══════════════════════════════════════════
  //  MathLive / المعاينة
  // ═══════════════════════════════════════════

  function _setMathLive(latex) {
    const ml = document.getElementById('me-mathlive');
    if (ml && ml.setValue) {
      ml.setValue(latex);
      _updateModalPreview();
    }
  }

  function _updateModalPreview() {
    const ml = document.getElementById('me-mathlive');
    const prev = document.getElementById('me-live-preview');
    if (!ml || !prev) return;

    let latex = '';
    if (ml.getValue) latex = ml.getValue('latex') || '';
    else latex = ml.value || '';

    if (!latex.trim()) {
      prev.innerHTML = '<span class="me-placeholder">اكتبي في المحرر أعلاه...</span>';
      return;
    }

    prev.innerHTML = `\\(${latex}\\)`;
    if (window.MathJax && MathJax.typesetPromise) {
      MathJax.typesetPromise([prev]).catch(() => {});
    }
  }

  function _previewLatexInput() {
    const inp = document.getElementById('me-latex-input');
    const prev = document.getElementById('me-live-preview');
    if (!inp || !prev) return;

    const latex = inp.value.trim();
    if (!latex) {
      prev.innerHTML = '<span class="me-placeholder">اكتبي في المحرر أعلاه...</span>';
      return;
    }

    prev.innerHTML = `\\(${latex}\\)`;
    if (window.MathJax && MathJax.typesetPromise) {
      MathJax.typesetPromise([prev]).catch(() => {});
    }

    const ml = document.getElementById('me-mathlive');
    if (ml && ml.setValue) {
      try { ml.setValue(latex); } catch(e) {}
    }
  }

  function _triggerPreview(fieldId) {
    if (!fieldId) return;
    const previewId = fieldId + '-preview';
    const prev = document.getElementById(previewId);
    if (!prev) return;

    clearTimeout(_previewTimers[fieldId]);
    _previewTimers[fieldId] = setTimeout(() => {
      const el = document.getElementById(fieldId);
      if (!el) return;

      const text = el.contentEditable === 'true' ? (el.innerText || '') : (el.value || '');
      if (!text.trim()) {
        prev.innerHTML = '<span class="me-placeholder">ستظهر المعادلات هنا تلقائياً...</span>';
        return;
      }

      prev.textContent = text;
      if (window.MathJax && MathJax.typesetPromise) {
        MathJax.typesetPromise([prev]).catch(() => {});
      }
    }, 500);
  }

  // ═══════════════════════════════════════════
  //  أدوات عامة
  // ═══════════════════════════════════════════

  function refreshAll() {
    if (window.MathJax && MathJax.typesetPromise) {
      MathJax.typesetPromise().catch(() => {});
    }
  }

  function syncField(editableId, hiddenId) {
    const el = document.getElementById(editableId);
    const hidden = document.getElementById(hiddenId);
    if (el && hidden) {
      hidden.value = el.innerText || '';
    }
  }

  function loadIntoEditable(editableId, text) {
    const el = document.getElementById(editableId);
    if (el && text) {
      el.textContent = text;
      if (window.MathJax && MathJax.typesetPromise) {
        const previewId = editableId + '-preview';
        const prev = document.getElementById(previewId);
        if (prev) {
          prev.textContent = text;
          MathJax.typesetPromise([prev]).catch(() => {});
        }
      }
    }
  }

  function _bindEvents() {
    document.querySelectorAll('[data-me-field]').forEach(el => {
      el.addEventListener('input', () => {
        _triggerPreview(el.id);
      });
    });
  }

  function init() {
    if (_initialized) return;
    _initialized = true;

    if (!document.getElementById('me-styles')) {
      const style = document.createElement('style');
      style.id = 'me-styles';
      style.textContent = ME_CSS;
      document.head.appendChild(style);
    }

    _bindEvents();

    if (document.readyState === 'complete') {
      refreshAll();
    } else {
      window.addEventListener('load', () => setTimeout(refreshAll, 300));
    }
  }

  // ═══════════════════════════════════════════
  //  CSS
  // ═══════════════════════════════════════════

  const ME_CSS = `
/* ═══ Math Editor Modal ═══ */
.me-modal {
  display:none; position:fixed; inset:0; background:rgba(0,0,0,0.8);
  z-index:99999; align-items:center; justify-content:center;
  padding:16px; backdrop-filter:blur(6px);
}
.me-modal.show { display:flex; }

.me-modal-content {
  background:var(--card,#fff); border:1px solid var(--border2,#e2e8f0);
  border-radius:14px; width:100%; max-width:720px; max-height:92vh;
  display:flex; flex-direction:column; overflow:hidden;
  box-shadow: 0 20px 60px rgba(0,0,0,0.3);
}

/* ── Header + Tabs ── */
.me-header {
  padding:10px 16px; border-bottom:1px solid var(--border,#e2e8f0);
  background:var(--bg2,#f8fafc); display:flex; justify-content:space-between; align-items:center;
}
.me-tabs-row { display:flex; gap:4px; }
.me-tab {
  background:var(--card2,#f1f5f9); border:1px solid var(--border2,#cbd5e1);
  color:var(--text2,#64748b); font-family:'Tajawal',sans-serif; font-size:12px;
  font-weight:700; padding:6px 14px; border-radius:8px; cursor:pointer;
  transition:all 0.15s;
}
.me-tab:hover { background:var(--card3,#e2e8f0); }
.me-tab.active {
  background:linear-gradient(135deg, #7c3aed, #6366f1);
  color:white; border-color:transparent;
}

.me-close {
  background:var(--card2,#f1f5f9); border:1px solid var(--border,#e2e8f0);
  color:var(--text,#333); border-radius:7px; padding:4px 10px; cursor:pointer; font-size:14px;
}

/* ── Tab panels ── */
.me-tab-panel { display:none; flex-direction:column; flex:1; overflow:hidden; }
.me-tab-panel.active { display:flex; }

.me-body { padding:14px 16px; overflow-y:auto; flex:1; }

.me-tips {
  font-size:10px; color:var(--text2,#475569); line-height:1.8;
  background:var(--card2,#f1f5f9); padding:8px 12px; border-radius:8px;
  border-right:3px solid var(--purple,#7c3aed); margin-bottom:12px;
}
.me-tips code {
  background:var(--card3,#fff); padding:1px 5px; border-radius:3px;
  font-family:monospace; font-size:10px;
}
.me-tips kbd {
  background:var(--bg3,#e2e8f0); padding:1px 5px; border-radius:3px;
  font-family:monospace; font-size:9px; border:1px solid var(--border2,#cbd5e1);
}

.me-section-label {
  font-size:9px; color:var(--text3,#94a3b8); font-weight:600;
  margin:10px 0 6px; letter-spacing:0.3px;
}

.me-tpl-grid { display:flex; flex-wrap:wrap; gap:4px; margin-bottom:8px; }
.me-tpl-btn {
  background:var(--card2,#f1f5f9); border:1px solid var(--border2,#cbd5e1);
  color:var(--text2,#475569); font-family:'Tajawal',sans-serif; font-size:9px;
  padding:4px 9px; border-radius:5px; cursor:pointer; transition:all 0.15s; white-space:nowrap;
}
.me-tpl-btn:hover {
  background:rgba(155,114,245,0.1); color:var(--purple,#7c3aed);
  border-color:rgba(155,114,245,0.3);
}

.me-preview {
  background:var(--card2,#f8fafc); border:1px solid var(--border2,#e2e8f0);
  border-radius:8px; padding:10px 14px; min-height:42px;
  display:flex; align-items:center; justify-content:center;
  font-size:16px; direction:rtl;
}

.me-footer {
  padding:10px 16px; border-top:1px solid var(--border,#e2e8f0);
  background:var(--bg2,#f8fafc);
}
.me-footer-alt {
  display:flex; align-items:center; gap:8px; margin-bottom:8px;
}
.me-latex-input {
  flex:1; background:var(--card2,#f1f5f9); border:1px solid var(--border2,#cbd5e1);
  color:var(--text,#333); font-family:'Courier New',monospace; font-size:11px;
  padding:7px 10px; border-radius:6px; outline:none;
}
.me-latex-input:focus { border-color:var(--purple,#7c3aed); }

.me-footer-btns { display:flex; gap:8px; justify-content:flex-end; }
.me-btn {
  font-family:'Tajawal',sans-serif; font-size:11px; font-weight:700;
  padding:8px 16px; border-radius:8px; cursor:pointer; border:none; transition:all 0.15s;
}
.me-btn-primary {
  background:linear-gradient(135deg, var(--green,#059669), var(--blue,#2563eb));
  color:white;
}
.me-btn-primary:hover { opacity:0.9; transform:translateY(-1px); }
.me-btn-secondary {
  background:var(--card2,#f1f5f9); color:var(--text2,#475569);
  border:1px solid var(--border2,#cbd5e1);
}
.me-btn-convert {
  background:linear-gradient(135deg, #f59e0b, #d97706);
  color:white; font-size:13px; padding:10px 24px;
}
.me-btn-convert:hover { opacity:0.9; transform:translateY(-1px); }
.me-btn-convert:disabled { opacity:0.5; cursor:wait; }

.me-placeholder { color:var(--text3,#94a3b8); font-size:11px; }

/* ═══ Drawing Canvas Tab ═══ */
.me-draw-body { padding:10px 14px; }

.me-draw-toolbar {
  display:flex; align-items:center; gap:4px; flex-wrap:wrap;
  padding:8px 10px; background:var(--card2,#f1f5f9);
  border:1px solid var(--border2,#e2e8f0); border-radius:10px;
  margin-bottom:8px;
}
.me-dtool {
  background:white; border:1px solid var(--border2,#cbd5e1);
  color:var(--text2,#475569); width:36px; height:34px; border-radius:7px;
  cursor:pointer; display:flex; align-items:center; justify-content:center;
  font-size:15px; transition:all 0.12s;
}
.me-dtool:hover { background:var(--card3,#e2e8f0); }
.me-dtool.active {
  background:var(--purple,#7c3aed); color:white;
  border-color:var(--purple,#7c3aed);
}
.me-dtool-sep { width:1px; height:24px; background:var(--border2,#cbd5e1); margin:0 4px; }

.me-size-label {
  display:flex; align-items:center; gap:4px; font-size:9px;
  color:var(--text3,#94a3b8); cursor:default;
}
.me-size-slider {
  width:70px; height:4px; accent-color:var(--purple,#7c3aed);
  cursor:pointer;
}

.me-canvas-wrap {
  position:relative; border:2px solid var(--border2,#cbd5e1);
  border-radius:12px; overflow:hidden; background:#fffef8;
}
#me-draw-canvas {
  display:block; width:100%; height:240px; cursor:crosshair;
}
.me-draw-hint {
  position:absolute; inset:0; display:flex; align-items:center;
  justify-content:center; font-size:14px; color:var(--text3,#b0b8c8);
  pointer-events:none; font-family:'Tajawal',sans-serif;
}

.me-draw-actions {
  display:flex; justify-content:center; margin:10px 0 6px;
}

/* Results */
.me-draw-success {
  background:var(--card2,#f0fdf4); border:1px solid #86efac;
  border-radius:10px; padding:10px 14px;
}
.me-draw-latex-label {
  font-size:9px; color:var(--text3,#94a3b8); font-weight:600; margin-bottom:2px;
}
.me-draw-latex-code {
  font-family:'Courier New',monospace; font-size:12px; color:#1e293b;
  background:white; padding:6px 10px; border-radius:6px;
  border:1px solid #e2e8f0; margin-bottom:8px; word-break:break-all;
}
.me-draw-latex-preview {
  font-size:18px; text-align:center; padding:8px;
  background:white; border-radius:6px; border:1px solid #e2e8f0;
}
.me-draw-error {
  background:#fef2f2; border:1px solid #fca5a5; border-radius:10px;
  padding:10px 14px; color:#991b1b; font-size:12px; text-align:center;
}
.me-draw-info {
  background:#fffbeb; border:1px solid #fcd34d; border-radius:10px;
  padding:12px 14px; color:#92400e; font-size:12px; text-align:center; line-height:1.8;
}
.me-draw-info code { background:white; padding:1px 5px; border-radius:3px; font-size:10px; }

.me-loading {
  text-align:center; padding:16px; color:var(--text2,#64748b); font-size:13px;
  display:flex; align-items:center; justify-content:center; gap:8px;
}
.me-spinner {
  width:20px; height:20px; border:3px solid var(--border2,#e2e8f0);
  border-top-color:var(--purple,#7c3aed); border-radius:50%;
  animation:me-spin 0.7s linear infinite;
}
@keyframes me-spin { to { transform:rotate(360deg); } }

/* ═══ Symbol Bar (inline in fields) ═══ */
.me-sym-tabs { display:flex; gap:3px; margin-bottom:6px; flex-wrap:wrap; }
.me-sym-tab {
  background:none; border:1px solid var(--border2,#cbd5e1); color:var(--text3,#94a3b8);
  font-family:'Tajawal',sans-serif; font-size:9px; padding:3px 8px;
  border-radius:5px; cursor:pointer; transition:all 0.15s;
}
.me-sym-tab.on {
  background:rgba(155,114,245,0.1); color:var(--purple,#7c3aed);
  border-color:rgba(155,114,245,0.3);
}

.me-sym-grid { display:flex; flex-wrap:wrap; gap:3px; }
.me-sym-btn {
  background:var(--card2,#f1f5f9); border:1px solid var(--border2,#cbd5e1);
  color:var(--text2,#475569); font-size:13px; width:34px; height:30px;
  border-radius:5px; cursor:pointer; display:flex; align-items:center;
  justify-content:center; transition:all 0.15s; font-family:'Tajawal',monospace;
}
.me-sym-btn:hover {
  background:var(--card3,#e2e8f0); color:var(--purple,#7c3aed);
  border-color:rgba(155,114,245,0.3); transform:scale(1.08);
}
.me-sym-btn.arabic { font-size:14px; font-weight:700; color:var(--teal,#0d9488); }

.me-quick-bar {
  display:flex; gap:3px; flex-wrap:wrap; align-items:center; padding:3px 0;
}
.me-quick-btn {
  background:none; border:1px solid var(--border2,#cbd5e1); color:var(--text2,#475569);
  font-size:11px; width:26px; height:24px; border-radius:4px; cursor:pointer;
  display:flex; align-items:center; justify-content:center; transition:all 0.12s;
}
.me-quick-btn:hover { background:rgba(155,114,245,0.1); color:var(--purple,#7c3aed); }
.me-quick-btn.math-open {
  color:var(--purple,#7c3aed); font-weight:700; font-size:12px; width:auto; padding:0 8px;
  background:rgba(155,114,245,0.08); border-color:rgba(155,114,245,0.25);
}

/* ═══ Responsive ═══ */
@media (max-width:600px) {
  .me-modal-content { max-height:95vh; border-radius:10px; }
  .me-body { padding:10px 12px; }
  #me-mathlive { min-height:80px !important; font-size:18px !important; padding:10px !important; }
  .me-tpl-grid { gap:3px; }
  .me-tpl-btn { font-size:8px; padding:3px 6px; }
  .me-sym-btn { width:30px; height:28px; font-size:12px; }
  .me-footer-alt { flex-direction:column; }

  /* Canvas mobile */
  #me-draw-canvas { height:200px; }
  .me-draw-toolbar { padding:6px 8px; gap:3px; }
  .me-dtool { width:32px; height:30px; font-size:13px; }
  .me-size-slider { width:50px; }
  .me-tab { font-size:11px; padding:5px 10px; }
}

@media (min-width:601px) and (max-width:900px) {
  #me-draw-canvas { height:260px; }
}

@media (min-width:901px) {
  #me-draw-canvas { height:300px; }
}
`;

  // ─── Public API ───
  return {
    init,
    openFor,
    close,
    insert,
    insertFromDraw,
    insertSymbol,
    insertText,
    buildSymbolBar,
    syncField,
    loadIntoEditable,
    refreshAll,
    setDrawTool,
    drawUndo,
    drawRedo,
    drawClear,
    convertDrawing,
    _previewLatexInput,
    _switchTab,
    SYMBOLS,
    TEMPLATES
  };
})();

// تصدير MathEditor على window حتى يكون متاحاً لكل السكربتات
window.MathEditor = MathEditor;

// Auto-init when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => MathEditor.init());
} else {
  MathEditor.init();
}
