import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import os

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

st.title("🏙️ 서울시 자치구별 연령별 인구 분석 시각화")

# 데이터 로드 (상위 폴더에 있는 population.csv 경로 참조)
@st.cache_data
def load_data():
    # 현재 파일(app.py) 위치 기준으로 상위 폴더(..)의 population.csv 경로 생성
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.abspath(os.path.join(current_dir, '..', 'population.csv'))
    
    df = pd.read_csv(file_path, encoding='cp949')
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()

# 사이드바 설정 (사용자 입력)
st.sidebar.header("🔍 조회 옵션 설정")

# 1. 행정구 선택
districts = df['행정구역'].unique()
selected_district = st.sidebar.selectbox("행정구 선택", districts)

# 2. 연도 선택 (2020~2025)
years = ['2020년', '2021년', '2022년', '2023년', '2024년', '2025년']
selected_year = st.sidebar.selectbox("연도 선택", years)

# 3. 성별 선택
gender_options = {
    "총인구": "거주자",
    "남성": "남_거주자",
    "여성": "여_거주자"
}
selected_gender_label = st.sidebar.selectbox("성별 선택", list(gender_options.keys()))
selected_gender_code = gender_options[selected_gender_label]

# 데이터 필터링
row = df[df['행정구역'] == selected_district]

# 연령대 컬럼 정의
age_groups = [
    '0~9세', '10~19세', '20~29세', '30~39세', '40~49세', 
    '50~59세', '60~69세', '70~79세', '80~89세', '90~99세', '100세 이상'
]

# 선택한 조건에 맞는 컬럼 조합
cols = [f"{selected_year}_{selected_gender_code}_{age}" for age in age_groups]

# 데이터 추출 및 쉼표 제거 후 정수형 변환
population_values = []
for col in cols:
    val = row[col].values[0]
    if isinstance(val, str):
        val = int(val.replace(',', ''))
    population_values.append(val)

# 시각화용 데이터프레임 생성
chart_df = pd.DataFrame({
    '나이': age_groups,
    '인구수': population_values
})

st.subheader(f"📍 {selected_district} - {selected_year} ({selected_gender_label}) 연령별 인구 분포")

# Matplotlib 그래프 생성 (초록색 선, 격자선 적용)
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(chart_df['나이'], chart_df['인구수'], marker='o', color='green', linewidth=2, markersize=6)

ax.set_title(f"{selected_district} {selected_year} 연령별 인구수", fontsize=14, pad=15)
ax.set_xlabel("연령 구간", fontsize=12)
ax.set_ylabel("인구수 (명)", fontsize=12)

# 세로축 그리드(구분선) 및 천 단위 콤마 포맷 설정
ax.grid(True, linestyle='--', alpha=0.6)
ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{int(x):,}'))

plt.xticks(rotation=45)
plt.tight_layout()

# 스트림릿에 그래프 출력
st.pyplot(fig)

# 하단
