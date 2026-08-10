#!/usr/bin/env python3
"""Clarify the proposal as a data → analysis → output → strategy pipeline."""
from pathlib import Path
import re
import sys
import zipfile
from lxml import etree

if len(sys.argv) != 3:
    raise SystemExit('usage: upgrade_methods_hwpx.py INPUT.hwpx OUTPUT.hwpx')

replacements = {
    ' 적용 분석 기법': ' 데이터 결합·분석·산출물',
    '분석 단계': '결합 데이터', '적용 기법': '분석 방법', '제안 산출물': '진단 결과',
    '상권 범위 설정': '상권 경계·연결성', 'GIS 버퍼·공간결합': '보행 네트워크 서비스권·공간조인', '후보 상권 경계 지도': '상권 경계·정류장 연결도',
    '유입·접근성 진단': '유입·접근성', '반경별 승하차·거리 분석': 'Hansen 접근성 지수·커널밀도추정(KDE)', '유입 잠재력 비교표': '유입 잠재력·접근성 격차',
    '업종 구조 진단': '업종 구조', '업종별 빈도·구성비·밀도 분석': 'LQ·Shannon 엔트로피·Gi* 핫스팟', '과밀·공백·특화 업종 목록': '과밀·공백·특화 업종',
    '소비 구조 진단': '소비 수요', '인천e음 구성비·요일 효과·군구 비교': '업종별 소비구성비·요일별 중앙값·변동계수(CV)', '미추홀구 소비 특성 기준선': '업종별 소비 기준선·요일별 변동',
    '우선순위 선정': '통합 우선순위', '다기준 의사결정과 지표 비교': '표준화 지수·AHP-TOPSIS (K-means는 보조)', '상권별 실행 후보 우선순위': '우선순위·상권 유형',
    ' 진단 결과별 전략': ' 진단 결과를 전략으로 전환',
    '진단 유형': '진단 신호', '판단 근거': '전략 방향', '우선 전략': '실행 예',
    '통과 유입형': '유입↑·소비전환↓', '유입 잠재력은 높으나 소비·체류가 낮음': '통과 유입을 체류·구매로 전환', '환승-골목-지하상가 보행 동선과 단시간 소비형 공동 혜택': '역-골목 연결 동선·공동 쿠폰',
    '생활소비 안정형': '생활수요↑·업종공백', '주거수요와 생활업종 비중이 높음': '생활서비스 공백을 우선 보완', '시장·골목 연계와 생활서비스 공백 업종 보완': '시장-골목 묶음상품·공백업종 유치',
    '청년·시간대 특화형': '대학수요↑·시간대 변동', '대학 접근성이 높고 특정 기간·요일 수요 변동이 큼': '수요가 큰 시간대에 집중', '학기·축제·야간 수요형 프로그램과 문화 콘텐츠 연계': '학기·야간 공동 프로모션',
    '업종 과밀형': '업종집중↑·차별성↓', '특정 업종 비중이 높고 점포당 성과가 낮음': '과밀업종의 차별화·전환', '업종전환 컨설팅과 공동마케팅, 차별화 업종 유도': '업종전환 컨설팅·공동브랜딩',
    '소비 수요 공백형': '정책 효과 검증', '유입·배후수요 대비 관련 업종 공급이 부족함': '사업 전후 변화로 지속·보완 판단', '팝업 운영으로 수요 검증 후 우선 유치 업종 제안': '세분 소비자료 확보 시 DID 검증',
    '   - 주안역세권은 유입-소비 전환, 신기시장 일대는 생활소비 연계, 인하대·용현동은 청년·시간대 특화를 우선 가설로 검증함.': '※ 후보 상권별로 위 진단 신호에 맞는 전략을 선택·조합함.',
    '    ※ 상권 단위 소비 자료가 없으므로 전략은 현 단계에서 검증 대상 가설로 제시함.': '※ 공개 소비자료는 군·구 단위이므로 상권별 전략은 실행 가설로 제시함.',
    '     * 세분화된 소비 집계자료 확보 시 사업 전후 소비 변화와 업종별 효과를 추가 검증함.': '* 세분 소비자료가 확보되면 사업 전후 변화는 DID로 검증함.',
}
source, output = map(Path, sys.argv[1:])
ns = {'hp': 'http://www.hancom.co.kr/hwpml/2011/paragraph'}

with zipfile.ZipFile(source, 'r') as src, zipfile.ZipFile(output, 'w') as dst:
    for info in src.infolist():
        data = src.read(info.filename)
        if info.filename == 'Contents/header.xml':
            data = re.sub(rb'(<hh:font\b[^>]*\bface=")[^"]*(")', lambda m: m.group(1) + '맑은 고딕'.encode() + m.group(2), data)
            data = re.sub(rb'(<hh:font\b(?=[^>]*\bid="3")[^>]*\bface=")[^"]*(")', lambda m: m.group(1) + 'HY견고딕'.encode() + m.group(2), data)
        elif info.filename == 'Contents/section0.xml':
            tree = etree.fromstring(data)
            changed = 0
            method_tables, strategy_tables = set(), set()
            for t in tree.xpath('.//hp:t', namespaces=ns):
                if t.text in replacements:
                    t.text = replacements[t.text]
                    paragraph = t.xpath('ancestor::hp:p[1]', namespaces=ns)[0]
                    for line in paragraph.xpath('./hp:linesegarray', namespaces=ns):
                        paragraph.remove(line)
                    table = t.xpath('ancestor::hp:tbl[1]', namespaces=ns)
                    if table:
                        if t.text in {'결합 데이터', '분석 방법', '진단 결과'}:
                            method_tables.add(table[0])
                        if t.text in {'진단 신호', '전략 방향', '실행 예'}:
                            strategy_tables.add(table[0])
                    changed += 1
            if changed != len(replacements):
                raise RuntimeError(f'Expected {len(replacements)} method labels; changed {changed}.')
            # Recalculate only changed tables so the compact labels can wrap without clipping.
            for table in method_tables:
                rows = table.xpath('./hp:tr', namespaces=ns)
                for row in rows[1:]:
                    for size in row.xpath('./hp:tc/hp:cellSz', namespaces=ns):
                        size.set('height', '4300')
                table.xpath('./hp:sz', namespaces=ns)[0].set('height', str(2379 + 5 * 4300))
            for table in strategy_tables:
                rows = table.xpath('./hp:tr', namespaces=ns)
                for row in rows[1:]:
                    for size in row.xpath('./hp:tc/hp:cellSz', namespaces=ns):
                        size.set('height', '3600')
                table.xpath('./hp:sz', namespaces=ns)[0].set('height', str(2379 + 5 * 3600))
            data = etree.tostring(tree, xml_declaration=True, encoding='UTF-8', standalone=True)
        clone = zipfile.ZipInfo(info.filename, info.date_time)
        clone.compress_type = zipfile.ZIP_STORED if info.filename == 'mimetype' else info.compress_type
        clone.external_attr, clone.comment = info.external_attr, info.comment
        dst.writestr(clone, data)
