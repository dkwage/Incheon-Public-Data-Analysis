#!/usr/bin/env python3
"""Apply the Incheon comprehensive-report layout to the Michuhol proposal."""
from copy import deepcopy
from pathlib import Path
import shutil
import subprocess
import tempfile
from lxml import etree

ROOT = Path(__file__).resolve().parents[1]
SKILL = Path('/Users/dkwage/vscode/hwpx-rekian/hwpx/scripts')
TEMPLATE = Path('/Users/dkwage/Downloads/인천종합보고양식.hwpx')
OUT = ROOT / 'docs/미추홀구_상권활성화_데이터분석_인천종합보고양식_제안서.hwpx'
NS = {'hp': 'http://www.hancom.co.kr/hwpml/2011/paragraph', 'hs': 'http://www.hancom.co.kr/hwpml/2011/section'}
HP, HS = NS['hp'], NS['hs']


def q(tag): return f'{{{HP}}}{tag}'


def para(pid, text='', ppr=48, cpr=65, page_break='0'):
    p = etree.Element(q('p'), id=str(pid), paraPrIDRef=str(ppr), styleIDRef='0', pageBreak=page_break, columnBreak='0', merged='0')
    run = etree.SubElement(p, q('run'), charPrIDRef=str(cpr))
    etree.SubElement(run, q('t')).text = text
    return p


def cell(pid, text, col, row, width, height, header=False):
    tc = etree.Element(q('tc'), name='', header='0', hasMargin='0', protect='0', editable='0', dirty='0', borderFillIDRef='9' if header else '3')
    sub = etree.SubElement(tc, q('subList'), id='', textDirection='HORIZONTAL', lineWrap='BREAK', vertAlign='CENTER', linkListIDRef='0', linkListNextIDRef='0', textWidth='0', textHeight='0', hasTextRef='0', hasNumRef='0')
    sub.append(para(pid, text, 3 if header else 1, 22 if header else 11))
    etree.SubElement(tc, q('cellAddr'), colAddr=str(col), rowAddr=str(row))
    etree.SubElement(tc, q('cellSpan'), colSpan='1', rowSpan='1')
    etree.SubElement(tc, q('cellSz'), width=str(width), height=str(height))
    etree.SubElement(tc, q('cellMargin'), left='141', right='141', top='141', bottom='141')
    return tc


def table(pid, rows, widths):
    tbl = etree.Element(q('tbl'), id=str(pid), zOrder='0', numberingType='TABLE', textWrap='TOP_AND_BOTTOM', textFlow='BOTH_SIDES', lock='0', dropcapstyle='None', pageBreak='CELL', repeatHeader='1', rowCnt=str(len(rows)), colCnt=str(len(widths)), cellSpacing='0', borderFillIDRef='3', noAdjust='0')
    height = 3000 * len(rows)
    etree.SubElement(tbl, q('sz'), width=str(sum(widths)), widthRelTo='ABSOLUTE', height=str(height), heightRelTo='ABSOLUTE', protect='0')
    etree.SubElement(tbl, q('pos'), treatAsChar='1', affectLSpacing='0', flowWithText='1', allowOverlap='0', holdAnchorAndSO='0', vertRelTo='PARA', horzRelTo='PARA', vertAlign='TOP', horzAlign='LEFT', vertOffset='0', horzOffset='0')
    etree.SubElement(tbl, q('outMargin'), left='141', right='141', top='141', bottom='141')
    etree.SubElement(tbl, q('inMargin'), left='141', right='141', top='141', bottom='141')
    n = pid + 1
    for r, values in enumerate(rows):
        tr = etree.SubElement(tbl, q('tr'))
        h = 3000 if r == 0 else 4300
        for c, value in enumerate(values):
            tr.append(cell(n, value, c, r, widths[c], h, r == 0)); n += 1
    return tbl


def table_para(pid, rows, widths):
    p = para(pid, '', 22, 1)
    p[0].append(table(pid + 10000, rows, widths))
    return p


def chapter(pid, roman, title):
    p = para(pid, '', 0, 1)
    tbl = etree.SubElement(p[0], q('tbl'), id=str(pid + 20000), zOrder='0', numberingType='TABLE', textWrap='TOP_AND_BOTTOM', textFlow='BOTH_SIDES', lock='0', dropcapstyle='None', pageBreak='CELL', repeatHeader='0', rowCnt='1', colCnt='3', cellSpacing='0', borderFillIDRef='7', noAdjust='0')
    etree.SubElement(tbl, q('sz'), width='47626', widthRelTo='ABSOLUTE', height='3248', heightRelTo='ABSOLUTE', protect='0')
    etree.SubElement(tbl, q('pos'), treatAsChar='1', affectLSpacing='0', flowWithText='1', allowOverlap='0', holdAnchorAndSO='0', vertRelTo='PARA', horzRelTo='PARA', vertAlign='TOP', horzAlign='LEFT', vertOffset='0', horzOffset='0')
    etree.SubElement(tbl, q('outMargin'), left='141', right='141', top='141', bottom='141'); etree.SubElement(tbl, q('inMargin'), left='141', right='141', top='141', bottom='141')
    tr = etree.SubElement(tbl, q('tr'))
    specs = [(roman, 3558, 16, 62), ('', 728, 5, 63), (title, 43340, 5, 19)]
    for c, (text, width, ppr, cpr) in enumerate(specs):
        tc = etree.SubElement(tr, q('tc'), name='', header='0', hasMargin='0', protect='0', editable='0', dirty='0', borderFillIDRef=str(16-c if c < 2 else 14))
        sub = etree.SubElement(tc, q('subList'), id='', textDirection='HORIZONTAL', lineWrap='BREAK', vertAlign='CENTER', linkListIDRef='0', linkListNextIDRef='0', textWidth='0', textHeight='0', hasTextRef='0', hasNumRef='0')
        sub.append(para(pid + 1 + c, text, ppr, cpr))
        etree.SubElement(tc, q('cellAddr'), colAddr=str(c), rowAddr='0'); etree.SubElement(tc, q('cellSpan'), colSpan='1', rowSpan='1')
        etree.SubElement(tc, q('cellSz'), width=str(width), height='3248'); etree.SubElement(tc, q('cellMargin'), left='141', right='141', top='141', bottom='141')
    return p


def main():
    with tempfile.TemporaryDirectory() as td:
        work = Path(td) / 'work'
        subprocess.run(['python', str(SKILL/'office/unpack.py'), str(TEMPLATE), str(work)], check=True)
        src = etree.parse(str(work/'Contents/section0.xml'))
        root = etree.Element(f'{{{HS}}}sec', nsmap=src.getroot().nsmap)
        first = src.xpath('//hp:p[1]', namespaces=NS)[0]
        sec_run = etree.Element(q('run'), charPrIDRef='58')
        sec_run.append(deepcopy(first.xpath('.//hp:secPr', namespaces=NS)[0]))
        sec_run.append(deepcopy(first.xpath('.//hp:ctrl[hp:colPr]', namespaces=NS)[0]))
        opener = etree.Element(q('p'), id='1', paraPrIDRef='66', styleIDRef='4', pageBreak='0', columnBreak='0', merged='0')
        opener.append(sec_run); opener.append(etree.Element(q('run'), charPrIDRef='58'))
        root.append(opener)

        # Cover
        root.append(table_para(10, [['종합보고서']], [47626]))
        root.append(para(11, '', 29, 56)); root.append(para(12, '', 29, 56)); root.append(para(13, '', 29, 56))
        root.append(para(14, '미추홀구 상권 활성화', 28, 71)); root.append(para(15, '데이터 분석 추진 제안서', 28, 71))
        root.append(para(16, '', 29, 56)); root.append(para(17, '수신  미추홀구청장 귀하', 48, 65)); root.append(para(18, '작성  인하대학교 데이터사이언스학과', 48, 65)); root.append(para(19, '2026. 8.', 48, 65))
        root.append(para(20, '', 29, 56)); root.append(para(21, '', 29, 56))

        root.append(chapter(30, 'Ⅰ', '제안 개요'))
        root.append(para(34, '1. 제안 목적', 47, 68)); root.append(para(35, '○ 유동·소비·점포 데이터를 결합하여 상권별 여건을 진단하고, 예산 투입 우선순위와 실행 전략을 제시하고자 함.', 48, 65))
        root.append(para(36, '2. 비교 후보 상권', 47, 68))
        root.append(table_para(40, [['후보 상권', '비교 관점', '분석 초점'], ['주안역 일대', '환승·생활권 중심', '시간대별 유입 대비 체류·소비 전환'], ['신기시장 일대', '전통시장 중심', '시장 방문객의 주변 상권 확산'], ['인하대·용현동 일대', '대학·주거 혼합', '청년 수요와 업종 구성의 적합성']], [12000, 15500, 20126]))

        root.append(chapter(60, 'Ⅱ', '활용 데이터 및 분석 방법'))
        root.append(para(64, '1. 즉시 활용 가능한 공개 데이터', 47, 68))
        root.append(table_para(70, [['데이터', '활용 내용', '제공 위치'], ['버스 정류소 승하차', '시간대별 대중교통 유입 잠재력', '공공데이터포털'], ['인천e음 결제금액', '미추홀구 업종별·요일별 소비 구조', '공공데이터포털'], ['상가(상권)정보', '점포 밀도·업종 구성·공실 위험', '공공데이터포털']], [15000, 21000, 11626]))
        root.append(para(76, '2. 분석·모델링 기법', 47, 68))
        root.append(table_para(80, [['분석 단계', '적용 기법', '전략 도출 결과'], ['상권 진단', 'GIS 반경 결합·표준화 지수', '유입·소비·점포 경쟁의 상권 프로필'], ['유형화', 'K-means 군집분석·주성분분석', '성장·전환·정비 등 지원 유형 분류'], ['우선순위', '회귀분석·랜덤포레스트·SHAP', '소비 활성화와 연관된 요인 및 투자 우선순위']], [12000, 19000, 16626]))
        root.append(para(86, '※ 정류장 승하차는 전체 보행량이 아닌, 공개·반복 수집이 가능한 대중교통 기반 유입 지표로 활용함.', 48, 65))

        root.append(chapter(100, 'Ⅲ', '상권별 전략 도출 방향'))
        root.append(para(104, '1. 전략 설계 원칙', 47, 68)); root.append(para(105, '○ 단순한 유동인구 순위가 아니라 유입→체류→소비 전환의 병목을 찾아 상권 유형별로 차등 지원함.', 48, 65))
        root.append(table_para(110, [['상권 유형', '판단 신호', '우선 전략'], ['환승·생활권형', '유입은 높으나 소비 전환이 낮음', '동선 안내·테이크아웃·시간대 특화 업종 지원'], ['시장 연계형', '시장 유입 대비 주변 소비 확산이 낮음', '시장-골목 연계 쿠폰·공동상품·보행동선 개선'], ['대학·주거 혼합형', '청년 수요와 업종 구성이 불일치', '저녁·주말 콘텐츠 및 청년 친화 업종 유치']], [12000, 17500, 18126]))
        root.append(para(116, '2. 인천e음 데이터 추가 활용', 47, 68)); root.append(para(117, '○ 월 단위 일별·업종별 결제금액으로 요일효과, 소비 집중 업종, 정책 전후 변화를 측정하고 사업 성과지표로 관리할 수 있음.', 48, 65))

        root.append(chapter(130, 'Ⅳ', '추진 요청 사항 및 데이터 출처'))
        root.append(para(134, '1. 추진 절차', 47, 68))
        root.append(table_para(140, [['기간', '주요 내용', '산출물'], ['1개월차', '데이터 정비·공간 결합·후보 상권 확정', '상권 기초진단'], ['2개월차', '유형화·영향요인 분석·현장 검토', '상권별 전략안'], ['3개월차', '부서 협의·성과지표 설정', '실행 우선순위 및 대시보드 초안']], [10000, 25000, 12626]))
        root.append(para(146, '2. 협조 요청', 47, 68)); root.append(para(147, '○ 후보 상권의 범위와 현안, 기존 지원사업 정보를 공유해 주시면 분석 결과를 현장 여건에 맞게 보정하겠음.', 48, 65))
        root.append(para(148, '3. 주요 데이터 출처', 47, 68))
        for i, url in enumerate(['https://www.data.go.kr/data/15048264/fileData.do', 'https://www.data.go.kr/data/15067973/fileData.do', 'https://www.data.go.kr/dataset/15012005/openapi.do']):
            root.append(para(150 + i, '○ ' + url, 48, 65))

        etree.ElementTree(root).write(str(work/'Contents/section0.xml'), xml_declaration=True, encoding='UTF-8', standalone=True)
        hpf = etree.parse(str(work/'Contents/content.hpf'))
        opf = {'opf': 'http://www.idpf.org/2007/opf/'}
        hpf.xpath('//opf:title', namespaces=opf)[0].text = '미추홀구 상권 활성화 데이터 분석 추진 제안서'
        creator = hpf.xpath('//opf:meta[@name="creator"]', namespaces=opf)
        if creator:
            creator[0].text = '인하대학교 데이터사이언스학과'
        hpf.write(str(work/'Contents/content.hpf'), xml_declaration=True, encoding='UTF-8')
        subprocess.run(['python', str(SKILL/'office/pack.py'), str(work), str(OUT)], check=True)
    print(OUT)


if __name__ == '__main__': main()
