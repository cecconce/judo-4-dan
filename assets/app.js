(function(){
var base=document.body.dataset.base||'';
var d=document.getElementById('drawer'),s=document.getElementById('scrim'),b=document.getElementById('menu-btn');
function tog(o){d.classList.toggle('open',o);s.hidden=!o;b.setAttribute('aria-expanded',o)}
b.onclick=function(){tog(!d.classList.contains('open'))};s.onclick=function(){tog(false)};
var tb=document.getElementById('theme-btn');
tb.onclick=function(){var r=document.documentElement,cur=r.dataset.theme||(matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light');var n=cur==='dark'?'light':'dark';r.dataset.theme=n;try{localStorage.setItem('theme',n)}catch(e){}};
var q=document.getElementById('q');
if(q){
 var idx=null,res=document.getElementById('results');
 function norm(x){return x.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'')}
 function esc(x){return x.replace(/[&<>]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;'}[c]})}
 function run(){
  var v=norm(q.value.trim());res.innerHTML='';if(v.length<2||!idx)return;
  var words=v.split(/\s+/),out=[];
  idx.forEach(function(e){
   var hay=e._n;if(words.every(function(w){return hay.indexOf(w)>-1})){
    var score=(norm(e.s).indexOf(words[0])>-1?5:0)+(norm(e.ct).indexOf(words[0])>-1?2:0);out.push([score,e]);}
  });
  out.sort(function(a,b){return b[0]-a[0]});
  out.slice(0,30).forEach(function(p){
   var e=p[1],pos=e._n.indexOf(words[0]);var raw=e.t;var st=Math.max(0,pos-60);
   var sn=esc(raw.substr(st,170));
   words.forEach(function(w){sn=sn.replace(new RegExp('('+w.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')+')','ig'),'<mark>$1</mark>')});
   var li=document.createElement('li');
   li.innerHTML='<a href="'+base+'c/'+e.c+'.html'+(e.id?'#'+e.id:'')+'"><b>'+esc(e.s||e.ct)+'</b><small>'+esc(e.ct)+'</small>'+(st>0?'…':'')+sn+'…</a>';
   res.appendChild(li)});
  if(!out.length)res.innerHTML='<li>Nessun risultato.</li>';
 }
 fetch(base+'search.json').then(function(r){return r.json()}).then(function(j){idx=j;idx.forEach(function(e){e._n=norm(e.s+' '+e.t)});run()});
 q.addEventListener('input',run);
 if(location.hash==='#cerca')q.focus();
}
if('serviceWorker' in navigator){addEventListener('load',function(){navigator.serviceWorker.register(base+'sw.js').catch(function(){})})}
})();
