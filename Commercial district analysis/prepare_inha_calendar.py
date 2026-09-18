"""공식 홈페이지 수집 스냅샷에서 학사일정 및 월별 결합표를 생성한다."""
from datetime import date, timedelta
from pathlib import Path
import json
import re
import pandas as pd

ROOT = Path(__file__).resolve().parent
OUT = ROOT/'outputs/inha'


def dates(year, heading, text):
    explicit = re.search(r'\((\d{4})년\)', heading)
    year = int(explicit[1]) if explicit else year
    pairs = re.findall(r'(\d{2})\.(\d{2})\.', text)
    if len(pairs) not in (1, 2):
        raise ValueError(f'날짜 해석 실패: {text}')
    start = date(year, *map(int,pairs[0]))
    end_month,end_day = map(int,pairs[-1])
    end = date(year+(end_month < start.month),end_month,end_day)
    assert start <= end
    return start.isoformat(),end.isoformat()


def classify(title):
    for word, label in [('보강주간','makeup'),('중간고사','midterm'),('기말고사','final_exam'),('개강','semester_start'),('계절학기 수업','seasonal_class'),('학위수여식','graduation')]:
        if word in title:
            return label
    return 'administrative_or_other'


def main():
    assert dates(2026,'12 월 (2025년)','12.22.(월) ~ 01.14.(수)') == ('2025-12-22','2026-01-14')
    assert dates(2024,'2 월','02.29.(목)') == ('2024-02-29','2024-02-29')
    assert classify('보강주간 *이러닝 기말고사') == 'makeup'
    raw = json.loads((ROOT/'data/raw/inha_calendar_2024_2026.json').read_text())
    records = []
    for page in raw['years']:
        assert page['events']
        for e in page['events']:
            start,end = dates(page['year'],e['month_heading'],e['date_text'])
            records.append(dict(start_date=start,end_date=end,title=e['title'],event_type=classify(e['title']),source_year=page['year'],date_text=e['date_text'],source_url=raw['source_url'],retrieved_at=raw['retrieved_at']))
    df = pd.DataFrame(records)
    # 전년도 12월 일정이 다음 해 페이지에도 나오므로 주석을 제외한 제목으로 중복 제거.
    df['event_key'] = df.title.str.split('*',regex=False).str[0].str.replace(r'\s+','',regex=True)
    df = df.drop_duplicates(['start_date','end_date','event_key']).sort_values(['start_date','title'])
    df.to_csv(OUT/'academic_events_2024_2026.csv',index=False)
    days = pd.DataFrame({'date':pd.date_range('2024-01-01','2026-12-31')})
    for key in ['midterm','final_exam','makeup','seasonal_class','graduation']:
        days[key] = False
        for e in df[df.event_type.eq(key)].itertuples():
            days.loc[days.date.between(e.start_date,e.end_date),key] = True
    days['regular_term_span_inferred'] = False
    for year in [2024,2025,2026]:
        for semester in [1,2]:
            candidates = df[df.start_date.str.startswith(str(year)) & df.title.str.contains(f'{semester}학기',regex=False)]
            start = candidates[candidates.event_type.eq('semester_start')]
            end = candidates[candidates.event_type.eq('makeup')]
            assert len(start) == len(end) == 1, (year,semester)
            days.loc[days.date.between(start.start_date.iloc[0],end.end_date.iloc[0]),'regular_term_span_inferred'] = True
    days['outside_regular_term_inferred'] = ~days.regular_term_span_inferred
    days['month'] = days.date.dt.strftime('%Y%m')
    days['after_collection_date'] = days.date > pd.Timestamp(raw['retrieved_at'][:10])
    days['definition'] = '정규학기 구간=공식 개강일부터 보강주간 종료일까지(주말 포함); 분석용 추론, 실제 수업·등교일 아님'
    days.to_csv(OUT/'academic_daily_flags.csv',index=False,date_format='%Y-%m-%d')
    flags = ['regular_term_span_inferred','outside_regular_term_inferred','midterm','final_exam','makeup','seasonal_class','graduation']
    monthly = days.groupby('month')[flags].sum().add_suffix('_days')
    monthly['calendar_days'] = days.groupby('month').size()
    monthly['regular_term_share_inferred'] = monthly.regular_term_span_inferred_days/monthly.calendar_days
    monthly['card_available_through_202606'] = monthly.index <= '202606'
    assert (monthly.regular_term_span_inferred_days+monthly.outside_regular_term_inferred_days == monthly.calendar_days).all()
    assert len(days) == 1096 and len(monthly) == 36
    assert days.date.is_unique and not df.duplicated(['start_date','end_date','title']).any()
    monthly.to_csv(OUT/'academic_monthly_features.csv')
    print(f'수집 {len(records)}행 → 중복 제거 {len(df)}개 일정; 일별 {len(days)}행; 월별 {len(monthly)}행')
    print(df[(df.start_date.str.startswith('2026')) & df.event_type.ne('administrative_or_other')][['start_date','end_date','title']].to_string(index=False))


if __name__ == '__main__':
    main()
