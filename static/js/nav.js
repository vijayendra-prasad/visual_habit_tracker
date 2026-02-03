document.addEventListener('DOMContentLoaded', () => {
  const hamburger = document.getElementById('hamburger');
  const overlay = document.getElementById('navOverlay');
  const navClose = document.getElementById('navClose');

  function openMenu(){
    overlay.classList.add('open');
    hamburger.setAttribute('aria-expanded', 'true');
    overlay.setAttribute('aria-hidden', 'false');
    // trap focus could be improved later
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

  // close on backdrop click
  overlay && overlay.addEventListener('click', (e)=>{
    if(e.target === overlay) closeMenu();
  });

  // close on Escape
  document.addEventListener('keydown', (e)=>{ if(e.key === 'Escape') closeMenu(); });
});