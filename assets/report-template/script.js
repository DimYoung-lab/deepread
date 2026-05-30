/**
 * Interview Report Template — Interactive Script
 * Vanilla JS, zero dependencies. Editorial-grade interactivity.
 * Supports: theme tabs, evidence toggles, search, scroll-spy, keyboard shortcuts.
 */
(function(){"use strict";

function ready(fn){document.readyState!=="loading"?fn():document.addEventListener("DOMContentLoaded",fn)}

ready(function(){
  try{
    var hdr=document.querySelector(".site-header");
    if(hdr){document.documentElement.style.setProperty("--header-height",hdr.offsetHeight+"px")}
    initTheme();
    initSearch();
    initThemeTabs();
    initEvidenceToggles();
    initScrollSpy();
    initKeyboardShortcuts();
    initReadingProgress();
    initTimestampClicks();
    initBackToTop();
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
    var els=mc.querySelectorAll(".theme-section,.timeline-segment");secs=[];
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

/* ---- Theme Tab Navigation ---- */
function initThemeTabs(){
  var nav=document.getElementById("themeNav");if(!nav)return;
  var tabs=nav.querySelectorAll(".theme-tab");
  var sections=document.querySelectorAll(".theme-section");
  if(!tabs.length||!sections.length)return;

  // Build id→section map
  var sectionMap={};
  sections.forEach(function(s){sectionMap[s.id]=s});

  // Click handler
  tabs.forEach(function(tab){
    tab.addEventListener("click",function(e){
      e.preventDefault();
      var targetId=tab.getAttribute("data-theme-id");
      var section=document.getElementById(targetId);
      if(section){
        section.scrollIntoView({behavior:"smooth",block:"start"});
        setActiveTab(targetId);
      }
    });
  });

  // IntersectionObserver for active tab tracking
  var observer=new IntersectionObserver(function(entries){
    var best=null,br=0;
    entries.forEach(function(e){
      if(e.intersectionRatio>br){br=e.intersectionRatio;best=e.target.id}
    });
    if(best)setActiveTab(best);
  },{rootMargin:"-20% 0px -60% 0px",threshold:[0,0.1,0.3,0.5,0.8]});

  sections.forEach(function(s){observer.observe(s)});

  function setActiveTab(id){
    tabs.forEach(function(t){
      t.classList[t.getAttribute("data-theme-id")===id?"add":"remove"]("active");
    });
  }
}

/* ---- Evidence Toggles ---- */
function initEvidenceToggles(){
  document.addEventListener("click",function(e){
    var btn=e.target.closest(".evidence-toggle");if(!btn)return;
    var targetId=btn.getAttribute("data-target");
    var detail=document.getElementById(targetId);
    if(detail){
      var isOpen=detail.classList.contains("visible");
      if(isOpen){detail.classList.remove("visible");btn.classList.remove("open")}
      else{detail.classList.add("visible");btn.classList.add("open")}
    }
  });
}

/* ---- Scroll-Spy (for segment anchors in timeline) ---- */
function initScrollSpy(){
  // Scroll spy is now handled by theme tab observer above.
  // Keep this for backward compatibility with any sidebar nav.
  var sb=document.getElementById("sidebar");if(!sb)return;
  var links=sb.querySelectorAll("a[href^='#']");if(!links.length)return;
  links.forEach(function(a){
    a.addEventListener("click",function(e){
      e.preventDefault();
      var t=document.getElementById(a.getAttribute("href").slice(1));
      if(t){t.scrollIntoView({behavior:"smooth",block:"start"});history.replaceState(null,"",a.getAttribute("href"))}
    });
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
      var sec=document.querySelectorAll(".theme-section");if(!sec.length)return;
      var ci=-1,st=scrollY+innerHeight/3;
      for(var i=0;i<sec.length;i++){if(sec[i].offsetTop>=st){ci=i;break}}
      if(ci===-1)ci=sec.length-1;
      e.preventDefault();
      var ni=e.key==="j"?Math.min(ci+1,sec.length-1):Math.max(ci-1,0);
      sec[ni].scrollIntoView({behavior:"smooth",block:"start"});
    }
  });
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
