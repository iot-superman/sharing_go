function hideAddressResults(target){
  const box=document.getElementById(`${target}SearchResults`);
  if(box){box.style.display='none';box.innerHTML='';}
}

function clearPlaceCoord(target){
  coords[target]=null;
  const status=document.getElementById(`${target}SearchStatus`);
  if(status){status.className='address-search-status';status.textContent='';}
  hideAddressResults(target);
}

function selectAddressResult(target,item,{keepList=false}={}){
  const input=document.getElementById(target);
  if(!input||!item||!Number.isFinite(+item.lat)||!Number.isFinite(+item.lng))return false;
  input.value=item.displayName||input.value;
  coords[target]={lat:+item.lat,lng:+item.lng};
  const status=document.getElementById(`${target}SearchStatus`);
  if(status){
    status.className='address-search-status text-success';
    status.textContent=`✓ 已定位：${(+item.lat).toFixed(6)}, ${(+item.lng).toFixed(6)}`;
  }
  if(!keepList)hideAddressResults(target);
  return true;
}

async function geocodeTextValue(target,{autoSelect=true,showCandidates=true}={}){
  const input=document.getElementById(target);
  const status=document.getElementById(`${target}SearchStatus`);
  const box=document.getElementById(`${target}SearchResults`);
  const q=(input?.value||'').trim();
  if(!q)throw Error('請先輸入地址或地名');

  if(status){status.className='address-search-status';status.textContent='🔎 正在查地址…';}
  if(box){box.style.display='none';box.innerHTML='';}

  const j=await api(`/geocode/?q=${encodeURIComponent(q)}`,{method:'GET',timeoutMs:12000});
  const rows=(j.results&&j.results.length)?j.results:[{lat:j.lat,lng:j.lng,displayName:j.displayName}];
  const valid=rows.filter(r=>Number.isFinite(+r.lat)&&Number.isFinite(+r.lng));
  if(!valid.length)throw Error('找不到可用的位置');

  window.__addressSearchResults=window.__addressSearchResults||{};
  window.__addressSearchResults[target]=valid;

  // 放大鏡的主要動作：立即採用最佳第一筆，讓使用者可以直接建立共乘。
  if(autoSelect)selectAddressResult(target,valid[0],{keepList:showCandidates&&valid.length>1});

  // 同時保留候選清單，若第一筆不正確可再點別筆。
  if(showCandidates&&box&&valid.length>1){
    box.innerHTML=valid.map((r,i)=>`<div class="address-result" tabindex="0" data-index="${i}" onclick="selectAddressResult('${target}',window.__addressSearchResults['${target}'][${i}])" onkeydown="if(event.key==='Enter')selectAddressResult('${target}',window.__addressSearchResults['${target}'][${i}])">📍 ${esc(r.displayName||q)}</div>`).join('');
    box.style.display='block';
    if(status)status.textContent=`✓ 已採用第 1 筆；另有 ${valid.length-1} 筆候選可改選`;
  }
  return valid[0];
}

async function searchAddress(target){
  try{
    await geocodeTextValue(target,{autoSelect:true,showCandidates:true});
  }catch(e){
    hideAddressResults(target);
    const status=document.getElementById(`${target}SearchStatus`);
    if(status){status.className='address-search-status error';status.textContent='查地址失敗：'+e.message;}
    console.warn('searchAddress failed',target,e);
  }
}

async function ensurePlaceCoord(target){
  if(coords[target] && Number.isFinite(+coords[target].lat) && Number.isFinite(+coords[target].lng))return coords[target];

  const input=document.getElementById(target);
  const q=(input?.value||'').trim();

  // 「目前位置附近集合點」優先使用瀏覽器最近 GPS，不拿這句文字去做地址搜尋。
  if(target==='meet' && /目前位置/.test(q) && lastBrowserLocation){
    coords.meet={lat:+lastBrowserLocation.lat,lng:+lastBrowserLocation.lng};
    const status=document.getElementById('meetSearchStatus');
    if(status){status.className='address-search-status text-success';status.textContent='✓ 已使用目前位置';}
    return coords.meet;
  }

  // 使用者只打字、沒按放大鏡也沒關係：建立前自動做一次地址解析。
  const first=await geocodeTextValue(target,{autoSelect:true,showCandidates:false});
  return coords[target]||{lat:+first.lat,lng:+first.lng};
}

async function createRide(){
  const btn=document.getElementById('createRideBtn');
  const status=document.getElementById('createStatus');
  const el=id=>document.getElementById(id);

  if(btn.disabled)return;
  btn.disabled=true;
  btn.textContent='建立中…';
  status.className='small mt-2 text-muted';
  status.textContent='正在確認集合點與目的地…';

  try{
    if(!el('date').value||!el('time').value)throw Error('請先選擇日期與時間');
    if(!el('meet').value.trim())throw Error('請輸入集合點');
    if(!el('dest').value.trim())throw Error('請輸入目的地');

    // 重要修正：不再強迫一定要先按「精確選」。
    // 若只有輸入地址，建立前會自動查地址取得座標。
    const [meetCoord,destCoord]=await Promise.all([
      ensurePlaceCoord('meet'),
      ensurePlaceCoord('dest')
    ]);

    if(!meetCoord||!destCoord)throw Error('集合點或目的地無法定位，請按 🔎 或 🗺️ 選位置');

    const d={
      date:el('date').value,
      time:el('time').value,
      maxPeople:+el('max').value,
      meetingName:el('meet').value.trim(),
      destinationName:el('dest').value.trim(),
      mode:el('mode').value,
      estimatedTotal:+el('fare').value||0,
      note:el('note').value,
      meetingLat:+meetCoord.lat,
      meetingLng:+meetCoord.lng,
      destinationLat:+destCoord.lat,
      destinationLng:+destCoord.lng
    };

    if(![d.meetingLat,d.meetingLng,d.destinationLat,d.destinationLng].every(Number.isFinite))throw Error('位置座標無效，請重新查地址或精確選點');
    if(Math.abs(d.meetingLat-d.destinationLat)<1e-7 && Math.abs(d.meetingLng-d.destinationLng)<1e-7)throw Error('集合點與目的地不能完全相同');

    status.textContent='位置確認完成，正在建立共乘…';
    const result=await api('/rides/',{method:'POST',body:JSON.stringify(d),timeoutMs:15000});
    if(!result?.ride?.id)throw Error('伺服器沒有回傳建立結果');

    active=result.ride;
    status.className='small mt-2 text-success';
    status.textContent=`✅ 已建立共乘 #${result.ride.id}`;

    // 成功後直接切到「行程」而不是先做多個背景 API 再決定。
    tab('trip');
    Promise.allSettled([loadRides(),loadTrip()]).then(()=>{});
  }catch(e){
    console.error('createRide failed',e);
    status.className='small mt-2 text-danger';
    status.textContent='建立失敗：'+e.message;
    alert('建立共乘失敗：'+e.message);
  }finally{
    btn.disabled=false;
    btn.textContent='建立共乘';
  }
}