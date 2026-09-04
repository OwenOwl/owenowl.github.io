(()=>{"use strict";
const items=Array.isArray(window.GALLERY_DATA)?window.GALLERY_DATA:[],colors={Baseball:"var(--baseball)",HIMEHINA:"var(--himehina)",Live:"var(--live)"},gallery=document.querySelector("#gallery"),empty=document.querySelector("#emptyState"),lightbox=document.querySelector("#lightbox"),detail=lightbox.querySelector(".detail"),image=document.querySelector("#detailImage");let active=null,returnFocus=null;
const color=c=>colors[c]||"var(--accent)";
const esc=value=>String(value).replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;").replaceAll('"',"&quot;");
document.querySelector("#categoryKey").innerHTML=[...new Set(items.map(x=>x.category))].map(c=>`<label class="key-item" style="--category-color:${color(c)}"><input type="checkbox" value="${esc(c)}" checked><span>${esc(c)}</span></label>`).join("");
empty.hidden=items.length>0;gallery.innerHTML=items.map((x,i)=>`<button class="tile" type="button" data-index="${i}" style="--category-color:${color(x.category)}"><img class="tile-image" src="${esc(x.image)}" alt="" loading="lazy"><span class="tile-copy"><span class="tile-title">${esc(x.title)}</span>${x.excerpt?`<span class="tile-excerpt">${esc(x.excerpt)}</span>`:""}<time class="tile-date" datetime="${esc(x.date)}">${esc(x.dateDisplay)}</time></span></button>`).join("");
function layoutMasonry(){
  const tiles=[...gallery.querySelectorAll(".tile:not([hidden])")],gap=window.innerWidth<=760?10:16,width=gallery.clientWidth;
  gallery.querySelectorAll(".tile[hidden]").forEach(tile=>{tile.style.left="";tile.style.top=""});
  empty.hidden=tiles.length>0;
  if(!tiles.length){gallery.style.height="0";return}
  if(!tiles.length||!width)return;
  const columns=window.innerWidth<=760?2:Math.max(1,Math.min(4,Math.floor((width+gap)/(240+gap))));
  const tileWidth=(width-gap*(columns-1))/columns,heights=Array(columns).fill(0);
  tiles.forEach(tile=>{
    tile.style.width=`${tileWidth}px`;
    const column=heights.indexOf(Math.min(...heights));
    tile.style.left=`${column*(tileWidth+gap)}px`;
    tile.style.top=`${heights[column]}px`;
    heights[column]+=tile.offsetHeight+gap;
  });
  gallery.style.height=`${Math.max(...heights)-gap}px`;
}
let resizeFrame;
const requestLayout=()=>{cancelAnimationFrame(resizeFrame);resizeFrame=requestAnimationFrame(layoutMasonry)};
gallery.querySelectorAll(".tile-image").forEach(img=>img.addEventListener("load",requestLayout));
new ResizeObserver(requestLayout).observe(gallery);
document.fonts?.ready.then(requestLayout);
requestLayout();
document.querySelectorAll("#categoryKey input").forEach(input=>input.addEventListener("change",()=>{
  const enabled=new Set([...document.querySelectorAll("#categoryKey input:checked")].map(box=>box.value));
  gallery.querySelectorAll(".tile").forEach((tile,index)=>{tile.hidden=!enabled.has(items[index].category)});
  requestLayout();
}));
function open(x,trigger){active=x;returnFocus=trigger;detail.style.setProperty("--category-color",color(x.category));document.querySelector("#detailCategory").textContent=x.category;document.querySelector("#detailTitle").textContent=x.title;const d=document.querySelector("#detailDate");d.dateTime=x.date;d.textContent=x.dateDisplay;document.querySelector("#detailBody").innerHTML=x.contentHtml||"";image.src=x.image;image.alt=x.title;lightbox.hidden=false;document.body.classList.add("has-lightbox");lightbox.querySelector(".detail-close").focus()}
function close(){lightbox.hidden=true;document.body.classList.remove("has-lightbox");image.removeAttribute("src");active=null;returnFocus?.focus()}
gallery.querySelectorAll(".tile").forEach(t=>t.addEventListener("click",()=>open(items[Number(t.dataset.index)],t)));lightbox.querySelectorAll("[data-close]").forEach(b=>b.addEventListener("click",close));document.addEventListener("keydown",e=>{if(!lightbox.hidden&&e.key==="Escape")close()});
})();
