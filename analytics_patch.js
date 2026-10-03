/* BA DASHBOARD - ANALYTICS PATCH (v7)
   Adds: fetch timeouts (no more stuck scans) · multi-source pair loader (CoinDCX ->
   bot's GitHub JSON -> cache -> embedded) · SIM banner · $ currency in QML panels ·
   analytics panel (shadow models + funnel). Load with ONE line before </body>:
   <script src="analytics_patch.js?v=7"></script> */
(function(){
"use strict";

/* ============ -1) GLOBAL FETCH TIMEOUT (10s) - kills stuck scans ============ */
try{
  var __ofetch = window.fetch.bind(window);
  window.fetch = function(url, opts){
    try{
      var u = String(url);
      if(u.indexOf('fapi.binance.com')!==-1 || u.indexOf('api.coindcx.com')!==-1){
        opts = opts || {};
        if(!opts.signal){
          var __c = new AbortController();
          opts.signal = __c.signal;
          setTimeout(function(){ try{__c.abort();}catch(e){} }, 10000);
        }
      }
    }catch(e){}
    return __ofetch(url, opts);
  };
}catch(e){}

/* ============ 0) FALLBACK + ROBUST MULTI-SOURCE PAIR LOADER ============ */
var FALLBACK_PAIRS = ["BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","XRPUSDT","DOGEUSDT","ADAUSDT","AVAXUSDT","LINKUSDT","TRXUSDT","DOTUSDT","LTCUSDT","NEARUSDT","UNIUSDT","ATOMUSDT","ARBUSDT","OPUSDT","SUIUSDT","SEIUSDT","TIAUSDT","APTUSDT","INJUSDT","GRTUSDT","AAVEUSDT","LDOUSDT","ARUSDT","FILUSDT","PEPEUSDT","SHIBUSDT","WIFUSDT","BONKUSDT","JUPUSDT","PYTHUSDT","STXUSDT","IMXUSDT","RNDRUSDT","FETUSDT","GALAUSDT","SANDUSDT","MANAUSDT","AXSUSDT","CHZUSDT","ENAUSDT","WLDUSDT","JASMYUSDT","FTMUSDT","ALGOUSDT","VETUSDT","EOSUSDT","XLMUSDT","ICPUSDT","HBARUSDT","KAVAUSDT","GMXUSDT","CRVUSDT","ENSUSDT","1INCHUSDT","COMPUSDT","ZECUSDT","XMRUSDT","ETCUSDT","BCHUSDT","QNTUSDT","EGLDUSDT","THETAUSDT","XTZUSDT","CAKEUSDT","MKRUSDT","SNXUSDT","ENJUSDT","CELOUSDT","FLOWUSDT","DYDXUSDT","ORDIUSDT","NOTUSDT","TRBUSDT","PENDLEUSDT","ONDOUSDT","STRKUSDT","ZROUSDT","BLURUSDT","SUSDT","BBUSDT"];

try{
  window.loadPairs = async function(){
    var pc=document.getElementById('pairCount');
    function setPairs(list){
      var mapped=list.map(function(x){return String(x).replace('B-','').replace('_USDT','')+'USDT';});
      try{ PAIRS=mapped; }catch(e){}
      try{ window.PAIRS=mapped; }catch(e){}
      try{ localStorage.setItem('ba_pairs', JSON.stringify({t:Date.now(), pairs:mapped})); }catch(e){}
    }
    /* source 1: CoinDCX direct (full 505 when their firewall allows) */
    var urls=[
      'https://api.coindcx.com/exchange/v1/derivatives/futures/data/active_instruments?margin_currency_short_name%5B%5D=USDT',
      'https://api.coindcx.com/exchange/v1/derivatives/futures/data/active_instruments?margin_currency_short_name=USDT',
      'https://api.coindcx.com/exchange/v1/derivatives/futures/data/active_instruments'
    ];
    for(var i=0;i<urls.length;i++){
      try{
        var r=await fetch(urls[i]);
        if(!r.ok) continue;
        var list=await r.json();
        if(Array.isArray(list) && list.length){ setPairs(list); if(pc) pc.textContent=''+PAIRS.length+' pairs'; return; }
      }catch(e){}
    }
    /* source 2: the BOT's own upload (same GitHub channel as the BOT tab - always reachable) */
    var botSrc=[
      'https://cdn.jsdelivr.net/gh/ajaysharda1992/ba-bot-data@main/bot_trades.json?_='+Date.now(),
      'https://raw.githubusercontent.com/ajaysharda1992/ba-bot-data/main/bot_trades.json?_='+Date.now()
    ];
    for(var j=0;j<botSrc.length;j++){
      try{
        var rb=await fetch(botSrc[j]);
        if(!rb.ok) continue;
        var db=await rb.json();
        if(db && Array.isArray(db.pairs) && db.pairs.length){ setPairs(db.pairs); if(pc) pc.textContent=''+PAIRS.length+' pairs (bot)'; return; }
      }catch(e){}
    }
    /* source 3: browser cache, then embedded majors */
    try{ var c=JSON.parse(localStorage.getItem('ba_pairs')||'null'); if(c && c.pairs && c.pairs.length) setPairs(c.pairs); }catch(e){}
    if(!PAIRS.length) setPairs(FALLBACK_PAIRS);
    if(pc) pc.textContent=''+PAIRS.length+' pairs';
  };
}catch(e){}

/* ============ 1) ENHANCE BOT TAB ============ */
function enhanceBot(d){
  if(!d) return;
  var ban=document.getElementById('simBanner');
  if(!ban){
    ban=document.createElement('div'); ban.id='simBanner';
    var sum=document.getElementById('botSummary');
    if(sum) sum.appendChild(ban);
  }
  if(ban){
    var simOn = d.sim && typeof d.sim.equity==='number';
    ban.style.cssText='width:100%;text-align:center;padding:10px 8px;border-radius:10px;font-weight:800;letter-spacing:.5px;font-size:13px;box-sizing:border-box;';
    if(simOn){
      ban.style.background='rgba(201,162,39,.12)'; ban.style.border='1px solid #C9A227'; ban.style.color='#E3C565';
      ban.innerHTML='&#x1F9EA; SIMULATION MODE &mdash; no real orders &middot; SIM bank $'+Math.round(d.sim.equity)+' (day '+(d.sim.day>=0?'+':'')+(+d.sim.day).toFixed(2)+'R) &middot; live book frozen $'+Math.round(((d.live&&d.live.equity)||0));
    } else {
      ban.style.background='rgba(46,191,113,.08)'; ban.style.border='1px solid #2FBF71'; ban.style.color='#2FBF71';
      ban.innerHTML='&#x1F4B0; LIVE MODE &mdash; real orders &middot; bank $'+Math.round(((d.live&&d.live.equity)||0));
    }
  }
  if(d.sim){
    document.querySelectorAll('#botSummary .stat').forEach(function(c){
      var l=c.querySelector('.l'), n=c.querySelector('.n');
      if(l && l.textContent.trim()==='Equity' && n){ n.textContent='$'+Math.round(d.sim.equity); l.textContent='SIM bank'; }
    });
  }
  var qw=document.getElementById('botQWrap');
  if(qw){ qw.querySelectorAll('*').forEach(function(n){
    if(n.children.length===0 && n.textContent.indexOf('Rs.')!==-1) n.textContent=n.textContent.split('Rs.').join('$');
  }); }
  var wrap=document.getElementById('analyticsWrap');
  if(!wrap){
    wrap=document.createElement('div'); wrap.id='analyticsWrap';
    var area=document.getElementById('botArea');
    if(area) area.appendChild(wrap);
    wrap.innerHTML='<div class="panel-title" style="font-size:13px;margin-top:26px;">&#x1F4C8; QML Analytics &mdash; Shadow Models &amp; Funnel</div>'
      +'<div id="anModels" style="display:flex;flex-wrap:wrap;gap:12px;justify-content:center;margin:14px 0;"></div>'
      +'<div id="anFunnel" style="text-align:center;color:#8B94A7;font-size:12.5px;line-height:2;padding:0 12px;"></div>'
      +'<div class="meta" style="margin-top:10px;">D=ideal P1 &middot; A=limit at P1 &middot; L=ladder (1R/1.5R rungs) &middot; B=basis-adjusted &middot; C=market at signal &middot; assumed-fill + slippage models, labeled &middot; gates: score &ge;5 &middot; counter-trend &ge;7 &middot; expiry if TP consumed or price leaves 1.5 ATR</div>';
  }
  var mo=(d.report&&d.report.models)||{};
  var mk=document.getElementById('anModels');
  if(mk){
    var keys=Object.keys(mo);
    mk.innerHTML=keys.map(function(m){ var s=mo[m];
      return '<div class="stat" style="min-width:110px;padding:10px 14px;"><div class="n" style="font-size:17px;color:'+(s.avg_r>=0?'#2ecc71':'#ff5c5c')+';">'+(s.avg_r>=0?'+':'')+s.avg_r+'R</div><div class="l">'+m+' &middot; win '+s.win_pct+'% &middot; n='+s.n+' &middot; fill '+s.fill_pct+'%</div></div>';
    }).join('') || '<div class="meta">shadow models accumulating&hellip;</div>';
  }
  var fn=d.funnel||{}, fk=document.getElementById('anFunnel');
  if(fk){
    var order=['raw_qml','st_RETEST','st_ARMED','st_STALE','score_ge4','score_ge5','gate_score','gate_exec_basis','gate_exec_listed','gate_exec_thin','gate_countertrend','gate_corr_dir_cap','gate_past_structure','gate_expired_at_rest','orders_submitted','orders_filled','orders_cancelled','exits_win','exits_loss','exits_time_stop'];
    var parts=order.filter(function(k){return fn[k]!=null;}).map(function(k){
      return k.replace('gate_','&#x26D4; ').replace('st_','')+': <b style="color:#DCE3F0">'+fn[k]+'</b>';
    });
    fk.innerHTML=parts.length?parts.join(' &middot; '):'funnel accumulating&hellip;';
  }
}

/* ============ 2) HOOK renderBot (if reachable) + SELF-POLL (always) ============ */
function hook(){
  if(typeof window.renderBot==='function' && !window.renderBot.__patched){
    var orig=window.renderBot;
    var wrapped=function(d){ var r=orig.call(this,d); try{enhanceBot(d);}catch(e){console.log('analytics_patch',e);} return r; };
    wrapped.__patched=true; window.renderBot=wrapped;
  }
}
var __BOTJSON = 'https://cdn.jsdelivr.net/gh/ajaysharda1992/ba-bot-data@main/bot_trades.json';
async function __pollBot(){
  try{
    var r = await fetch(__BOTJSON + '?_=' + Date.now());
    var d = await r.json();
    enhanceBot(d);
  }catch(e){}
}
if(document.readyState==='loading'){ document.addEventListener('DOMContentLoaded',function(){setTimeout(hook,800); setTimeout(__pollBot,3000);}); }
else { setTimeout(hook,800); setTimeout(__pollBot,3000); }
setInterval(hook,5000);
setInterval(__pollBot,60000);
})();
