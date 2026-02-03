document.addEventListener('DOMContentLoaded', () => {
  const hamburger = document.getElementById('hamburger');
  const overlay = document.getElementById('navOverlay');
  const navClose = document.getElementById('navClose');
  // support multiple toggles (desktop + drawer)
  const themeToggles = Array.from(document.querySelectorAll('.theme-toggle'));

  // Menu handlers
  function openMenu(){
    overlay.classList.add('open');
    hamburger.setAttribute('aria-expanded', 'true');
    overlay.setAttribute('aria-hidden', 'false');
  }
  function closeMenu(){
    overlay.classList.remove('open');
    hamburger.setAttribute('aria-expanded', 'false');
    overlay.setAttribute('aria-hidden', 'true');
  }

  hamburger && hamburger.addEventListener('click', () => {
    const expanded = hamburger.getAttribute('aria-expanded') === 'true';
    if(expanded) closeMenu(); else openMenu();
  });
  navClose && navClose.addEventListener('click', closeMenu);
  overlay && overlay.addEventListener('click', (e)=>{ if(e.target === overlay) closeMenu(); });
  document.addEventListener('keydown', (e)=>{ if(e.key === 'Escape') closeMenu(); });

  // Theme handlers
  function applyTheme(theme){
    if(theme === 'dark') document.body.classList.add('dark'); else document.body.classList.remove('dark');
    // Update all toggles to reflect the state
    themeToggles.forEach(t => t.setAttribute('aria-pressed', theme === 'dark' ? 'true' : 'false'));
  }

  function loadTheme(){
    try{
      const stored = localStorage.getItem('theme');
      if(stored) return stored;
    }catch(e){}
    // Default: use prefers-color-scheme
    const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    return prefersDark ? 'dark' : 'light';
  }

  // Initialize theme
  const initialTheme = loadTheme();
  applyTheme(initialTheme);

  // Toggle theme on click for all toggles
  themeToggles.forEach(tt => tt.addEventListener('click', ()=>{
    const now = document.body.classList.contains('dark') ? 'light' : 'dark';
    applyTheme(now);
    try{ localStorage.setItem('theme', now); }catch(e){}
  }));
});