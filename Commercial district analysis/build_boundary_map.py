"""기존 보고 지도를 재사용하여 후문 경계 편집 지도를 생성한다."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EDITOR = r'''
<script>
const panel=document.createElement('section');
panel.innerHTML=`<h2 style="font-size:18px">인하대 후문 분석 경계</h2>
<p>① 경계 그리기 → 지도에서 꼭짓점 클릭 → ② 그리기 종료 → 점을 끌어 수정 → ③ 저장</p>
<button id="drawBoundary" aria-pressed="false">경계 그리기</button>
<button id="undoBoundary">마지막 점 취소</button>
<button id="saveBoundary">GeoJSON 저장</button>
<button id="resetBoundary">초기화</button>
<label>경계 설정 이유 <input id="boundaryReason" size="45" placeholder="예: 후문 음식점 거리 포함, 대학 내부 제외"></label>
<p id="boundaryStatus" role="status" aria-live="polite"></p>
<p>표시 점포는 기존 후보지 1km 자료입니다. 경계 저장 후 구 전체 원자료로 재집계합니다. 이 경계로 읍면동 카드매출을 분할할 수는 없습니다.</p>`;
document.querySelector('header').append(panel);
const boundary=L.polygon([],{color:'#dc2626',weight:3,fillOpacity:.12,interactive:false}).addTo(map);
const handles=L.layerGroup().addTo(map);
let points=[],drawing=false,dirty=false;
const status=document.getElementById('boundaryStatus');
const orient=(a,b,c)=>(b.lng-a.lng)*(c.lat-a.lat)-(b.lat-a.lat)*(c.lng-a.lng);
function validBoundary(ps){
 if(ps.length<3)return false;
 if(!ps.every(p=>Number.isFinite(p.lat)&&Number.isFinite(p.lng)&&Math.abs(p.lat)<=90&&Math.abs(p.lng)<=180))return false;
 if(new Set(ps.map(p=>p.lat+','+p.lng)).size!==ps.length)return false;
 const on=(a,b,c)=>Math.abs(orient(a,b,c))<1e-14&&c.lng>=Math.min(a.lng,b.lng)&&c.lng<=Math.max(a.lng,b.lng)&&c.lat>=Math.min(a.lat,b.lat)&&c.lat<=Math.max(a.lat,b.lat);
 const intersects=(a,b,c,d)=>orient(a,b,c)*orient(a,b,d)<0&&orient(c,d,a)*orient(c,d,b)<0||on(a,b,c)||on(a,b,d)||on(c,d,a)||on(c,d,b);
 for(let i=0;i<ps.length;i++){
  const a=ps[i],b=ps[(i+1)%ps.length],c=ps[(i+2)%ps.length];
  if(Math.abs(orient(a,b,c))<1e-14)return false;
  for(let j=i+1;j<ps.length;j++){
   if(j===i+1||(i===0&&j===ps.length-1))continue;
   if(intersects(a,b,ps[j],ps[(j+1)%ps.length]))return false;
  }
 }
 return true;
}
function refreshBoundary(){
 boundary.setLatLngs(points);
 const valid=validBoundary(points);
 document.getElementById('saveBoundary').disabled=!valid;
 status.textContent=`꼭짓점 ${points.length}개 · `+(valid?'저장 가능':'점 3개 이상 필요 · 선 교차·중복점·일직선 꼭짓점은 수정하세요');
}
function renderHandles(){
 handles.clearLayers();
 points.forEach((p,i)=>{
  const m=L.marker(p,{draggable:true,autoPan:true,title:`꼭짓점 ${i+1}: 끌어서 수정`,icon:L.divIcon({className:'boundary-handle',html:'<span style="display:block;background:#fff;border:3px solid #dc2626;border-radius:50%;width:14px;height:14px"></span>',iconSize:[20,20],iconAnchor:[10,10]})}).addTo(handles);
  m.on('drag',()=>{points[i]=m.getLatLng();dirty=true;refreshBoundary();});
 });
 refreshBoundary();
}
document.getElementById('drawBoundary').onclick=()=>{
 drawing=!drawing;
 document.getElementById('drawBoundary').textContent=drawing?'그리기 종료':'경계 그리기';
 document.getElementById('drawBoundary').setAttribute('aria-pressed',String(drawing));
 map.getContainer().style.cursor=drawing?'crosshair':'';
};
map.on('click',e=>{if(drawing){points.push(e.latlng);dirty=true;renderHandles();}});
document.getElementById('undoBoundary').onclick=()=>{points.pop();dirty=true;renderHandles();};
document.getElementById('resetBoundary').onclick=()=>{
 if(points.length&&!confirm('현재 경계를 지울까요? 저장한 파일은 유지됩니다.'))return;
 points=[];dirty=false;renderHandles();
};
document.getElementById('boundaryReason').oninput=()=>{dirty=true;};
function boundaryFeature(){
 if(!validBoundary(points))throw new Error('유효하지 않은 경계');
 const feature=boundary.toGeoJSON(false);
 feature.properties={name:'인하대후문',boundary_type:'연구자 설정 분석 경계',reason:document.getElementById('boundaryReason').value.trim(),created_at:new Date().toISOString()};
 return feature;
}
document.getElementById('saveBoundary').onclick=()=>{
 const url=URL.createObjectURL(new Blob([JSON.stringify(boundaryFeature(),null,2)],{type:'application/geo+json'}));
 const a=document.createElement('a');a.href=url;a.download='inha_boundary.geojson';document.body.append(a);a.click();a.remove();
 setTimeout(()=>URL.revokeObjectURL(url),1000);dirty=false;
 status.textContent='다운로드를 요청했습니다. 다운로드 폴더에서 inha_boundary.geojson을 확인하세요.';
};
window.addEventListener('beforeunload',e=>{if(dirty){e.preventDefault();e.returnValue='';}});
map.setView([37.4512316667,126.6564506667],16);
map.removeLayer(groups['인하대후문 · 500m 점포']);
groups['인하대후문 · 1km 점포'].addTo(map);
refreshBoundary();
// 실행 점검: 브라우저 콘솔에서 boundarySelfCheck() 호출.
window.boundarySelfCheck=()=>{
 const p=arr=>arr.map(([lng,lat])=>({lng,lat}));
 const checks=[validBoundary(p([[0,0],[1,0],[1,1],[0,1]])),!validBoundary(p([[0,0],[1,1],[0,1],[1,0]])),!validBoundary(p([[0,0],[1,0],[2,0]])),!validBoundary(p([[0,0],[1,0],[1,1],[0,0]])),!validBoundary(p([[0,0],[1,0]]))];
 if(!checks.every(Boolean))throw new Error('경계 검증 실패');
 return '5 checks passed';
};
</script>
'''

if __name__ == '__main__':
    source = (ROOT / 'outputs/briefing_map.html').read_text(encoding='utf-8')
    assert source.count('</body>') == 1
    target = ROOT / 'outputs/inha_boundary_editor.html'
    page = source.replace('</body>', EDITOR + '</body>')
    # 파일로 직접 열면 Referer 없는 타일 요청 대신 서버 실행 안내를 표시한다.
    page = page.replace('<script>\nconst D=', '''<script>
if (location.protocol === 'file:') {
 document.querySelector('header').innerHTML = '<h1>로컬 서버로 지도를 열어주세요</h1><p>프로젝트 폴더에서 다음 명령을 실행하세요.</p><pre>python3 -m http.server 8765 --bind 127.0.0.1 --directory outputs</pre><a href="http://127.0.0.1:8765/inha_boundary_editor.html">경계 편집 지도 열기</a>';
} else {
const D=''', 1)
    page = page.replace('window.reportData=D;\n</script>', 'window.reportData=D;\n}\n</script>', 1)
    page = page.replace('const panel=document.createElement', "if (location.protocol !== 'file:') {\nconst map=window.reportMap, groups=window.reportLayers;\nconst panel=document.createElement", 1)
    page = page.replace("return '5 checks passed';\n};", "return '5 checks passed';\n};\n}", 1)
    target.write_text(page, encoding='utf-8')
    print(target)
