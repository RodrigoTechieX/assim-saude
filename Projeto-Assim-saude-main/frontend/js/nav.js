document.addEventListener('DOMContentLoaded', function(){
  const btn = document.getElementById('nav-toggle');
  const nav = document.querySelector('.nav');

  if(btn && nav){
    btn.addEventListener('click', () => {
      nav.classList.toggle('show');
      btn.setAttribute('aria-expanded', nav.classList.contains('show'));
    });

    // fecha o menu ao clicar em link (mobile)
    nav.querySelectorAll('a').forEach(a => a.addEventListener('click', () => {
      if(nav.classList.contains('show')) nav.classList.remove('show');
    }));
  }

  // marca link ativo baseado no pathname
  const path = window.location.pathname.split('/').pop();
  document.querySelectorAll('.nav a').forEach(a => {
    const href = a.getAttribute('href').split('/').pop();
    if(href === path || (href === 'index.html' && path === '')) a.classList.add('active');
  });
});
