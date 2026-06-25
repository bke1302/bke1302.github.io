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
})();
