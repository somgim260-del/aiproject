import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import platform
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler

# 운영체제별 및 Streamlit Cloud (Linux) 환경 한글 폰트 깨짐 방지 설정
env_os = platform.system()
if env_os == "Windows":
    plt.rc("font", family="Malgun Gothic")
elif env_os == "Darwin":
    plt.rc("font", family="AppleGothic")
else:
    # Linux (Streamlit Cloud) 환경: 사용 가능한 나눔폰트 자동 탐색 또는 기본 지정
    font_list = [f.name for f in fm.fontManager.ttflist]
    if "NanumGothic" in font_list:
        plt.rc("font", family="NanumGothic")
    elif "NanumBarunGothic" in font_list:
        plt.rc("font", family="NanumBarunGothic")
    else:
        plt.rc("font", family="DejaVu Sans")  # 대체 폰트

plt.rcParams["axes.unicode_minus"] = False  # 마이너스(-) 기호 깨짐 방지

# 페이지 기본 설정
st.set_page_config(page_title="멀티 알고리즘 기온 예측 비교", page_icon="🌡️", layout="wide")

st.title("🌡️ 멀티 머신러닝 알고리즘 기반 월별 기온 예측 및 한눈에 비교")
st.markdown("선형회귀, 랜덤 포레스트, SVR(서포트 벡터 머신) 모델을 이용해 과거 데이터를 학습하고 미래 기온 예측 결과를 비교합니다.")

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

# 3. 데이터 필터링 및 모델 학습 (SVR 오류 방지를 위한 StandardScaler 적용)
month_df = df[df["월"] == selected_month].sort_values("연도")
X = month_df[["연도"]].values
y = month_df["평균기온(℃)"].values

# SVR과 선형모델의 성능 최적화를 위한 스케일러 분리
scaler_X = StandardScaler()
X_scaled = scaler_X.fit_transform(X)

# 세 가지 모델 정의 및 학습
lr_model = LinearRegression()
lr_model.fit(X, y)
lr_pred = lr_model.predict([[target_year]])[0]

rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
rf_model.fit(X, y)  # 숲 모델은 스케일링 불필요
rf_pred = rf_model.predict([[target_year]])[0]

svr_model = SVR(kernel='rbf', C=100, gamma='scale')
svr_model.fit(X_scaled, y)
svr_pred = svr_model.predict(scaler_X.transform([[target_year]]))[0]

# 4. 상단 결과 요약 메트릭 카드 (한눈에 비교)
st.subheader(f"📊 {target_year}년 {selected_month}월 알고리즘별 예측 기온 비교")

col1, col2, col3 = st.columns(3)
recent_avg = month_df.tail(10)["평균기온(℃)"].mean()

col1.metric(
    label="📈 선형회귀 (Linear Regression)",
    value=f"{lr_pred:.2f} ℃",
    delta=f"최근 10년 평균 대비 {lr_pred - recent_avg:+.2f} ℃"
)
col2.metric(
    label="🌳 랜덤 포레스트 (Random Forest)",
    value=f"{rf_pred:.2f} ℃",
    delta=f"최근 10년 평균 대비 {rf_pred - recent_avg:+.2f} ℃"
)
col3.metric(
    label="📉 서포트 벡터 머신 (SVR)",
    value=f"{svr_pred:.2f} ℃",
    delta=f"최근 10년 평균 대비 {svr_pred - recent_avg:+.2f} ℃"
)

# 5. 시각화 그래프 영역 (3개 모델을 하나의 그래프에 한눈에 비교)
st.subheader(f"📈 역대 {selected_month}월 평균기온 및 3대 알고리즘 예측 비교 그래프")

fig, ax = plt.subplots(figsize=(12, 6))

# (1) 실제 과거 기온 데이터
ax.plot(month_df["연도"], y, color="#bde0fe", alpha=0.5, linewidth=1)
ax.scatter(month_df["연도"], y, color="#1d3557", label="과거 실제 평균기온", alpha=0.8, s=35, zorder=3)

# (2) 연도별 연속 예측을 위한 구간 생성
curve_years = np.linspace(month_df["연도"].min(), target_year, 200).reshape(-1, 1)

# 선형회귀 추세선 및 예측점
ax.plot(curve_years, lr_model.predict(curve_years), color="#fb8500", linewidth=2.5, label="선형회귀 추세선")
ax.scatter([target_year], [lr_pred], color="#fb8500", s=150, zorder=5, edgecodes="black", marker="o")

# 랜덤 포레스트 예측 곡선 및 예측점
ax.plot(curve_years, rf_model.predict(curve_years), color="#38b000", linewidth=2, linestyle="--", label="랜덤 포레스트 예측선")
ax.scatter([target_year], [rf_pred], color="#38b000", s=150, zorder=5, edgecodes="black", marker="^")

# SVR 추세선 및 예측점
curve_years_scaled = scaler_X.transform(curve_years)
ax.plot(curve_years, svr_model.predict(curve_years_scaled), color="#7209b7", linewidth=2, linestyle="-.", label="SVR(비선형) 추세선")
ax.scatter([target_year], [svr_pred], color="#7209b7", s=150, zorder=5, edgecodes="black", marker="s")

ax.set_title(f"역대 {selected_month}월 평균기온 및 {target_year}년 예측 비교", fontsize=15, fontweight="bold", pad=15)
ax.set_xlabel("연도 (Year)", fontsize=12)
ax.set_ylabel("평균기온 (℃)", fontsize=12)
ax.grid(True, linestyle="--", alpha=0.4)
ax.legend(loc="upper left", fontsize=10, frameon=True, shadow=True)

st.pyplot(fig)

# 6. 그래프 하단: 알고리즘 쉬운 설명
st.divider()
st.subheader("💡 3가지 머신러닝 알고리즘 작동 원리 요약")

st.info(f"""
1. 📈 **선형회귀 (Linear Regression):** 과거 점들을 통과하는 **가장 반듯한 하나의 직선**을 그어 장기적인 상승/하강 추세를 파악합니다. ({target_year}년 예측: **{lr_pred:.2f}℃**)
2. 🌳 **랜덤 포레스트 (Random Forest):** 수많은 의사결정 나무를 심어 각각의 예측을 종합(다수결)하여 **유연한 계단식/구간별 평균**을 찾아냅니다. ({target_year}년 예측: **{rf_pred:.2f}℃**)
3. 📉 **서포트 벡터 머신 (SVR):** 데이터 분포 속에서 허용 오차 범위 내를 관통하는 **최적의 비선형 곡선**을 찾아 정교하게 예측합니다. ({target_year}년 예측: **{svr_pred:.2f}℃**)
""")
