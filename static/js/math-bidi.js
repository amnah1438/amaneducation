/**
 * Math Bidi — يضمن عرض المعادلات الرياضية ($...$) بالاتجاه الصحيح (LTR)
 * حتى عندما تكون مدمجة في نص عربي (RTL).
 *
 * الاستخدام: ضع class="math-aware" على أي عنصر يحوي معادلات.
 * المكتبة تعمل تلقائياً عند تحميل الصفحة.
 */
(function(){
  const AR_TO_LA = {'٠':'0','١':'1','٢':'2','٣':'3','٤':'4','٥':'5','٦':'6','٧':'7','٨':'8','٩':'9','۰':'0','۱':'1','۲':'2','۳':'3','۴':'4','۵':'5','۶':'6','۷':'7','۸':'8','۹':'9'};

  function normalizeMath(text){
    return String(text).replace(/\$([^$]+)\$/g, (m, inner) => {
      let s = inner;
      // الأرقام العربية → لاتينية
      s = [...s].map(ch => AR_TO_LA[ch] || ch).join('');
      // / → \ في حال كتبتْ المعلمة slash بالخطأ
      s = s.replace(/\/(?=[a-z])/gi, '\\');
      // sqrt/frac بدون backslash → معها
      s = s.replace(/(?<![\\])\bsqrt\b/g, '\\sqrt');
      s = s.replace(/(?<![\\])\bfrac\b/g, '\\frac');
      return '$' + s + '$';
    });
  }

  function processElement(el){
    if (el.dataset.processed) return;
    const original = el.textContent || '';
    const normalized = normalizeMath(original);
    let safe = '';
    let i = 0;
    while (i < normalized.length) {
      if (normalized[i] === '$') {
        const end = normalized.indexOf('$', i + 1);
        if (end > i) {
          safe += '<span class="math-ltr" style="unicode-bidi:isolate;direction:ltr;display:inline-block">' + normalized.slice(i, end + 1) + '</span>';
          i = end + 1; continue;
        }
      }
      const c = normalized[i];
      safe += (c === '<' ? '&lt;' : c === '>' ? '&gt;' : c === '&' ? '&amp;' : c);
      i++;
    }
    el.innerHTML = safe;
    el.dataset.processed = '1';
  }

  function run(){
    document.querySelectorAll('.math-aware').forEach(processElement);
    if (window.MathJax && window.MathJax.typesetPromise) {
      window.MathJax.typesetPromise().catch(()=>{});
    }
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', run);
  else run();

  window.amaneducProcessMath = run;
})();
