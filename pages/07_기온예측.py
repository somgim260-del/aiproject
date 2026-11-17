import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from sklearn.linear_model import LinearRegression

# Streamlit Cloud (Linux) 환경에서 한글 폰트(나눔고딕) 설정
plt.rc("font", family="NanumGothic")
plt.rcParams["axes.unicode_minus"] = False  # 마이너스(-) 기호 깨짐 방지

# 페이지 기본 설정
st.set_page_config(page_title="기온 예측 선형회귀 시각화", page_icon="🌡️", layout="wide")

st.title("🌡️ 월별 평균기온 추이 및 미래 기온 예측")
st.markdown("과거 기온 데이터를 바탕으로 **선형회귀(Linear Regression)** 알고리즘이 어떻게 미래의 기온을 예측하는지 확인해 보세요.")

# 1. 데이터 로드 및 전처리 (캐싱을 통해 속도 향상)
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("temperature.csv", encoding="cp949")
    except UnicodeDecodeError:
        df = pd.read_csv("temperature.csv", encoding="utf-8")

    # 결측치(데이터가 없는 시기) 제거
    df = df.dropna(subset=["평균기온(℃)"]).copy()

    # 'Oct-07' 형태의 문자열에서 월(Month)과 연도(Year) 분리
    month_map = {
        "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
        "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
    }
    split_date = df["일시"].str.split("-", expand=True)
    df["월"] = split_date[0].map(month_map)
    yy = split_date[1].astype(int)

    # 2자리 연도 변환 (1907년~2026년 기준: 00~26은 2000년대, 27~99는 1900년대)
    df["연도"] = np.where(yy <= 26, 2000 + yy, 1900 + yy)
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("🚨 같은 폴더에 `temperature.csv` 파일이 있는지 확인해주세요!")
    st.stop()

# 2. 사이드바: 사용자 입력 (월 및 예측 연도)
st.sidebar.header("⚙️ 예측 조건 설정")
selected_month = st.sidebar.selectbox(
    "분석할 월(Month)을 선택하세요:",
    options=list(range(1, 13)),
    index=7,  # 기본값: 8월
    format_func=lambda x: f"{x}월"
)

max_year = int(df["연도"].max())
target_year = st.sidebar.number_input(
    "예측하고 싶은 연도를 입력하세요:",
    min_value=max_year + 1,
    max_value=2150,
    value=2035,
    step=1
)

# 3. 선택한 월 데이터 필터링 및 선형회귀 모델 학습
month_df = df[df["월"] == selected_month].sort_values("연도")

X = month_df[["연도"]].values  # 독립변수 (연도)
y = month_df["평균기온(℃)"].values  # 종속변수 (평균기온)

model = LinearRegression()
model.fit(X, y)

# 예측값 계산
predicted_temp = model.predict([[target_year]])[0]
recent_avg = month_df.tail(10)["평균기온(℃)"].mean()
diff_temp = predicted_temp - recent_avg

# 4. 상단 핵심 결과 요약 카드
col1, col2, col3 = st.columns(3)
col1.metric(
    label=f"🔮 {target_year}년 {selected_month}월 예측 평균기온",
    value=f"{predicted_temp:.2f} ℃",
    delta=f"최근 10년 평균 대비 {diff_temp:+.2f} ℃"
)
col2.metric(
    label="📈 연평균 기온 상승 기울기",
    value=f"{model.coef_[0]:+.4f} ℃/년",
    delta=f"100년당 {model.coef_[0]*100:+.2f} ℃ 변화"
)
col3.metric(
    label="📊 학습에 사용된 데이터 수",
    value=f"{len(month_df)}년 치",
    delta=f"{int(month_df['연도'].min())}년 ~ {int(month_df['연도'].max())}년"
)

# 5. 선형회귀 작동 원리 시각화 그래프
st.subheader(f"📈 {selected_month}월 평균기온 변화 및 선형회귀 예측 그래프")

fig, ax = plt.subplots(figsize=(12, 6))

# (1) 실제 과거 기온 데이터 (산점도 & 연한 연결선)
ax.plot(month_df["연도"], y, color="#8ecae6", alpha=0.5, linewidth=1)
ax.scatter(month_df["연도"], y, color="#219ebc", label="과거 실제 평균기온 (데이터 점)", alpha=0.8, s=35)

# (2) 학습 구간 추세선 (과거 ~ 현재)
ax.plot(month_df["연도"], model.predict(X), color="#fb8500", linewidth=2.5, label="선형회귀 추세선 (데이터를 가장 잘 관통하는 직선)")

# (3) 미래 예측 연장선 (현재 ~ 예측 연도)
future_years = np.linspace(max_year, target_year, 50).reshape(-1, 1)
ax.plot(future_years, model.predict(future_years), color="#e63946", linestyle="--", linewidth=2.5, label="미래 기온 예측 연장선")

# (4) 예측 지점 강조 및 가이드라인 (직선이 좌표를 찾아가는 원리 표현)
ax.scatter([target_year], [predicted_temp], color="#e63946", s=180, zorder=5, edgecolors="black", label=f"{target_year}년 예측 결과 ({predicted_temp:.2f}℃)")
ax.vlines(x=target_year, ymin=y.min() - 1, ymax=predicted_temp, color="gray", linestyle=":", alpha=0.8)
ax.hlines(y=predicted_temp, xmin=month_df["연도"].min(), xmax=target_year, color="gray", linestyle=":", alpha=0.8)

# 예측 값 말풍선 표시
ax.annotate(
    f"  {target_year}년 예측: {predicted_temp:.2f}℃",
    xy=(target_year, predicted_temp),
    xytext=(target_year - (target_year - month_df["연도"].min()) * 0.18, predicted_temp + 0.6),
    fontsize=11,
    fontweight="bold",
    color="#d62828",
    arrowprops=dict(arrowstyle="->", color="#d62828", lw=1.5)
)

ax.set_title(f"역대 {selected_month}월 평균기온과 {target_year}년 선형회귀 예측", fontsize=15, fontweight="bold", pad=15)
ax.set_xlabel("연도 (Year)", fontsize=12)
ax.set_ylabel("평균기온 (℃)", fontsize=12)
ax.set_ylim(y.min() - 1, max(y.max(), predicted_temp) + 1.5)
ax.grid(True, linestyle="--", alpha=0.4)
ax.legend(loc="upper left", fontsize=10, frameon=True, shadow=True)

st.pyplot(fig)

# 6. 그래프 하단: 선형회귀 알고리즘 쉬운 설명
st.divider()
st.subheader("💡 그래프 속 '선형회귀 알고리즘'은 어떻게 작동할까요?")

st.info(f"""
**선형회귀(Linear Regression)**는 한마디로 **"과거의 점들 사이를 가장 잘 가로지르는 하나의 직선(추세선)을 그어서 미래를 예측하는 방법"**입니다.

1. **파란색 점 (과거 데이터):** 역대 {selected_month}월의 실제 평균기온들입니다. 해마다 춥기도 하고 덥기도 해서 점들이 위아래로 흩어져 있습니다.
2. **주황색 실선 (가장 이상적인 직선 찾기):** 컴퓨터는 모든 파란색 점들과 직선 사이의 거리(오차)가 **가장 작아지는 단 하나의 직선**을 수학적으로 계산해 긋습니다. 
   * 현재 데이터에서 이 직선의 공식은 **`예측 기온 = ({model.coef_[0]:.4f} × 연도) + ({model.intercept_:.2f})`** 입니다.
3. **빨간색 점선과 점 (미래 예측하기):** 찾아낸 주황색 직선의 각도(기울기)를 그대로 유지한 채 **{target_year}년**까지 쭉 연장합니다. 회색 점선을 따라가 보면 **{target_year}년**과 만나는 지점의 기온이 바로 **{predicted_temp:.2f}℃**가 됩니다!
""")
