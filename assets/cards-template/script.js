/**
 * Learning Cards — Interactive Script
 * Vanilla JS. Swipe, keyboard, touch, and progress tracking.
 */
(function(){"use strict";

function ready(fn){document.readyState!=="loading"?fn():document.addEventListener("DOMContentLoaded",fn)}

ready(function(){
  try{
    initTheme();
    initNav();
    initExpandables();
    initIntersectionObserver();
    initRoleTabs();
    initKeyboardShortcuts();
    initTouchSupport();
    initProgressBar();
    initDotNav();
  }catch(e){console.error("[Cards] Init error:",e)}
});

/* ---- Theme ---- */
function initTheme(){
  var btn=document.getElementById("themeToggle");if(!btn)return;
  var s=localStorage.getItem("learning-cards-theme");
  if(s)document.documentElement.setAttribute("data-theme",s);
  else if(window.matchMedia&&matchMedia("(prefers-color-scheme:dark)").matches)
    document.documentElement.setAttribute("data-theme","dark");
  btn.addEventListener("click",function(){
    var c=document.documentElement.getAttribute("data-theme");
    var n=c==="dark"?"light":"dark";
    document.documentElement.setAttribute("data-theme",n);
    localStorage.setItem("learning-cards-theme",n);
  });
}

/* ---- Card Navigation ---- */
var allCards=[],currentIndex=0;

function initNav(){
  allCards=document.querySelectorAll(".card");if(!allCards.length)return;
  currentIndex=0;
  updateCounter();

  var prev=document.getElementById("prevCard");
  var next=document.getElementById("nextCard");
  if(prev)prev.addEventListener("click",function(){goToCard(currentIndex-1)});
  if(next)next.addEventListener("click",function(){goToCard(currentIndex+1)});

  // Click on hero "Start Learning" button
  var startBtn=document.querySelector(".btn-primary");
  if(startBtn&&startBtn.textContent.includes("开始")){
    startBtn.addEventListener("click",function(e){
      e.preventDefault();goToCard(1);
    });
  }
}

function goToCard(index){
  if(index<0||index>=allCards.length)return;
  currentIndex=index;
  allCards[index].scrollIntoView({behavior:"smooth",block:"center"});
  updateCounter();
  updateActiveDot();
}

function updateCounter(){
  var c=document.getElementById("cardCounter");
  var m=document.getElementById("mobileCounter");
  var txt=(currentIndex+1)+" / "+allCards.length;
  if(c)c.textContent=txt;
  if(m)m.textContent=txt;
}

/* ---- Expandables ---- */
function initExpandables(){
  document.addEventListener("click",function(e){
    var btn=e.target.closest(".expand-toggle");if(!btn)return;
    btn.classList.toggle("open");
    var content=btn.nextElementSibling;
    if(content&&content.classList.contains("expand-content")){
      content.classList.toggle("visible");
    }
  });
}

/* ---- Intersection Observer for card tracking ---- */
function initIntersectionObserver(){
  var obs=new IntersectionObserver(function(entries){
    entries.forEach(function(e){
      if(e.isIntersecting&&e.intersectionRatio>0.4){
        e.target.classList.add("card-in-view");
        // Find index
        var idx=Array.from(allCards).indexOf(e.target);
        if(idx>=0){currentIndex=idx;updateCounter();updateActiveDot();}
      }
    });
  },{threshold:[0,0.3,0.5,0.8]});

  allCards.forEach(function(c){obs.observe(c)});
}

/* ---- Role Tabs (Closing Card) ---- */
function initRoleTabs(){
  document.addEventListener("click",function(e){
    var tab=e.target.closest(".role-tab");if(!tab)return;
    var role=tab.getAttribute("data-role");
    // Deactivate all tabs in this group
    var group=tab.parentElement;
    group.querySelectorAll(".role-tab").forEach(function(t){t.classList.remove("active")});
    tab.classList.add("active");
    // Show matching content
    var container=group.parentElement;
    container.querySelectorAll(".role-content").forEach(function(c){c.classList.remove("visible")});
    var target=container.querySelector('.role-content[data-role="'+role+'"]');
    if(target)target.classList.add("visible");
  });
}

/* ---- Keyboard Shortcuts ---- */
function initKeyboardShortcuts(){
  document.addEventListener("keydown",function(e){
    var inp=e.target.tagName==="INPUT"||e.target.tagName==="TEXTAREA"||e.target.isContentEditable;
    if(inp)return;

    if(e.key==="ArrowRight"||e.key==="ArrowDown"||e.key==="j"){
      e.preventDefault();goToCard(currentIndex+1);
    }else if(e.key==="ArrowLeft"||e.key==="ArrowUp"||e.key==="k"){
      e.preventDefault();goToCard(currentIndex-1);
    }else if(e.key===" "||e.key==="Enter"){
      // Expand current card's first expandable
      var card=allCards[currentIndex];
      if(card){
        var toggle=card.querySelector(".expand-toggle");
        if(toggle){e.preventDefault();toggle.click();}
      }
    }else if(e.key>="1"&&e.key<="9"){
      e.preventDefault();goToCard(parseInt(e.key)-1);
    }
  });
}

/* ---- Touch / Swipe ---- */
function initTouchSupport(){
  var startX=0,startY=0;
  document.addEventListener("touchstart",function(e){
    startX=e.touches[0].clientX;startY=e.touches[0].clientY;
  },{passive:true});

  document.addEventListener("touchend",function(e){
    var dx=e.changedTouches[0].clientX-startX;
    var dy=e.changedTouches[0].clientY-startY;
    var absDx=Math.abs(dx),absDy=Math.abs(dy);

    // Only trigger if horizontal swipe is dominant and significant
    if(absDx>absDy&&absDx>50){
      if(dx<-30)goToCard(currentIndex+1);
      else if(dx>30)goToCard(currentIndex-1);
    }
  },{passive:true});
}

/* ---- Progress Bar ---- */
function initProgressBar(){
  var bar=document.getElementById("progressBar");if(!bar)return;
  var tick=false;
  window.addEventListener("scroll",function(){
    if(!tick){requestAnimationFrame(function(){
      var h=document.documentElement.scrollHeight-innerHeight;
      bar.style.width=(h>0?Math.min((scrollY/h)*100,100):0)+"%";tick=false;
    });tick=true}
  },{passive:true});
}

/* ---- Dot Nav ---- */
function initDotNav(){
  var container=document.getElementById("navDots");if(!container)return;
  container.addEventListener("click",function(e){
    var dot=e.target.closest(".nav-dot");if(!dot)return;
    var idx=parseInt(dot.getAttribute("data-index"));
    if(!isNaN(idx))goToCard(idx);
  });
}

function updateActiveDot(){
  var dots=document.querySelectorAll(".nav-dot");
  dots.forEach(function(d,i){
    d.classList[i===currentIndex?"add":"remove"]("active");
  });
}

})();
