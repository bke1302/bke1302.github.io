// FlowOps AI - shared JS for content pages: mobile nav + FAQ accordion
(function(){
  var t=document.getElementById('navtoggle'),l=document.getElementById('navlinks');
  if(t&&l){t.addEventListener('click',function(){var o=l.classList.toggle('open');t.classList.toggle('open',o);t.setAttribute('aria-expanded',o);});}
  document.querySelectorAll('.faq-q').forEach(function(q){
    q.addEventListener('click',function(){
      var it=q.closest('.faq-item');var open=it.classList.toggle('open');
      q.setAttribute('aria-expanded',open);
    });
  });

  // ===== Accessibility widget =====
  (function(){
    var root=document.documentElement;
    var btn=document.getElementById('accBtn'),panel=document.getElementById('accPanel'),x=document.getElementById('accClose');
    if(!btn||!panel) return;
    var KEY='flowops-a11y',fs=0;
    var FLAGS=['acc-contrast','acc-gray','acc-links','acc-readable','acc-nomotion'];
    var applyFs=function(){document.body.style.zoom = fs? String(1+fs*0.12):'';};
    var sync=function(){panel.querySelectorAll('[data-cls]').forEach(function(b){b.classList.toggle('active',root.classList.contains(b.dataset.cls));});};
    var save=function(){try{var s={fs:fs};FLAGS.forEach(function(f){s[f]=root.classList.contains(f);});localStorage.setItem(KEY,JSON.stringify(s));}catch(e){}};
    var openP=function(o){panel.classList.toggle('open',o);btn.setAttribute('aria-expanded',o?'true':'false');};
    btn.addEventListener('click',function(){openP(!panel.classList.contains('open'));});
    if(x) x.addEventListener('click',function(){openP(false);btn.focus();});
    document.addEventListener('keydown',function(e){if(e.key==='Escape'&&panel.classList.contains('open')){openP(false);btn.focus();}});
    panel.querySelector('[data-act=fsplus]').addEventListener('click',function(){fs=Math.min(fs+1,4);applyFs();save();});
    panel.querySelector('[data-act=fsminus]').addEventListener('click',function(){fs=Math.max(fs-1,0);applyFs();save();});
    panel.querySelectorAll('[data-cls]').forEach(function(b){b.addEventListener('click',function(){root.classList.toggle(b.dataset.cls);b.classList.toggle('active');save();});});
    panel.querySelector('[data-act=reset]').addEventListener('click',function(){fs=0;applyFs();FLAGS.forEach(function(f){root.classList.remove(f);});sync();save();});
    try{var s=JSON.parse(localStorage.getItem(KEY));if(s){fs=s.fs||0;applyFs();FLAGS.forEach(function(f){root.classList.toggle(f,!!s[f]);});sync();}}catch(e){}
  })();

  // ===== Modals (accessibility statement + privacy) =====
  function bindModal(modalId,linkId,closeId){
    var m=document.getElementById(modalId),open=document.getElementById(linkId),close=document.getElementById(closeId);
    if(!m||!open) return;
    open.addEventListener('click',function(e){e.preventDefault();m.classList.add('open');});
    if(close) close.addEventListener('click',function(){m.classList.remove('open');});
    m.addEventListener('click',function(e){if(e.target===m)m.classList.remove('open');});
    document.addEventListener('keydown',function(e){if(e.key==='Escape')m.classList.remove('open');});
  }
  bindModal('accStatement','accStatementLink','accStatementClose');
  bindModal('privacy','privacyLink','privacyClose');

  // ===== Back to top =====
  (function(){
    var b=document.getElementById('toTop'); if(!b) return;
    addEventListener('scroll',function(){b.classList.toggle('show',scrollY>600);},{passive:true});
    b.addEventListener('click',function(){scrollTo({top:0,behavior:'smooth'});});
  })();
})();
