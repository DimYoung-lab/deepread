/**
 * Interview Report Template — Interactive Script
 * Vanilla JS, zero dependencies. Editorial-grade interactivity.
 */
(function(){"use strict";

function ready(fn){document.readyState!=="loading"?fn():document.addEventListener("DOMContentLoaded",fn)}

ready(function(){
  try{
    var hdr=document.querySelector(".site-header");
    if(hdr){document.documentElement.style.setProperty("--header-height",hdr.offsetHeight+"px")}
    initTheme();
    initSearch();
    initScrollSpy();
    initKeyboardShortcuts();
    initCollapseControls();
    initReadingProgress();
    initTimestampClicks();
    initBackToTop();
    initSidebarNav();
  }catch(e){console.error("[Report] Init error:",e)}
});

/* ---- Theme ---- */
function initTheme(){
  var t=document.getElementById("themeToggle");if(!t)return;
  var s=localStorage.getItem("interview-report-theme");
  if(s)document.documentElement.setAttribute("data-theme",s);
  else if(window.matchMedia&&matchMedia("(prefers-color-scheme:dark)").matches)
    document.documentElement.setAttribute("data-theme","dark");
  t.addEventListener("click",function(){
    var c=document.documentElement.getAttribute("data-theme");
    var n=c==="dark"?"light":"dark";
    document.documentElement.setAttribute("data-theme",n);
    localStorage.setItem("interview-report-theme",n);
  });
}

/* ---- Search ---- */
function initSearch(){
  var input=document.getElementById("searchInput");
  var badge=document.getElementById("searchBadge");
  if(!input)return;
  var secs=[],timer=null,indexed=false;
  function build(){
    if(indexed)return;indexed=true;
    var mc=document.getElementById("mainContent");if(!mc)return;
    var els=mc.querySelectorAll("section,article,details");secs=[];
    els.forEach(function(e){secs.push({el:e,text:(e.textContent||"").toLowerCase()})});
  }
  input.addEventListener("focus",build);
  input.addEventListener("input",function(){build();clearTimeout(timer);timer=setTimeout(doSearch,150)});

  function doSearch(){
    var q=input.value.trim().toLowerCase();clearHighlights();
    if(!q){secs.forEach(function(s){s.el.style.display=""});if(badge)badge.textContent="";return}
    var c=0;
    secs.forEach(function(s){
      if(s.text.indexOf(q)!==-1){s.el.style.display="";highlight(s.el,q);c++}
      else s.el.style.display="none";
    });
    if(badge)badge.textContent=c>0?c+"/"+secs.length:"0";
  }

  function highlight(el,q){
    var tw=document.createTreeWalker(el,NodeFilter.SHOW_TEXT,null,false),nodes=[];
    while(tw.nextNode()){
      var p=tw.currentNode.parentNode;
      if(p.nodeName==="MARK"||p.nodeName==="SCRIPT"||p.nodeName==="STYLE"||
         p.nodeName==="INPUT"||p.nodeName==="TEXTAREA"||p.closest(".search-highlight"))continue;
      if(tw.currentNode.textContent.toLowerCase().indexOf(q)!==-1)nodes.push(tw.currentNode);
    }
    var re=new RegExp("("+escRx(q)+")","gi");
    nodes.forEach(function(tn){
      var f=document.createDocumentFragment(),h=tn.textContent,li=0,m;
      re.lastIndex=0;
      while((m=re.exec(h))!==null){
        if(m.index>li)f.appendChild(document.createTextNode(h.slice(li,m.index)));
        var mk=document.createElement("mark");mk.textContent=m[0];mk.className="search-highlight";
        f.appendChild(mk);li=re.lastIndex;
      }
      if(li<h.length)f.appendChild(document.createTextNode(h.slice(li)));
      if(f.childNodes.length>1){tn.parentNode.replaceChild(f,tn)}
    });
  }

  function escRx(s){return s.replace(/[.*+?^${}()|[\]\\]/g,"\\$&")}
  function clearHighlights(){
    document.querySelectorAll(".search-highlight").forEach(function(m){
      var p=m.parentNode;if(p){p.replaceChild(document.createTextNode(m.textContent),m);p.normalize()}
    });
  }
}

/* ---- Scroll-Spy ---- */
function initScrollSpy(){
  var sb=document.getElementById("sidebar");if(!sb)return;
  var links=sb.querySelectorAll("a[href^='#']");if(!links.length)return;
  var map={};links.forEach(function(a){map[a.getAttribute("href").slice(1)]=a});
  var th=[];for(var i=0;i<=20;i++)th.push(i/20);
  var obs=new IntersectionObserver(function(entries){
    var vis={};entries.forEach(function(e){vis[e.target.id]=e.intersectionRatio});
    var best=null,br=0;
    Object.keys(vis).forEach(function(id){if(vis[id]>br){br=vis[id];best=id}});
    if(best){
      links.forEach(function(a){a.classList.remove("active");a.removeAttribute("aria-current")});
      var al=map[best];if(al){al.classList.add("active");al.setAttribute("aria-current","true")}
    }
  },{rootMargin:"-10% 0px -70% 0px",threshold:th});
  var mc=document.getElementById("mainContent");if(!mc)return;
  mc.querySelectorAll("section[id],article[id]").forEach(function(e){obs.observe(e)});
}

/* ---- Sidebar Nav Click ---- */
function initSidebarNav(){
  var sb=document.getElementById("sidebar");if(!sb)return;
  sb.addEventListener("click",function(e){
    var a=e.target.closest("a[href^='#']");if(!a)return;e.preventDefault();
    var t=document.getElementById(a.getAttribute("href").slice(1));
    if(t){t.scrollIntoView({behavior:"smooth",block:"start"});history.replaceState(null,"",a.getAttribute("href"))}
  });
}

/* ---- Keyboard Shortcuts ---- */
function initKeyboardShortcuts(){
  document.addEventListener("keydown",function(e){
    var inp=e.target.tagName==="INPUT"||e.target.tagName==="TEXTAREA"||e.target.isContentEditable;
    if(!inp&&(e.key==="/"||(e.key==="k"&&(e.ctrlKey||e.metaKey)))){
      e.preventDefault();var si=document.getElementById("searchInput");if(si)si.focus();return;
    }
    if(e.key==="Escape"){
      var si=document.getElementById("searchInput");
      if(si&&document.activeElement===si){si.value="";si.blur();si.dispatchEvent(new Event("input"))}return;
    }
    if(!inp&&(e.key==="j"||e.key==="k")){
      var mc=document.getElementById("mainContent");if(!mc)return;
      var sec=mc.querySelectorAll("section[id],article[id]");if(!sec.length)return;
      var ci=-1,st=scrollY+innerHeight/3;
      for(var i=0;i<sec.length;i++){if(sec[i].offsetTop>=st){ci=i;break}}
      if(ci===-1)ci=sec.length-1;
      e.preventDefault();
      var ni=e.key==="j"?Math.min(ci+1,sec.length-1):Math.max(ci-1,0);
      sec[ni].scrollIntoView({behavior:"smooth",block:"start"});
    }
  });
}

/* ---- Collapse / Expand ---- */
function initCollapseControls(){
  function all(){return document.querySelectorAll("#mainContent details,.supplemental details")}
  var eb=document.getElementById("expandAll"),cb=document.getElementById("collapseAll");
  if(eb)eb.addEventListener("click",function(){all().forEach(function(d){d.setAttribute("open","")})});
  if(cb)cb.addEventListener("click",function(){all().forEach(function(d){d.removeAttribute("open")})});
}

/* ---- Reading Progress ---- */
function initReadingProgress(){
  var bar=document.getElementById("progressBar");if(!bar)return;
  var tick=false;
  window.addEventListener("scroll",function(){
    if(!tick){requestAnimationFrame(function(){
      var h=document.documentElement.scrollHeight-innerHeight;
      bar.style.width=(h>0?Math.min((scrollY/h)*100,100):0)+"%";tick=false;
    });tick=true}
  },{passive:true});
}

/* ---- Timestamp Click ---- */
function initTimestampClicks(){
  document.addEventListener("click",function(e){
    var b=e.target.closest(".timestamp-badge");if(!b)return;
    var rid=b.getAttribute("data-ref"),ts=b.getAttribute("data-timestamp");
    if(!rid&&!ts)return;
    var t=null;
    if(rid)t=document.getElementById(rid);
    if(!t&&ts)t=document.querySelector('[data-timestamp="'+CSS.escape(ts)+'"]');
    if(t){
      t.scrollIntoView({behavior:"smooth",block:"center"});
      t.classList.add("highlight-flash");
      t.addEventListener("animationend",function(){t.classList.remove("highlight-flash")},{once:true});
    }
  });
}

/* ---- Back to Top ---- */
function initBackToTop(){
  var btn=document.getElementById("backToTop");if(!btn)return;
  var tick=false;
  window.addEventListener("scroll",function(){
    if(!tick){requestAnimationFrame(function(){
      btn.classList[scrollY>600?"add":"remove"]("visible");tick=false;
    });tick=true}
  },{passive:true});
  btn.addEventListener("click",function(){scrollTo({top:0,behavior:"smooth"})});
}

})();
