import re
import numpy as np
import pandas as pd
import statsmodels.api as sm


def to_bool(value):
    if isinstance(value, bool):
        return value
    if pd.isna(value):
        return False
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def safe_div(numerator, denominator):
    return np.where(denominator == 0, np.nan, numerator / denominator)


def run_ols(df, x_col, y_col, title):
    data = df[[x_col, y_col]].dropna()
    x = sm.add_constant(data[x_col])
    y = data[y_col]
    model = sm.OLS(y, x).fit()

    print("\n" + "-" * 80)
    print(title)
    print(f"표본 수: {len(data)}")
    print(f"Pearson r: {data[x_col].corr(data[y_col]):.4f}")
    print(f"Spearman r: {data[x_col].rank().corr(data[y_col].rank()):.4f}")
    print(f"기울기(beta): {model.params.get(x_col, np.nan):.6f}")
    print(f"p-value(beta): {model.pvalues.get(x_col, np.nan):.6f}")
    print(f"R-squared: {model.rsquared:.4f}")
    return model


# 1) 데이터 로드
df_raw = pd.read_csv("michuhol_analysis_raw.csv")

# 2) 타입 정리
df_raw["is_event"] = df_raw["is_event"].apply(to_bool)
df_raw["is_complaint"] = df_raw["is_complaint"].apply(to_bool)
df_raw["comment"] = df_raw["comment"].fillna("").astype(str)
df_raw["sentiment_label"] = df_raw["sentiment_label"].fillna("").astype(str)

# 3) 체리피커 프록시 정의
# 짧은 응모형 문구/정답형 템플릿을 체리피커 프록시로 사용
pattern = re.compile(r"정답|\b\d+번\b|이벤트|응모|참여|폼|마감")
df_raw["is_positive_eval"] = (
    (~df_raw["is_event"]) & (df_raw["sentiment_label"].str.contains("긍정", na=False))
)
df_raw["event_text_length"] = df_raw["comment"].str.len()
df_raw["is_cherrypick_proxy"] = df_raw["is_event"] & (
    (df_raw["event_text_length"] <= 20) | (df_raw["comment"].str.contains(pattern, na=False))
)

# 4) 콘텐츠 단위 집계
by_title = (
    df_raw.groupby("title", as_index=False)
    .agg(
        total_comments=("comment", "count"),
        event_comments=("is_event", "sum"),
        complaint_comments=("is_complaint", "sum"),
        positive_eval_comments=("is_positive_eval", "sum"),
        cherrypick_proxy_comments=("is_cherrypick_proxy", "sum"),
    )
)

by_title["event_ratio"] = safe_div(by_title["event_comments"], by_title["total_comments"]) * 100
by_title["positive_ratio_total"] = safe_div(
    by_title["positive_eval_comments"], by_title["total_comments"]
) * 100
by_title["non_event_comments"] = by_title["total_comments"] - by_title["event_comments"]
by_title["positive_ratio_non_event"] = safe_div(
    by_title["positive_eval_comments"], by_title["non_event_comments"]
) * 100
by_title["cherrypick_proxy_ratio"] = safe_div(
    by_title["cherrypick_proxy_comments"], by_title["event_comments"]
) * 100
by_title["complaint_ratio"] = safe_div(
    by_title["complaint_comments"], by_title["total_comments"]
) * 100

print("=" * 80)
print("가설 1 검증")
print("질문: 이벤트 유도 비중이 커질수록 긍정평가 비율이 증가하는가, 체리피커만 늘어나는가?")
print("=" * 80)

# H1-1: 이벤트 비율 -> 전체 기준 긍정평가 비율
run_ols(
    by_title,
    x_col="event_ratio",
    y_col="positive_ratio_total",
    title="H1-1) event_ratio -> positive_ratio_total",
)

# H1-2: 이벤트 비율 -> 비이벤트 모수 기준 긍정평가 비율
run_ols(
    by_title,
    x_col="event_ratio",
    y_col="positive_ratio_non_event",
    title="H1-2) event_ratio -> positive_ratio_non_event",
)

# H1-3: 이벤트 비율 -> 체리피커 프록시 비율
run_ols(
    by_title,
    x_col="event_ratio",
    y_col="cherrypick_proxy_ratio",
    title="H1-3) event_ratio -> cherrypick_proxy_ratio",
)

print("\n" + "=" * 80)
print("가설 2 검증")
print("질문: 댓글 수가 많아질수록 민원 비율이 선형적으로 증가하는가?")
print("=" * 80)

# H2-1: 선형 모델
linear_model = run_ols(
    by_title,
    x_col="total_comments",
    y_col="complaint_ratio",
    title="H2-1) total_comments -> complaint_ratio (선형)",
)

# H2-2: 비선형(2차항) 모델과 비교
h2_data = by_title[["total_comments", "complaint_ratio"]].dropna().copy()
h2_data["total_comments_sq"] = h2_data["total_comments"] ** 2

X_quad = sm.add_constant(h2_data[["total_comments", "total_comments_sq"]])
y_quad = h2_data["complaint_ratio"]
quad_model = sm.OLS(y_quad, X_quad).fit()

print("\n" + "-" * 80)
print("H2-2) 2차항 포함 모델 비교")
print(f"선형모델 R-squared: {linear_model.rsquared:.4f}, AIC: {linear_model.aic:.2f}")
print(f"2차모델  R-squared: {quad_model.rsquared:.4f}, AIC: {quad_model.aic:.2f}")
print(f"2차항 p-value: {quad_model.pvalues.get('total_comments_sq', np.nan):.6f}")

# 결과 저장
by_title.to_csv("hypothesis_test_by_title.csv", index=False, encoding="utf-8-sig")
print("\n저장 완료: hypothesis_test_by_title.csv")