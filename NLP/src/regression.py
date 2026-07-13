
import re
import os
import warnings
import numpy as np
import pandas as pd
import statsmodels.api as sm
import matplotlib
import matplotlib.pyplot as plt
from statsmodels.tools.sm_exceptions import ConvergenceWarning

import platform, matplotlib.font_manager as fm

def set_korean_font():
    available_fonts = {font.name for font in fm.fontManager.ttflist}
    family_candidates = [
        "Apple SD Gothic Neo",
        "AppleGothic",
        "NanumGothic",
        "Nanum Gothic",
        "Noto Sans CJK KR",
        "Noto Sans KR",
        "DejaVu Sans",
    ]
    file_candidates = [
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    ]

    font_family = None
    for font_path in file_candidates:
        if os.path.exists(font_path):
            try:
                font_family = fm.FontProperties(fname=font_path).get_name()
                break
            except Exception:
                continue

    if font_family is None:
        font_family = next((family for family in family_candidates if family in available_fonts), "DejaVu Sans")

    plt.rcParams["font.family"] = font_family
    plt.rcParams["axes.unicode_minus"] = False

set_korean_font()


# ════════════════════════════════════════════════════════════
#  유틸리티 함수
# ════════════════════════════════════════════════════════════

def to_bool(value):
    if isinstance(value, bool):
        return value
    if pd.isna(value):
        return False
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def safe_div(numerator, denominator):
    return np.where(denominator == 0, np.nan, numerator / denominator)


def pearson_r_with_ci(x, y, label=""):
    from scipy.stats import pearsonr
    mask = ~(np.isnan(x) | np.isnan(y))
    x, y = x[mask], y[mask]
    n = len(x)
    r, p = pearsonr(x, y)
    if n > 3:
        z = np.arctanh(r)
        se = 1 / np.sqrt(n - 3)
        ci_lo = np.tanh(z - 1.96 * se)
        ci_hi = np.tanh(z + 1.96 * se)
    else:
        ci_lo, ci_hi = np.nan, np.nan
    print(f"  {label}Pearson r: {r:.4f}  95%CI [{ci_lo:.3f}, {ci_hi:.3f}]  n={n}  p={p:.6f}")
    return r, p, (ci_lo, ci_hi)


def run_ols(df, x_col, y_col, title):

    data = df[[x_col, y_col]].dropna()
    x = sm.add_constant(data[x_col])
    y = data[y_col]
    model = sm.OLS(y, x).fit()

    print("\n" + "-" * 80)
    print(title)
    print(f"  표본 수   : {len(data)}")
    # 소표본 경고
    if len(data) < 15:
        print(f"  ⚠ 소표본(n={len(data)}) — 결과 해석 시 신중 필요")
    pearson_r_with_ci(data[x_col].values, data[y_col].values)
    sp_r = data[x_col].rank().corr(data[y_col].rank())
    print(f"  Spearman r: {sp_r:.4f}")
    from scipy.stats import spearmanr
    _, sp_p = spearmanr(data[x_col], data[y_col])
    print(f"  Spearman p: {sp_p:.6f}")
    print(f"  기울기(β) : {model.params.get(x_col, np.nan):.6f}")
    print(f"  p-value(β): {model.pvalues.get(x_col, np.nan):.6f}")
    print(f"  R-squared : {model.rsquared:.4f}")

    # Pearson/Spearman 부호 불일치 경고
    if np.sign(data[x_col].corr(data[y_col])) != np.sign(sp_r):
        print("  ⚠ Pearson/Spearman 부호 불일치 — 이상치 또는 비단조 관계 가능성")

    return model




def permutation_test(group_a, group_b, n_permutations=10_000, stat="mean_diff", seed=42):
    """
    두 독립 집단 간 지표 차이에 대한 Permutation test.

    Parameters
    ----------
    group_a, group_b : array-like
    n_permutations   : 셔플 횟수
    stat             : "mean_diff" | "median_diff"
    seed             : 재현성을 위한 랜덤 시드

    Returns
    -------
    observed_stat : 관측된 통계량
    p_value       : 양측 p-value
    null_dist     : 귀무가설 분포 (배열)
    """
    rng = np.random.default_rng(seed)
    a, b = np.asarray(group_a, dtype=float), np.asarray(group_b, dtype=float)
    a, b = a[~np.isnan(a)], b[~np.isnan(b)]
    combined = np.concatenate([a, b])
    na = len(a)

    if stat == "mean_diff":
        observed = np.mean(a) - np.mean(b)
        def calc(arr): return np.mean(arr[:na]) - np.mean(arr[na:])
    else:
        observed = np.median(a) - np.median(b)
        def calc(arr): return np.median(arr[:na]) - np.median(arr[na:])

    null_dist = np.array([calc(rng.permutation(combined)) for _ in range(n_permutations)])
    p_value = np.mean(np.abs(null_dist) >= np.abs(observed))
    return observed, p_value, null_dist


def run_permutation_tests(df_raw, by_title, n_perm=10_000):

    print("\n" + "=" * 80)
    print("Permutation Test — 이벤트 게시물 vs 비이벤트 게시물 집단 비교")
    print("=" * 80)
    print("""
목적:
  단순 OLS 회귀는 같은 게시물 속성에서 0/1 댓글 반응을 예측할 때
  오차가 커지는 구조적 한계가 있습니다.
  대신 '게시물' 단위로 두 집단(이벤트 O / 이벤트 X)을 구분하고
  집단 간 댓글 행동 지표의 차이가 우연인지 검증합니다.

귀무가설 H₀: 두 집단 간 지표의 평균 차이는 0이다 (= 집단 구분 불가)
대립가설 H₁: 두 집단 간 지표의 평균 차이는 0이 아니다
방법: 10,000회 무작위 라벨 셔플 후 관측값 이상의 극단치 비율 계산
""")

    event_mask = by_title["is_event_video"]
    ev  = by_title[event_mask]
    nev = by_title[~event_mask]

    print(f"  이벤트 게시물   : {len(ev)}편")
    print(f"  비이벤트 게시물 : {len(nev)}편")

    metrics = [
        ("total_comments",  "게시물당 총 댓글 수",      "mean_diff"),
        ("avg_comment_len", "게시물당 평균 댓글 글자 수", "mean_diff"),
    ]

    results = []
    for col, label, stat in metrics:
        obs, p, null = permutation_test(ev[col], nev[col], n_permutations=n_perm, stat=stat)
        ev_mean  = ev[col].mean()
        nev_mean = nev[col].mean()
        flag = "★ 유의" if p < 0.05 else "  비유의"
        print(f"\n  [{label}]")
        print(f"    이벤트 게시물 평균 : {ev_mean:.2f}")
        print(f"    비이벤트 게시물 평균: {nev_mean:.2f}")
        print(f"    관측 차이(A-B)      : {obs:.2f}")
        print(f"    Permutation p-value : {p:.4f}  {flag}")
        results.append((col, label, ev_mean, nev_mean, obs, p, null))

    # ── 시각화 ──────────────────────────────────────────────
    fig, axes = plt.subplots(1, 2, figsize=(13, 5), constrained_layout=True)
    fig.suptitle("Permutation Test — 이벤트 vs 비이벤트 게시물 귀무가설 분포", fontsize=13)

    for ax, (col, label, ev_m, nev_m, obs, p, null) in zip(axes, results):
        ax.hist(null, bins=50, color="#4C9BE8", alpha=0.7, edgecolor="white", label="귀무가설 분포")
        ax.axvline(obs,  color="#E84C4C", lw=2.2, label=f"관측값 ({obs:.2f})")
        ax.axvline(-obs, color="#E84C4C", lw=2.2, linestyle="--", alpha=0.6)
        ax.set_title(f"{label}\np = {p:.4f}")
        ax.set_xlabel("평균 차이 (이벤트 - 비이벤트)")
        ax.set_ylabel("빈도")
        ax.legend(fontsize=9)

    fig.savefig("figures/permutation_test_results.png", dpi=150)
    plt.close(fig)
    print("\n  시각화 저장 완료: figures/permutation_test_results.png")

    # ── 박스플롯 보조 시각화 ────────────────────────────────
    fig2, axes2 = plt.subplots(1, 2, figsize=(10, 5), constrained_layout=True)
    fig2.suptitle("이벤트 vs 비이벤트 게시물 — 집단별 분포 비교", fontsize=12)

    for ax, (col, label, *_) in zip(axes2, results):
        data_ev  = by_title.loc[ event_mask, col].dropna()
        data_nev = by_title.loc[~event_mask, col].dropna()
        ax.boxplot(
            [data_nev, data_ev],
            tick_labels=["비이벤트", "이벤트"],
            patch_artist=True,
            boxprops=dict(facecolor="#D6E4F0"),
            medianprops=dict(color="#1B3A6B", lw=2),
        )
        ax.set_title(label)
        ax.set_ylabel(col)

    fig2.savefig("figures/permutation_boxplot.png", dpi=150)
    plt.close(fig2)
    print("  박스플롯 저장 완료: figures/permutation_boxplot.png")

    return results


# ════════════════════════════════════════════════════════════
#  기존 분석 함수 (표현만 수정)
# ════════════════════════════════════════════════════════════

def summarize_outcome_by_category(df, category_col, min_comments=10):
    grouped = (
        df.groupby(category_col, as_index=False)
        .agg(
            total_comments=("comment", "count"),
            complaint_comments=("is_complaint", "sum"),
            positive_eval_comments=("is_positive_eval", "sum"),
        )
        .sort_values("total_comments", ascending=False)
    )
    grouped["complaint_rate"] = safe_div(grouped["complaint_comments"], grouped["total_comments"]) * 100
    grouped["positive_rate"]  = safe_div(grouped["positive_eval_comments"], grouped["total_comments"]) * 100

    overall_complaint = df["is_complaint"].mean() * 100
    overall_positive  = df["is_positive_eval"].mean() * 100
    grouped["complaint_lift_vs_overall"] = safe_div(grouped["complaint_rate"], overall_complaint)
    grouped["positive_lift_vs_overall"]  = safe_div(grouped["positive_rate"],  overall_positive)

    grouped = grouped[grouped["total_comments"] >= min_comments].copy()
    grouped = grouped.sort_values(["complaint_rate", "total_comments"], ascending=[False, False])
    return grouped


def compare_event_inclusion(df, category_col, min_comments=30):
    all_s     = summarize_outcome_by_category(df, category_col, min_comments=min_comments)
    non_event = summarize_outcome_by_category(df[~df["is_event"]].copy(), category_col, min_comments=min_comments)
    merged = all_s.merge(non_event, on=category_col, how="inner", suffixes=("_all", "_non_event"))
    merged["complaint_rate_delta(non_event-all)"] = (
        merged["complaint_rate_non_event"] - merged["complaint_rate_all"]
    )
    merged["positive_rate_delta(non_event-all)"] = (
        merged["positive_rate_non_event"] - merged["positive_rate_all"]
    )
    return merged.sort_values(
        ["complaint_rate_delta(non_event-all)", "total_comments_all"],
        ascending=[False, False],
    )


# ── 로지스틱 오즈비 (참고 자료 섹션으로 분리) ──────────────

def logistic_or_table(df, outcome_col, category_col, min_comments=30, top_n=8):
    """
    [참고 자료] 로지스틱 회귀 기반 오즈비.
    단순 관찰 단계에서의 경향성 파악용이며 인과관계 해석은 불가.
    댓글 수 불균형 및 소표본 환경에서 CI=NaN이 발생할 수 있음.
    """
    temp   = df[[outcome_col, category_col]].dropna().copy()
    counts = temp[category_col].value_counts()
    kept   = counts[counts >= min_comments].index.tolist()
    temp   = temp[temp[category_col].isin(kept)].copy()

    if temp.empty or temp[category_col].nunique() < 2:
        return pd.DataFrame()

    top_levels       = temp[category_col].value_counts().head(top_n).index.tolist()
    temp[category_col] = np.where(temp[category_col].isin(top_levels), temp[category_col], "OTHER")

    dummies = pd.get_dummies(temp[category_col], prefix=category_col, drop_first=True)
    x = sm.add_constant(dummies.astype(float))
    y = temp[outcome_col].astype(int)

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ConvergenceWarning)
            model = sm.Logit(y, x).fit(disp=False)
        converged = bool(model.mle_retvals.get("converged", True))
        if not converged:
            raise ValueError("logit did not converge")
        params = model.params
        conf   = model.conf_int()
        pvals  = model.pvalues
    except Exception:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ConvergenceWarning)
            model = sm.Logit(y, x).fit_regularized(alpha=1e-4, disp=False)
        params = model.params
        conf   = pd.DataFrame(index=params.index, data={0: np.nan, 1: np.nan})
        pvals  = pd.Series(index=params.index, data=np.nan)

    coef_clip    = np.clip(params.values,                       -700, 700)
    ci_lo_clip   = np.clip(conf.loc[params.index, 0].values,   -700, 700)
    ci_hi_clip   = np.clip(conf.loc[params.index, 1].values,   -700, 700)

    result = pd.DataFrame({
        "term":        params.index,
        "coef":        params.values,
        "odds_ratio":  np.exp(coef_clip),
        "ci_low":      np.exp(ci_lo_clip),
        "ci_high":     np.exp(ci_hi_clip),
        "p_value":     pvals.loc[params.index].values,
    })
    result = result[result["term"] != "const"].copy()

    # CI 유효성 플래그
    result["ci_valid"] = result["ci_low"].notna() & result["ci_high"].notna()
    result["note"] = np.where(
        ~result["ci_valid"],
        "표본 부족 — CI 미산출, 오즈비 해석 주의",
        ""
    )
    result.insert(0, "outcome",  outcome_col)
    result.insert(1, "category", category_col)
    return result.sort_values("odds_ratio", ascending=False)


# ════════════════════════════════════════════════════════════
#  메인 파이프라인
# ════════════════════════════════════════════════════════════

# 1) 데이터 로드
df_raw = pd.read_csv("results/michuhol_analysis_raw.csv")

# 2) 타입 정리
df_raw["is_event"]      = df_raw["is_event"].apply(to_bool)
df_raw["is_complaint"]  = df_raw["is_complaint"].apply(to_bool)
df_raw["comment"]       = df_raw["comment"].fillna("").astype(str)
df_raw["sentiment_label"] = df_raw["sentiment_label"].fillna("").astype(str)

# 3) 파생변수 생성
pattern = re.compile(r"정답|\b\d+번\b|이벤트|응모|참여|폼|마감")
df_raw["is_positive_eval"] = (
    (~df_raw["is_event"]) & (df_raw["sentiment_label"].str.contains("긍정", na=False))
)
df_raw["event_text_length"] = df_raw["comment"].str.len()

# 체리피커 프록시: 이벤트 댓글 중 '응모 키워드 단독' 조건만으로 정의
# (기존: is_event & (글자수≤20 | 키워드) → 키워드 조건과 is_event가 겹쳐 동어반복)
df_raw["is_cherrypick_proxy"] = df_raw["is_event"] & (
    (df_raw["event_text_length"] <= 20) | (df_raw["comment"].str.contains(pattern, na=False))
)

# 4) 영상(title) 단위 집계
by_title = (
    df_raw.groupby("title", as_index=False)
    .agg(
        total_comments=("comment", "count"),
        event_comments=("is_event", "sum"),
        complaint_comments=("is_complaint", "sum"),
        positive_eval_comments=("is_positive_eval", "sum"),
        cherrypick_proxy_comments=("is_cherrypick_proxy", "sum"),
        avg_comment_len=("event_text_length", "mean"),   # ← Permutation test용
    )
)

by_title["event_ratio"]           = safe_div(by_title["event_comments"],          by_title["total_comments"]) * 100
by_title["positive_ratio_total"]  = safe_div(by_title["positive_eval_comments"],  by_title["total_comments"]) * 100
by_title["non_event_comments"]    = by_title["total_comments"] - by_title["event_comments"]
by_title["positive_ratio_non_event"] = safe_div(by_title["positive_eval_comments"], by_title["non_event_comments"]) * 100
by_title["cherrypick_proxy_ratio"]   = safe_div(by_title["cherrypick_proxy_comments"], by_title["event_comments"]) * 100
by_title["complaint_ratio"]          = safe_div(by_title["complaint_comments"],    by_title["total_comments"]) * 100
by_title["is_event_video"]           = by_title["event_comments"] > 0


# ════════════════════════════════════════════════════════════
#  가설 1 — 이벤트 비율과 댓글 반응 지표 간 경향성 검증
# ════════════════════════════════════════════════════════════
print("=" * 80)
print("가설 1 검증")
print("질문: 이벤트 유도 비중이 커질수록 긍정 평가 경향성이 나타나는가,")
print("      아니면 체리피커 유입 경향성이 더 강한가?")
print("=" * 80)
print("[주의] 아래는 단순 회귀(독립변수 1개)로 '경향성'을 탐색하는 것이며,")
print("       다른 교란변수를 통제하지 않았으므로 인과관계로 해석할 수 없습니다.")

run_ols(by_title, "event_ratio", "positive_ratio_total",    "H1-1) event_ratio → positive_ratio_total")
run_ols(by_title, "event_ratio", "positive_ratio_non_event","H1-2) event_ratio → positive_ratio_non_event (낙수효과)")
run_ols(by_title, "event_ratio", "cherrypick_proxy_ratio",  "H1-3) event_ratio → cherrypick_proxy_ratio")


# ════════════════════════════════════════════════════════════
#  가설 2 — 댓글 트래픽 규모와 민원율 간 선형성 검증
# ════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("가설 2 검증")
print("질문: 총 댓글 수가 많아질수록 민원율이 선형 또는 비선형적으로 증가하는가?")
print("=" * 80)
print("[주의] 마찬가지로 경향성 탐색 목적이며, 인과관계 해석은 불가합니다.")

linear_model = run_ols(by_title, "total_comments", "complaint_ratio", "H2-1) total_comments → complaint_ratio (선형)")

h2_data = by_title[["total_comments", "complaint_ratio"]].dropna().copy()
h2_data["total_comments_sq"] = h2_data["total_comments"] ** 2
X_quad = sm.add_constant(h2_data[["total_comments", "total_comments_sq"]])
quad_model = sm.OLS(h2_data["complaint_ratio"], X_quad).fit()

print("\n" + "-" * 80)
print("H2-2) 2차항 포함 모델 비교")
print(f"  선형모델 R-squared: {linear_model.rsquared:.4f},  AIC: {linear_model.aic:.2f}")
print(f"  2차모델  R-squared: {quad_model.rsquared:.4f},  AIC: {quad_model.aic:.2f}")
print(f"  2차항 p-value     : {quad_model.pvalues.get('total_comments_sq', np.nan):.6f}")


# ════════════════════════════════════════════════════════════
#  [신규] Permutation Test
# ════════════════════════════════════════════════════════════
perm_results = run_permutation_tests(df_raw, by_title, n_perm=10_000)


# ════════════════════════════════════════════════════════════
#  [참고 자료] 세그먼트별 요약 + 로지스틱 오즈비
#  (가설 본문에서 분리; 참고 목적으로만 활용)
# ════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("[참고 자료] 세그먼트별 댓글 반응 경향성 및 로지스틱 오즈비")
print("  ※ 이하는 탐색적 분석이며, 같은 게시물 내 0/1 레이블 예측 한계로")
print("     인과관계가 아닌 '관찰된 경향성'으로만 해석해야 합니다.")
print("=" * 80)

topic_summary    = summarize_outcome_by_category(df_raw, "topic",   min_comments=30)
content_summary  = summarize_outcome_by_category(df_raw, "content", min_comments=30)

topic_compare_event   = compare_event_inclusion(df_raw, "topic",   min_comments=30)
content_compare_event = compare_event_inclusion(df_raw, "content", min_comments=30)

or_positive_topic = logistic_or_table(df_raw, "is_positive_eval", "topic",   min_comments=30)
or_complaint_topic = logistic_or_table(df_raw, "is_complaint",    "topic",   min_comments=30)

print("\n[topic별 민원/긍정 경향성]")
print(topic_summary[["topic", "total_comments", "complaint_rate", "positive_rate"]].to_string(index=False))

print("\n[이벤트 포함/제외 비교 — topic]")
print(
    topic_compare_event[[
        "topic", "total_comments_all",
        "positive_rate_all", "positive_rate_non_event",
        "positive_rate_delta(non_event-all)",
    ]].to_string(index=False)
)

if not or_positive_topic.empty:
    print("\n[참고] 로지스틱 오즈비 — is_positive_eval ~ topic")
    print("  (CI=NaN은 표본 부족으로 인한 계산 불가를 의미)")
    print(or_positive_topic[["term", "odds_ratio", "ci_low", "ci_high", "p_value", "note"]].to_string(index=False))

if not or_complaint_topic.empty:
    print("\n[참고] 로지스틱 오즈비 — is_complaint ~ topic")
    print(or_complaint_topic[["term", "odds_ratio", "ci_low", "ci_high", "p_value", "note"]].to_string(index=False))

# ── CSV 저장 ────────────────────────────────────────────────
by_title.to_csv("results/hypothesis_test_by_title.csv",             index=False, encoding="utf-8-sig")
topic_summary.to_csv("results/content_type_analysis_topic.csv",     index=False, encoding="utf-8-sig")
content_summary.to_csv("results/content_type_analysis_content.csv", index=False, encoding="utf-8-sig")
topic_compare_event.to_csv("results/content_type_topic_event_compare.csv",   index=False, encoding="utf-8-sig")
content_compare_event.to_csv("results/content_type_content_event_compare.csv", index=False, encoding="utf-8-sig")

if not or_positive_topic.empty:
    or_positive_topic.to_csv("results/ref_logit_odds_positive_topic.csv", index=False, encoding="utf-8-sig")
if not or_complaint_topic.empty:
    or_complaint_topic.to_csv("results/ref_logit_odds_complaint_topic.csv", index=False, encoding="utf-8-sig")

print("\n" + "=" * 80)
print("전체 파이프라인 완료")
print("  results/hypothesis_test_by_title.csv")
print("  figures/permutation_test_results.png")
print("  figures/permutation_boxplot.png")
print("  results/content_type_analysis_topic.csv")
print("  ref_logit_odds_*.csv  (참고 자료)")