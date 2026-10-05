const assert = require('assert');
const fs = require('fs');
const vm = require('vm');

const elements = {};
function el(id, value='') {
  const obj = {
    id, value, disabled:false, textContent:'', className:'', style:{display:'none'}, innerHTML:'',
    closest(){ return { contains(){ return true; } }; }
  };
  elements[id]=obj; return obj;
}
['date','time','max','meet','dest','mode','fare','note','createRideBtn','createStatus','meetSearchResults','meetSearchStatus','destSearchResults','destSearchStatus'].forEach(id=>el(id));
elements.date.value='2026-10-05';
elements.time.value='16:50';
elements.max.value='3';
elements.meet.value='桃園市政府';
elements.dest.value='埔心火車站';
elements.mode.value='taxi';
elements.fare.value='120';
elements.note.value='smoke';

const calls=[];
let tabCalled=null;
const context = {
  console,
  coords:{meet:null,dest:null},
  lastBrowserLocation:null,
  window:{},
  document:{
    getElementById(id){ return elements[id] || null; },
    addEventListener(){},
  },
  esc:s=>String(s),
  api: async (path,opt={})=>{
    calls.push({path,opt});
    if(path.startsWith('/geocode/?q=')) {
      const q=decodeURIComponent(path.split('=')[1]);
      if(q.includes('桃園市政府')) return {ok:true,results:[{lat:24.9937,lng:121.3010,displayName:'桃園市政府'}]};
      if(q.includes('埔心火車站')) return {ok:true,results:[{lat:24.9199,lng:121.1830,displayName:'埔心火車站'}]};
      throw Error('unexpected geocode '+q);
    }
    if(path==='/rides/' && opt.method==='POST') {
      const body=JSON.parse(opt.body);
      assert.equal(body.date,'2026-10-05');
      assert.equal(body.time,'16:50');
      assert.equal(body.maxPeople,3);
      assert.equal(body.mode,'taxi');
      assert.equal(body.estimatedTotal,120);
      assert.equal(body.meetingName,'桃園市政府');
      assert.equal(body.destinationName,'埔心火車站');
      assert.ok(Number.isFinite(body.meetingLat));
      assert.ok(Number.isFinite(body.meetingLng));
      assert.ok(Number.isFinite(body.destinationLat));
      assert.ok(Number.isFinite(body.destinationLng));
      return {ride:{id:99,...body}};
    }
    throw Error('unexpected API '+path);
  },
  tab:id=>{tabCalled=id;},
  loadRides:async()=>{},
  loadTrip:async()=>{},
  Promise,
  Number,
  Math,
  Error,
  setTimeout,
  clearTimeout,
};
context.window.__addressSearchResults={};
vm.createContext(context);
vm.runInContext(fs.readFileSync('/mnt/data/cg_functions.js','utf8'),context);

(async()=>{
  // Test 1: magnifier search auto-selects first result and saves coordinates.
  await context.searchAddress('meet');
  assert.deepStrictEqual(JSON.parse(JSON.stringify(context.coords.meet)),{lat:24.9937,lng:121.301});
  assert.ok(elements.meetSearchStatus.textContent.includes('已定位') || elements.meetSearchStatus.textContent.includes('已採用'));

  // reset so createRide must geocode BOTH fields itself
  context.coords.meet=null; context.coords.dest=null;
  await context.createRide();
  assert.equal(tabCalled,'trip');
  assert.ok(elements.createStatus.textContent.includes('已建立共乘'));
  assert.equal(elements.createRideBtn.disabled,false);
  assert.equal(elements.createRideBtn.textContent,'建立共乘');
  assert.equal(calls.filter(c=>c.path.startsWith('/geocode/')).length,3); // 1 manual + 2 auto
  assert.equal(calls.filter(c=>c.path==='/rides/').length,1);
  console.log('PASS: magnifier search');
  console.log('PASS: createRide auto geocode + POST /rides/');
  console.log('PASS: success switches to trip and restores button');
})().catch(e=>{console.error(e);process.exit(1)});
