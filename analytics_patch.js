/* BA DASHBOARD - ANALYTICS PATCH (v3)
   Mirrors the bot's Phase A analytics + SIM mode into the dashboard without touching index.html logic.
   Add ONE line to index.html before </body>:  <script src="analytics_patch.js?v=3"></script> */
(function(){
"use strict";
function enhanceBot(d){
  if(!d) return;
  /* 1) SIM / LIVE banner */
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
  /* 2) QML equity card -> SIM bank when simulating */
  if(d.sim){
    document.querySelectorAll('#botSummary .stat').forEach(function(c){
      var l=c.querySelector('.l'), n=c.querySelector('.n');
      if(l && l.textContent.trim()==='Equity' && n){ n.textContent='$'+Math.round(d.sim.equity); l.textContent='SIM bank'; }
    });
  }
  /* 3) currency honesty: QML/live panels are USDT -> show $ (sweep paper book stays INR) */
  var qw=document.getElementById('botQWrap');
  if(qw){ qw.querySelectorAll('*').forEach(function(n){
    if(n.children.length===0 && n.textContent.indexOf('Rs.')!==-1) n.textContent=n.textContent.split('Rs.').join('$');
  }); }
  /* 4) Analytics panel: shadow models + funnel */
  var wrap=document.getElementById('analyticsWrap');
  if(!wrap){
    wrap=document.createElement('div'); wrap.id='analyticsWrap';
    var area=document.getElementById('botArea');
    if(area) area.appendChild(wrap);
    wrap.innerHTML='<div class="panel-title" style="font-size:13px;margin-top:26px;">&#x1F4C8; QML Analytics &mdash; Shadow Models &amp; Funnel</div>'
      +'<div id="anModels" style="display:flex;flex-wrap:wrap;gap:12px;justify-content:center;margin:14px 0;"></div>'
      +'<div id="anFunnel" style="text-align:center;color:#8B94A7;font-size:12.5px;line-height:2;padding:0 12px;"></div>'
      +'<div class="meta" style="margin-top:10px;">D=ideal P1 &middot; A=limit at P1 &middot; B=basis-adjusted &middot; C=market at signal (assumed-fill model, labeled) &middot; live gates: score &ge;5 &middot; counter-trend &ge;7 &middot; order expires if TP consumed or price leaves 1.5 ATR</div>';
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
function hook(){
  if(typeof window.renderBot==='function' && !window.renderBot.__patched){
    var orig=window.renderBot;
    var wrapped=function(d){ var r=orig.call(this,d); try{enhanceBot(d);}catch(e){console.log('analytics_patch',e);} return r; };
    wrapped.__patched=true; window.renderBot=wrapped;
  }
}
if(document.readyState==='loading'){ document.addEventListener('DOMContentLoaded',function(){setTimeout(hook,800);}); }
else { setTimeout(hook,800); }
setInterval(hook,5000);
})();
