import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import koreanize_matplotlib  # 한글 폰트 및 마이너스 부호 깨짐 방지

# 페이지 기본 설정
st.set_page_config(page_title="월별 기온 분석", layout="wide")
st.title("🌡️ 기온 데이터 시각화 대시보드")

# 1. 데이터 로드 및 전처리 (캐싱 적용)
@st.cache_data
def load_data():
    # 인코딩 자동 처리 (cp949 우선 시도 후 utf-8 시도)
    try:
        df = pd.read_csv("temperature.csv", encoding="cp949")
    except UnicodeDecodeError:
        df = pd.read_csv("temperature.csv", encoding="utf-8")

    # 결측치 제거
    df = df.dropna(subset=["최고기온(℃)", "최저기온(℃)"]).copy()

    # '일시' 컬럼(예: Oct-07)에서 월과 연도 추출
    month_map = {
        "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4,
        "May": 5, "Jun": 6, "Jul": 7, "Aug": 8,
        "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
    }
    split_date = df["일시"].str.split("-")
    df["월"] = split_date.str[0].map(month_map)
    year_2d = split_date.str[1].astype(int)

    # 1907년~1999년과 2000년~2026년 4자리 연도 정확히 복원
    # 인덱스 1093('Jan-00') 이전은 1900년대, 이후는 2000년대 데이터
    years = []
    century = 1900
    prev_y = -1
    for y in year_2d:
        if prev_y == 99 and y == 0:
            century = 2000
        years.append(century + y)
        prev_y = y
    df["연도"] = years

    return df

df = load_data()

# 2. 사용자 월 선택 UI
selected_month = st.selectbox(
    "분석할 월을 선택하세요:",
    options=list(range(1, 13)),
    format_func=lambda x: f"{x}월"
)

# 선택한 월 데이터 필터링 및 연도순 정렬
filtered_df = df[df["월"] == selected_month].sort_values("연도")

# 3. 꺾은선 그래프 그리기
fig, ax = plt.subplots(figsize=(12, 6))

# 최고기온 (핫핑크)
ax.plot(
    filtered_df["연도"],
    filtered_df["최고기온(℃)"],
    color="hotpink",
    marker="o",
    linewidth=2,
    label="최고기온(℃)"
)

# 최저기온 (하늘색)
ax.plot(
    filtered_df["연도"],
    filtered_df["최저기온(℃)"],
    color="skyblue",
    marker="o",
    linewidth=2,
    label="최저기온(℃)"
)

# 그래프 제목, 축 라벨, 범례 설정
ax.set_title("월별 기온분석", fontsize=18, fontweight="bold", pad=15)
ax.set_xlabel("연도", fontsize=12)
ax.set_ylabel("온도", fontsize=12)
ax.legend(loc="best", fontsize=11)
ax.grid(True, linestyle="--", alpha=0.5)

# 스트림릿 화면에 그래프 출력
st.pyplot(fig)

# 선택된 월의 원본 데이터 표 함께 제공 (선택 사항)
with st.expander(f"{selected_month}월 기온 데이터 상세 보기"):
    st.dataframe(
        filtered_df[["연도", "일시", "평균기온(℃)", "최고기온(℃)", "최저기온(℃)"]].reset_index(drop=True),
        use_container_width=True
    )
