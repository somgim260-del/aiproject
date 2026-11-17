import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR

# Streamlit Cloud (Linux) 환경에서 한글 폰트(나눔고딕) 설정
plt.rc("font", family="NanumGothic")
plt.rcParams["axes.unicode_minus"] = False  # 마이너스(-) 기호 깨짐 방지

# 페이지 기본 설정
st.set_page_config(page_title="멀티 알고리즘 기온 예측 비교", page_icon="🌡️", layout="wide")

st.title("🌡️ 멀티 머신러닝 알고리즘 기반 월별 기온 예측 및 비교")
st.markdown("과거 기온 데이터를 여러 가지 예측 알고리즘(**선형회귀, 랜덤 포레스트, SVR**)으로 학습시키고 예측 결과를 비교해보세요.")

# 1. 데이터 로드 및 전처리
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("temperature.csv", encoding="cp949")
    except UnicodeDecodeError:
        df = pd.read_csv("temperature.csv", encoding="utf-8")

    # 결측치 제거
    df = df.dropna(subset=["평균기온(℃)"]).copy()

    # 'Oct-07' 형태의 문자열에서 월(Month)과 연도(Year) 분리
    month_map = {
        "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
        "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
    }
    split_date = df["일시"].str.split("-", expand=True)
    df["월"] = split_date[0].map(month_map)
    yy = split_date[1].astype(int)

    # 2자리 연도 변환 (1907년~2026년 기준)
    df["연도"] = np.where(yy <= 26, 2000 + yy, 1900 + yy)
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("🚨 같은 폴더에 `temperature.csv` 파일이 있는지 확인해주세요!")
    st.stop()

# 2. 사이드바: 사용자 입력 (월, 예측 연도, 알고리즘 선택)
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

model_choice = st.sidebar.selectbox(
    "사용할 알고리즘을 선택하세요:",
    options=["전체 비교 (3개 모델 동시 비교)", "선형회귀 (Linear Regression)", "랜덤 포레스트 (Random Forest)", "서포트 벡터 머신 (SVR)"]
)

# 3. 선택한 월 데이터 필터링 및 모델 학습 딕셔너리 구성
month_df = df[df["월"] == selected_month].sort_values("연도")
X = month_df[["연도"]].values
y = month_df["평균기온(℃)"].values

# 세 가지 모델 정의
models = {
    "선형회귀": LinearRegression(),
    "랜덤 포레스트": RandomForestRegressor(n_estimators=100, random_state=42),
    "SVR": SVR(kernel='rbf', C=1e3, gamma=0.1)
}

# 모델 학습 및 예측값 수집
results = {}
for name, model in models.items():
    model.fit(X, y)
    pred = model.predict([[target_year]])[0]
    results[name] = {"model": model, "prediction": pred}

# 4. 상단 결과 요약 (선택한 모드에 맞게 출력)
st.subheader(f"📊 {target_year}년 {selected_month}월 기온 예측 결과 비교")

col1, col2, col3 = st.columns(3)

with col1:
    lr_pred = results["선형회귀"]["prediction"]
    st.metric(label="📈 선형회귀 예측", value=f"{lr_pred:.2f} ℃", delta=f"기울기: {results['선형회귀']['model'].coef_[0]:+.3f}℃/년")

with col2:
    rf_pred = results["랜덤 포레스트"]["prediction"]
    recent_avg = month_df.tail(10)["평균기온(℃)"].mean()
    st.metric(label="🌳 랜덤 포레스트 예측", value=f"{rf_pred:.2f} ℃", delta=f"최근 10년 평균 대비 {rf_pred - recent_avg:+.2f}℃")

with col3:
    svr_pred = results["SVR"]["prediction"]
    st.metric(label="📉 SVR (서포트 벡터) 예측", value=f"{svr_pred:.2f} ℃", delta=f"과거 데이터 패턴 반영")

# 5. 시각화 그래프 영역
st.subheader(f"📈 역대 {selected_month}월 평균기온 및 알고리즘별 예측 비교 그래프")

fig, ax = plt.subplots(figsize=(12, 6))

# (1) 실제 과거 기온 데이터 점
ax.plot(month_df["연도"], y, color="#bde0fe", alpha=0.6, linewidth=1)
ax.scatter(month_df["연도"], y, color="#3a86ff", label="과거 실제 평균기온", alpha=0.8, s=40)

# 선택된 모드에 따른 그래프 라인 드로잉
future_years = np.linspace(max_year, target_year, 50).reshape(-1, 1)

if model_choice == "전체 비교 (3个 모델 동시 비교)" or model_choice == "선형회귀 (Linear Regression)":
    ax.plot(month_df["연도"], results["선형회귀"]["model"].predict(X), color="#fb8500", linewidth=2, label="선형회귀 추세선")
    ax.scatter([target_year], [lr_pred], color="#fb8500", s=140, zorder=5, marker="o", edgecodes="black")

if model_choice == "전체 비교 (3个 모델 동시 비교)" or model_choice == "랜덤 포레스트 (Random Forest)":
    # 랜덤 포레스트는 부드러운 곡선 형태로 연장선 시각화
    rf_curve_years = np.linspace(month_df["연도"].min(), target_year, 100).reshape(-1, 1)
    ax.plot(rf_curve_years, results["랜덤 포레스트"]["model"].predict(rf_curve_years), color="#38b000", linewidth=2, linestyle="-.", label="랜덤 포레스트 예측 곡선")
    ax.scatter([target_year], [rf_pred], color="#38b000", s=140, zorder=5, marker="^", edgecodes="black")

if model_choice == "전체 비교 (3个 모델 동시 비교)" or model_choice == "서포트 벡터 머신 (SVR)":
    svr_curve_years = np.linspace(month_df["연도"].min(), target_year, 100).reshape(-1, 1)
    ax.plot(svr_curve_years, results["SVR"]["model"].predict(svr_curve_years), color="#7209b7", linewidth=2, linestyle=":", label="SVR(비선형) 추세선")
    ax.scatter([target_year], [svr_pred], color="#7209b7", s=140, zorder=5, marker="s", edgecodes="black")

ax.set_title(f"{target_year}년 {selected_month}월 기온 알고리즘별 예측 비교", fontsize=15, fontweight="bold", pad=15)
ax.set_xlabel("연도 (Year)", fontsize=12)
ax.set_ylabel("평균기온 (℃)", fontsize=12)
ax.grid(True, linestyle="--", alpha=0.4)
ax.legend(loc="upper left", fontsize=10, frameon=True, shadow=True)

st.pyplot(fig)

# 6. 그래프 하단: 알고리즘 쉬운 설명
st.divider()
st.subheader("💡 사용된 3가지 머신러닝 알고리즘의 작동 원리")

st.markdown("""
1. 📈 **선형회귀 (Linear Regression)**
   * **원리:** 과거의 모든 데이터 점들을 가장 잘 관통하는 **하나의 반듯한 직선**을 긋는 방식입니다.
   * **특징:** 기온이 장기적으로 일정한 비율로 꾸준히 오르거나 내릴 때 직관적이고 강력합니다.
2. 🌳 **랜덤 포레스트 (Random Forest)**
   * **원리:** 여러 개의 '의사결정 나무(Decision Tree)'를 수많이 만들어, 이 나무들이 내린 예측 결과들을 **다수결(평균)**로 모아 최종 결론을 내는 앙상블 방식입니다.
   * **특징:** 데이터의 급격한 변동이나 복잡한 비선형 패턴을 유연하게 포착합니다.
3. 📉 **서포트 벡터 머신 (SVR - Support Vector Regression)**
   * **원리:** 데이터들 사이에서 허용 가능한 오차 범위(마진) 안쪽을 지나가는 **가장 유연한 곡선/직선**을 찾아내는 방식입니다.
   * **특징:** 데이터의 특정한 경향과 미세한 패턴을 정교하게 반영하여 예측합니다.
""")
