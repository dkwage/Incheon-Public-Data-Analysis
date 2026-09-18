"""사용자 경계로 전체 점포 스냅샷을 재집계한다. .venv/bin/python analyze_inha_boundary.py"""
from pathlib import Path
import hashlib
import json
import math

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'outputs/inha'


def orient(a, b, c):
    return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])


def on_segment(a, b, p):
    return (abs(orient(a, b, p)) <= 1e-8
            and min(a[0], b[0])-1e-8 <= p[0] <= max(a[0], b[0])+1e-8
            and min(a[1], b[1])-1e-8 <= p[1] <= max(a[1], b[1])+1e-8)


def validate_ring(ring):
    if len(ring) < 4 or ring[0] != ring[-1]:
        raise ValueError('닫힌 다각형이 필요합니다.')
    if not all(len(p) == 2 and all(math.isfinite(v) for v in p) for p in ring):
        raise ValueError('유한한 2차원 좌표가 필요합니다.')
    vertices = ring[:-1]
    if len(set(map(tuple, vertices))) != len(vertices):
        raise ValueError('중복 꼭짓점')
    for i, (a, b) in enumerate(zip(ring, ring[1:])):
        for j, (c, d) in enumerate(zip(ring, ring[1:])):
            if j <= i+1 or (i == 0 and j == len(vertices)-1):
                continue
            if (orient(a,b,c)*orient(a,b,d) < 0 and orient(c,d,a)*orient(c,d,b) < 0
                    or any((on_segment(a,b,c), on_segment(a,b,d), on_segment(c,d,a), on_segment(c,d,b)))):
                raise ValueError('교차하거나 접촉하는 다각형 변')
    if abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(ring,ring[1:]))) < 1e-8:
        raise ValueError('면적이 0인 다각형')


def contains(p, ring):
    """경계 위 점을 포함하는 ray casting; 오목 다각형도 처리한다."""
    inside = False
    for a, b in zip(ring, ring[1:]):
        if on_segment(a, b, p):
            return True
        if (a[1] > p[1]) != (b[1] > p[1]):
            x = a[0] + (p[1]-a[1])*(b[0]-a[0])/(b[1]-a[1])
            if p[0] < x:
                inside = not inside
    return inside


def edge_distance(p, ring):
    distances = []
    p = np.asarray(p)
    for a, b in zip(ring, ring[1:]):
        a, b = np.asarray(a), np.asarray(b)
        t = np.clip(np.dot(p-a, b-a)/np.dot(b-a, b-a), 0, 1)
        distances.append(float(np.linalg.norm(p-(a+t*(b-a)))))
    return min(distances)


def self_check():
    square = [[0,0],[10,0],[10,10],[0,10],[0,0]]
    validate_ring(square)
    assert contains([5,5], square) and contains([0,5], square)
    assert contains([0,0], square) and not contains([-1,5], square)
    concave = [[0,0],[10,0],[10,4],[4,4],[4,10],[0,10],[0,0]]
    validate_ring(concave)
    assert not contains([7,7], concave) and contains([2,7], concave)
    assert contains([2,7], list(reversed(concave)))
    assert edge_distance([5,5], square) == 5 and edge_distance([-1,5], square) == 1
    for bad in ([[0,0],[10,10],[0,10],[10,0],[0,0]], [[0,0],[1,0],[2,0],[0,0]]):
        try:
            validate_ring(bad)
        except ValueError:
            pass
        else:
            raise AssertionError('잘못된 경계가 통과했습니다.')


def category_table(frame, district, level):
    code, name = f'inds{level}clsCd', f'inds{level}clsNm'
    result = district.groupby([code,name]).size().rename('district_count').reset_index()
    counts = frame.groupby(code).size()
    result['store_count'] = result[code].map(counts).fillna(0).astype(int)
    result['store_share'] = result.store_count / len(frame)
    result['district_share'] = result.district_count / len(district)
    result['LQ'] = result.store_share / result.district_share
    result['small_count'] = result.store_count < 5
    assert result.store_count.sum() == len(frame)
    assert np.isclose(result.store_share.sum(), 1)
    assert np.isclose((result.LQ*result.district_share).sum(), 1)
    return result.sort_values(['store_count',code], ascending=[False,True])


def main():
    self_check()
    OUT.mkdir(exist_ok=True, parents=True)
    boundary_bytes = (ROOT/'data/inha_boundary.geojson').read_bytes()
    feature = json.loads(boundary_bytes)
    if feature.get('type') != 'Feature' or feature.get('geometry',{}).get('type') != 'Polygon':
        raise ValueError('GeoJSON Polygon Feature가 필요합니다.')
    rings = feature['geometry']['coordinates']
    if len(rings) != 1:
        raise ValueError('현재 분석기는 구멍 없는 단일 다각형을 지원합니다.')
    ring = rings[0]
    if not all(len(p)==2 and 126 < p[0] < 127 and 37 < p[1] < 38 for p in ring):
        raise ValueError('인천 지역의 [경도, 위도] 좌표를 확인하세요.')
    origin = np.mean(ring[:-1], axis=0)
    # ponytail: 1km 미만 국지 경계의 근사 거리·면적; 넓은 범위는 투영 GIS로 교체.
    scale = np.array([math.cos(math.radians(origin[1])),1])*math.pi/180*6371000
    xy = lambda coords: (np.asarray(coords, dtype=float)-origin)*scale
    projected = xy(ring).tolist()
    validate_ring(projected)
    area = abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(projected,projected[1:]))) / 2
    meta = json.loads((ROOT/'data/raw/district_stores.json').read_text())
    stores = pd.DataFrame(meta['rows'])
    assert meta['complete'] and meta['total'] == len(stores)
    assert stores.bizesId.notna().all() and stores.bizesId.is_unique
    assert stores.signguCd.astype(str).eq('28177').all()
    assert stores[['indsLclsCd','indsMclsCd','indsSclsCd','adongCd','ldongCd']].notna().all().all()
    coords = stores[['lon','lat']].apply(pd.to_numeric, errors='raise').to_numpy()
    assert np.isfinite(coords).all()
    positions = xy(coords)
    mask = np.array([contains(p, projected) for p in positions])
    # 전 점포를 경계와 대조하므로 기존 1km 지도 자료의 범위에 의존하지 않는다.
    selected = stores.loc[mask].copy()
    assert len(selected) > 0
    near_bbox = ((positions >= np.min(projected,axis=0)-10) & (positions <= np.max(projected,axis=0)+10)).all(axis=1)
    review = stores.loc[near_bbox].copy()
    review['boundary_distance_m_approx'] = [edge_distance(p,projected) for p in positions[near_bbox]]
    review['inside_boundary'] = mask[near_bbox]
    review = review[review.boundary_distance_m_approx <= 10].sort_values('boundary_distance_m_approx')
    selected.to_csv(OUT/'stores.csv',index=False)
    review.to_csv(OUT/'boundary_review_10m.csv',index=False)
    tables = {}
    for level in ['L','M','S']:
        tables[level] = category_table(selected,stores,level)
        tables[level].to_csv(OUT/f'industries_{level}.csv',index=False)
    dong = selected.groupby(['adongCd','adongNm','ldongCd','ldongNm']).size().rename('store_count').reset_index()
    dong.to_csv(OUT/'dong_links.csv', index=False)
    pop = pd.read_csv(ROOT/'outputs/population_dong_summary.csv',dtype={'dong_code':str,'month':str})
    links = selected.groupby(['adongCd','adongNm']).size().rename('boundary_store_count').reset_index()
    links['dong_code'] = links.adongCd.astype(str)+'00'
    context = links.merge(pop,on='dong_code',how='left',validate='one_to_many',indicator=True)
    assert context['_merge'].eq('both').all()
    assert context.apply(lambda r:r.region_name.split()[-1]==r.adongNm,axis=1).all()
    context.drop(columns='_merge').assign(population_scope='행정동 전체; 상권 인구 아님').to_csv(OUT/'population_context.csv',index=False)
    centers = pd.read_csv(ROOT/'outputs/zone_centers.csv')
    c = centers[centers.zone.eq('인하대후문')].iloc[0]
    a,b = np.radians(coords[:,1]),np.radians(coords[:,0])
    ca,cb = np.radians([c.lat,c.lon])
    h = np.sin((a-ca)/2)**2+np.cos(a)*np.cos(ca)*np.sin((b-cb)/2)**2
    distance = 2*6371000*np.arcsin(np.sqrt(np.clip(h,0,1)))
    comparison = []
    for radius in [300,500,1000]:
        circle = distance <= radius
        comparison.append(dict(radius_m=radius,circle_stores=int(circle.sum()),polygon_stores=len(selected),both=int((mask&circle).sum()),polygon_only=int((mask&~circle).sum()),circle_only=int((~mask&circle).sum())))
    pd.DataFrame(comparison).to_csv(OUT/'boundary_comparison.csv',index=False)
    summary = dict(standard_month=meta['standard_month'],district_stores=len(stores),boundary_stores=len(selected),vertices=len(ring)-1,area_m2_approx=area,boundary_sha256=hashlib.sha256(boundary_bytes).hexdigest(),boundary_reason=feature.get('properties',{}).get('reason',''),boundary_review_10m=len(review),review_inside=int(review.inside_boundary.sum()),review_outside=int((~review.inside_boundary).sum()))
    (OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
    write_report(summary,tables,dong,context,comparison,feature,stores,mask)
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    print(tables['M'].head(12).to_string(index=False))
    print(dong.to_string(index=False))


def write_report(s,tables,dong,context,comparison,feature,stores,mask):
    lines = ['# 인하대 후문 사용자 경계 기초진단','',
             '**판단: 현재 자료로 상권의 문제·쇠퇴 여부는 아직 확정할 수 없다. 아래는 2026년 6월 점포 구조 진단이다.**','',
             f"- 미추홀구 전체 {s['district_stores']:,}개 중 사용자 경계 안 **{s['boundary_stores']:,}개**.",
             f"- 꼭짓점 {s['vertices']}개, 근사 면적 {s['area_m2_approx']/10000:.2f}ha. 면적은 국지 평면 근사이며 보행권·상업용 면적이 아니다.",
             '- 경계 위 점 포함. 경계 파일과 SHA-256을 보존해 재현 가능하게 했다.',
             '- 경계 설정 이유는 원본에서 미기입 상태다. 포함·제외 기준을 결과 해석 전에 기록할 필요가 있다.',
             f"- 경계에서 10m 이내 점포 {s['boundary_review_10m']}개(내부 {s['review_inside']}, 외부 {s['review_outside']})를 지도 확인 대상으로 분리했다. 10m는 검토용 폭이며 좌표오차 추정치가 아니다.",
             '', '## 업종 구성', '', '| 대분류 | 점포 수 | 구성비 |','|---|---:|---:|']
    for r in tables['L'].itertuples():
        if r.store_count: lines.append(f'| {r.indsLclsNm} | {r.store_count} | {r.store_share:.1%} |')
    lines += ['', '### 중분류 점포 수 상위 12개', '', '| 업종 | 점포 수 | 구성비 | 구 전체 대비 LQ |','|---|---:|---:|---:|']
    for r in tables['M'].head(12).itertuples():
        lines.append(f'| {r.indsMclsNm} | {r.store_count} | {r.store_share:.1%} | {r.LQ:.2f} |')
    lines += ['', 'LQ는 업종 구성의 특화 지표다. 과밀·공급부족·수익성·쇠퇴의 증거가 아니다. 전체 업종과 5개 미만 표시는 CSV에 있다.', '', '## 카드자료 연결 후보', '']
    for r in dong.itertuples():
        lines.append(f'- 점포 주소 기준 행정동 **{r.adongNm} ({r.adongCd})**, 법정동 **{r.ldongNm} ({r.ldongCd})**: {r.store_count}개.')
    lines += ['', '점포 주소로 확인한 관련 동 목록이다. 동 경계 폴리곤과 교차 검증한 결과는 아니며 점포가 없는 교차 동은 포착하지 못한다. 카드 UMD_CD의 행정동/법정동 정의에 맞춰 연결해야 한다.', '', '관련 행정동 전체 주민 참고:', '']
    for r in context[context.month.eq('202608')].itertuples():
        lines.append(f'- {r.adongNm}: {r.total_population:,}명, 20~39세 {r.age_20_39_pct:.1f}%, 65세 이상 {r.age_65_plus_pct:.1f}%. 상권 인구·학생 수가 아니다.')
    lines += ['', '## 기존 반경과 비교', '', '| 반경 | 기존 점포 | 공통 점포 | 사용자 경계에만 포함 | 기존 반경에만 포함 |', '|---|---:|---:|---:|---:|']
    for r in comparison:
        lines.append(f"| {r['radius_m']}m | {r['circle_stores']} | {r['both']} | {r['polygon_only']} | {r['circle_only']} |")
    lines += ['', '이는 경계 변경에 따른 포함 범위 차이이며 점포 감소나 폐업이 아니다.', '', '## 다음 단계: 문제를 검증하기 위한 자료', '',
              '| 문제 후보 | 현재 판단 | 다음 근거 |','|---|---|---|',
              '| 지속적인 소비 위축 | 판단 유보 | 관련 동 카드 금액·건수의 다년 추이, 전년 동월·유사 지역 비교, 후문 현장 대조 |',
              '| 폐업·공실 증가 | 판단 유보 | 과거 점포·인허가 개폐업 이력 및 반복 현장 확인; 인허가 업종 범위 명시 |',
              '| 특정 시기 영업 어려움 | 판단 유보 | 학기·방학 달력, 월별 소비, 상인 의견; 단순 계절성 구분 |',
              '| 이용 동선·편의 문제 | 판단 유보 | 같은 구간·시간 길이의 관찰 및 이용자 의견 |', '',
              '우선 경계 인접 점포와 실제 골목 범위를 지도에서 확인하고, 시간대를 달리한 탐색 현장조사를 진행한다. 관련 동 카드자료는 후문 문제의 직접 증거가 아니라 배경 근거로 사용한다. 문제가 확인된 뒤 원인 후보 검증과 대응 방안으로 넘어간다.', '',
              '## 재실행', '', '`.venv/bin/python analyze_inha_boundary.py`', '',
              '원본: `data/inha_boundary.geojson`, `data/raw/district_stores.json`, `outputs/population_dong_summary.csv`. 결과: `outputs/inha/`.',
              '공간 포함·경계점·오목 다각형·교차 거부·경계 거리 및 집계 합계·인구 연결 검증을 실행한다.']
    (OUT/'diagnosis.md').write_text('\n'.join(lines)+'\n')
    # 기존 지도와 같은 Leaflet/OSM 구성; 외부로 보내는 것은 현재 화면의 타일 요청뿐이다.
    minx,miny = np.min(feature['geometry']['coordinates'][0],axis=0)
    maxx,maxy = np.max(feature['geometry']['coordinates'][0],axis=0)
    nearby = stores.lon.between(minx-.001,maxx+.001)&stores.lat.between(miny-.001,maxy+.001)
    map_stores = stores.loc[nearby,['bizesNm','indsMclsNm','rdnmAdr','lon','lat']].copy()
    map_stores['inside'] = mask[nearby]
    review_ids = set(pd.read_csv(OUT/'boundary_review_10m.csv',dtype={'bizesId':str}).bizesId)
    map_stores['review'] = stores.loc[nearby,'bizesId'].isin(review_ids)
    data = json.dumps({'boundary':feature,'stores':map_stores.to_dict('records')},ensure_ascii=False).replace('<','\\u003c')
    page = '''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>인하대 후문 경계 확정 후 점포 현황</title><link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<style>body{margin:0;font:15px system-ui}header{padding:16px;background:#f3f6fa}h1{font-size:20px}#map{height:75vh}p{margin:8px 0}</style>
<header><h1>인하대 후문 · 사용자 경계 기준 점포 현황</h1><p>__COUNT__개 · 2026년 6월 · 빨강: 경계 내부 / 회색: 주변 점포</p>
<p>원형 반경과 점포 수가 다른 것은 범위 차이이며 쇠퇴가 아닙니다. 카드매출·공실·폐업은 아직 미확인입니다.</p><p id="status" role="status">지도 로딩 중</p></header><div id="map"></div>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script><script>
if(location.protocol==='file:'){document.getElementById('status').textContent='로컬 서버에서 /inha/map.html을 열어주세요.';}else{
const D=__DATA__;
const esc=x=>String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const map=L.map('map',{preferCanvas:true,zoomAnimation:false,fadeAnimation:false});
const boundary=L.geoJSON(D.boundary,{style:{color:'#dc2626',fillOpacity:.04,weight:3}}).addTo(map);
map.fitBounds(boundary.getBounds(),{padding:[35,35]});
let failed=false;
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19,attribution:'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'}).on('tileerror',()=>{failed=true;document.getElementById('status').textContent='일부 배경지도 로딩 실패';}).on('load',()=>{if(!failed)document.getElementById('status').textContent='점포를 클릭하면 업종·주소가 표시됩니다.';}).addTo(map);
const inside=L.layerGroup().addTo(map),outside=L.layerGroup().addTo(map),review=L.layerGroup();
for(const s of D.stores)L.circleMarker([s.lat,s.lon],{radius:s.inside?4:3,color:s.inside?'#dc2626':'#64748b',weight:0,fillOpacity:s.inside?.8:.35}).bindPopup('<b>'+esc(s.bizesNm)+'</b><br>'+esc(s.indsMclsNm)+'<br>'+esc(s.rdnmAdr)+'<br>'+(s.inside?'경계 내부':'경계 외부')).addTo(s.inside?inside:outside);
for(const s of D.stores.filter(s=>s.review))L.circleMarker([s.lat,s.lon],{radius:7,color:'#d97706',weight:2,fillOpacity:.1}).bindPopup(esc(s.bizesNm)+'<br>경계 10m 이내 · '+(s.inside?'내부':'외부')).addTo(review);
L.control.layers(null,{'사용자 경계':boundary,'경계 안 점포':inside,'주변 점포':outside,'경계 10m 이내 확인 대상':review},{collapsed:false}).addTo(map);L.control.scale({imperial:false}).addTo(map);
window.inhaData=D;
}
</script></html>'''
    (OUT/'map.html').write_text(page.replace('__COUNT__',str(s['boundary_stores'])).replace('__DATA__',data))


if __name__ == '__main__':
    main()
