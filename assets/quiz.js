(function(){
var MAXQ=30,root=document.getElementById('quiz'),base=document.body.dataset.base||'';
var data=null,sel={},pool=[],cur=0,score=0,wrong=[],answered=false,session=[];
function esc(x){return String(x).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function shuffle(a){a=a.slice();for(var i=a.length-1;i>0;i--){var j=Math.floor(Math.random()*(i+1));var t=a[i];a[i]=a[j];a[j]=t}return a}
function avail(){var n=0;data.topics.forEach(function(t){if(sel[t.id])n+=t.n});return n}
function setup(keepN){
 var n0=keepN||10;
 var h='<h2>Scegli gli argomenti</h2><p class="qhint">Tocca per selezionare uno o più capitoli. Ogni domanda ha 4 risposte, una sola è corretta.</p>';
 h+='<div class="qtools"><button type="button" id="q-all">Tutti</button><button type="button" id="q-none">Nessuno</button></div><div class="qtopics">';
 data.topics.forEach(function(t){
  h+='<label class="qt'+(sel[t.id]?' on':'')+'"><input type="checkbox" data-id="'+t.id+'"'+(sel[t.id]?' checked':'')+'><span>'+esc(t.title)+'</span><small>'+t.n+'</small></label>';
 });
 h+='</div><h2>Numero di domande</h2><div class="qnum"><div class="qchips">';
 [5,10,15,20,25,30].forEach(function(n){h+='<button type="button" class="chip" data-n="'+n+'">'+n+'</button>'});
 h+='</div><label>oppure: <input id="q-n" type="number" min="1" max="'+MAXQ+'" value="'+n0+'" inputmode="numeric"></label></div>';
 h+='<p id="q-info" class="qhint"></p><button type="button" id="q-start" class="qgo">Inizia il quiz</button>';
 root.innerHTML=h;
 var num=document.getElementById('q-n'),info=document.getElementById('q-info'),go=document.getElementById('q-start');
 function refresh(){
  var a=avail(),v=parseInt(num.value,10)||0,cap=Math.min(MAXQ,a);
  if(v>cap){v=cap;num.value=cap}
  if(v<1&&a>0){v=1;num.value=1}
  num.max=Math.max(1,cap);
  Array.prototype.forEach.call(root.querySelectorAll('.chip'),function(c){var n=+c.dataset.n;c.classList.toggle('on',n===v);c.disabled=n>a});
  info.textContent=a?('Domande disponibili negli argomenti scelti: '+a+'. Massimo per quiz: '+MAXQ+'.'):'Seleziona almeno un argomento.';
  go.disabled=!a;
 }
 root.querySelectorAll('.qt input').forEach(function(i){i.onchange=function(){sel[i.dataset.id]=i.checked;i.parentNode.classList.toggle('on',i.checked);refresh()}});
 document.getElementById('q-all').onclick=function(){data.topics.forEach(function(t){sel[t.id]=true});setup(+num.value)};
 document.getElementById('q-none').onclick=function(){sel={};setup(+num.value)};
 root.querySelectorAll('.chip').forEach(function(c){c.onclick=function(){num.value=c.dataset.n;refresh()}});
 num.oninput=refresh;
 go.onclick=function(){start(parseInt(num.value,10)||10)};
 refresh();
}
function build(n,qs){
 // round-robin tra gli argomenti scelti, poi mescola
 var by={};qs.forEach(function(q){(by[q.t]=by[q.t]||[]).push(q)});
 var keys=shuffle(Object.keys(by));keys.forEach(function(k){by[k]=shuffle(by[k])});
 var out=[];while(out.length<n){var any=false;for(var i=0;i<keys.length&&out.length<n;i++){var q=by[keys[i]].pop();if(q){out.push(q);any=true}}if(!any)break}
 return shuffle(out);
}
function start(n,fixed){
 var qs=fixed||data.q.filter(function(q){return sel[q.t]});
 n=Math.max(1,Math.min(MAXQ,n,qs.length));
 session=fixed?shuffle(fixed).slice(0,MAXQ):build(n,qs);
 session=session.map(function(q){var o=q.o.map(function(t,i){return {t:t,ok:i===0}});return {t:q.t,q:q.q,e:q.e,o:shuffle(o),src:q}});
 cur=0;score=0;wrong=[];ask();
}
function title(id){var f=data.topics.filter(function(t){return t.id===id})[0];return f?f.title:''}
function ask(){
 answered=false;var q=session[cur];
 var h='<div class="qbar"><div style="width:'+(cur/session.length*100)+'%"></div></div>';
 h+='<p class="qmeta">Domanda '+(cur+1)+' di '+session.length+' · <span>'+esc(title(q.t))+'</span></p>';
 h+='<h2 class="qq">'+esc(q.q)+'</h2><div class="qopts">';
 q.o.forEach(function(o,i){h+='<button type="button" class="qo" data-i="'+i+'"><b>'+'ABCD'[i]+'</b><span>'+esc(o.t)+'</span></button>'});
 h+='</div><div id="q-fb"></div><div class="qnav"><button type="button" id="q-quit" class="ghost">Interrompi</button></div>';
 root.innerHTML=h;window.scrollTo(0,0);
 root.querySelectorAll('.qo').forEach(function(b){b.onclick=function(){pickAns(+b.dataset.i)}});
 document.getElementById('q-quit').onclick=function(){if(confirm('Interrompere il quiz?'))setup()};
}
function pickAns(i){
 if(answered)return;answered=true;var q=session[cur],ok=q.o[i].ok;
 if(ok)score++;else wrong.push(q);
 root.querySelectorAll('.qo').forEach(function(b,k){b.disabled=true;if(q.o[k].ok)b.classList.add('right');else if(k===i)b.classList.add('wrong')});
 var last=cur===session.length-1;
 document.getElementById('q-fb').innerHTML='<div class="qfb '+(ok?'ok':'ko')+'"><b>'+(ok?'Corretto.':'Sbagliato.')+'</b> '+esc(q.e)+'</div><button type="button" id="q-next" class="qgo">'+(last?'Vedi il risultato':'Avanti')+'</button>';
 var nb=document.getElementById('q-next');nb.focus();
 nb.onclick=function(){if(last)end();else{cur++;ask()}};
}
function end(){
 var n=session.length,pc=Math.round(score/n*100),voto=Math.round(score/n*10*10)/10;
 var h='<div class="qbar"><div style="width:100%"></div></div><h2>Risultato</h2>';
 h+='<p class="qscore"><b>'+score+' / '+n+'</b> · '+pc+'% · voto indicativo '+String(voto).replace('.',',')+'/10</p>';
 if(wrong.length){
  h+='<h3>Da ripassare</h3><ul class="qrev">';
  wrong.forEach(function(q){var c=q.o.filter(function(o){return o.ok})[0];h+='<li><b>'+esc(q.q)+'</b><br>Risposta corretta: <em>'+esc(c.t)+'</em><br><small>'+esc(q.e)+'</small></li>'});
  h+='</ul>';
 }else h+='<p>Nessun errore. Ottimo lavoro: ripeti con altri argomenti o con più domande.</p>';
 h+='<div class="qnav">';
 if(wrong.length)h+='<button type="button" id="q-redo" class="qgo">Rifai gli errori ('+wrong.length+')</button>';
 h+='<button type="button" id="q-again" class="qgo alt">Stesso quiz, nuove domande</button><button type="button" id="q-new" class="ghost">Cambia argomenti</button></div>';
 root.innerHTML=h;window.scrollTo(0,0);
 var r=document.getElementById('q-redo');
 if(r)r.onclick=function(){start(wrong.length,wrong.map(function(q){return q.src}))};
 document.getElementById('q-again').onclick=function(){start(n)};
 document.getElementById('q-new').onclick=function(){setup(n)};
}
fetch(base+'assets/quiz.json').then(function(r){return r.json()}).then(function(j){
 data=j;
 var m=/[?&]t=([0-9,]+)/.exec(location.search);
 if(m)m[1].split(',').forEach(function(id){sel[id]=true});
 setup();
}).catch(function(){root.innerHTML='<p>Impossibile caricare le domande. Apri la pagina una volta con la connessione attiva.</p>'});
})();
