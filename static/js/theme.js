/**
 * نظام تبديل الوضع (Dark/Light) موحَّد لكل لوحات المنصة.
 * يستعمل CSS variables ضمن :root[data-theme="..."]
 * يحفظ التفضيل في localStorage تحت المفتاح "amaneduc-theme".
 *
 * الاستخدام في القالب:
 *   <html lang="ar" dir="rtl" data-theme="dark">
 *   <body>
 *     <button id="themeToggle" class="theme-fab">🌙</button>
 *     <script src="{% static 'js/theme.js' %}"></script>
 */
(function(){
  const KEY = 'amaneduc-theme';
  const html = document.documentElement;
  const saved = localStorage.getItem(KEY) || (html.getAttribute('data-theme') || 'dark');
  html.setAttribute('data-theme', saved);

  function setIcon(theme){
    const btns = document.querySelectorAll('#themeToggle, .theme-toggle-btn, [data-theme-toggle]');
    btns.forEach(b => { b.textContent = (theme === 'dark') ? '☀️' : '🌙'; b.title = (theme === 'dark') ? 'الوضع الفاتح' : 'الوضع الداكن'; });
  }

  function apply(theme){
    html.setAttribute('data-theme', theme);
    localStorage.setItem(KEY, theme);
    setIcon(theme);
    // إعادة رسم Charts إن كانت موجودة
    if (typeof window.redrawAllCharts === 'function') {
      setTimeout(window.redrawAllCharts, 30);
    }
  }

  // ربط الأزرار عند تحميل الصفحة
  function attach(){
    setIcon(html.getAttribute('data-theme') || 'dark');
    document.querySelectorAll('#themeToggle, .theme-toggle-btn, [data-theme-toggle]').forEach(btn => {
      btn.addEventListener('click', () => {
        const cur = html.getAttribute('data-theme') || 'dark';
        apply(cur === 'dark' ? 'light' : 'dark');
      });
    });
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', attach);
  } else {
    attach();
  }

  // expose
  window.amaneducSetTheme = apply;
})();
