import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import os

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

st.title("🏙️ 서울시 자치구별 연령/성별 인구 분석 시각화")

# 데이터 로드 (상위 폴더에 있는 population.csv 참조)
@st.cache_data
def load_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.abspath(os.path.join(current_dir, '..', 'population.csv'))
    df = pd.read_csv(file_path, encoding='cp949')
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()

# 서울시 전체 행정구('서울특별시 (1100000000)')를 제외하고 25개 자치구만 필터링
districts_df = df[df['행정구역'].str.contains('구') & ~df['행정구역'].str.contains('서울특별시$')].copy()
districts = districts_df['행정구역'].unique()

# 사이드바 메뉴 선택
menu = st.sidebar.radio("📊 분석 메뉴 선택", ["1. 자치구별 남녀 연령별 인구", "2. 연령대별 자치구 순위 막대그래프"])

# 공통 연령대 정의
age_groups = [
    '0~9세', '10~19세', '20~29세', '30~39세', '40~49세', 
    '50~59세', '60~69세', '70~79세', '80~89세', '90~99세', '100세 이상'
]
years = ['2020년', '2021년', '2022년', '2023년', '2024년', '2025년']

if menu == "1. 자치구별 남녀 연령별 인구":
    st.subheader("📈 자치구별 남녀 연령별 인구 꺾은선 그래프")
    
    st.sidebar.header("조회 옵션")
    selected_district = st.sidebar.selectbox("행정구 선택", districts)
    selected_year = st.sidebar.selectbox("연도 선택", years)

    # 선택된 자치구 행 추출
    row = districts_df[districts_df['행정구역'] == selected_district]

    # 남성(핑크색: deeppink), 여성(초록색: green) 데이터 추출
    male_cols = [f"{selected_year}_남_거주자_{age}" for age in age_groups]
    female_cols = [f"{selected_year}_여_거주자_{age}" for age in age_groups]

    male_values, female_values = [], []
    for m_col, f_col in zip(male_cols, female_cols):
        m_val = row[m_col].values[0]
        f_val = row[f_col].values[0]
        
        if isinstance(m_val, str): m_val = int(m_val.replace(',', ''))
        if isinstance(f_val, str): f_val = int(f_val.replace(',', ''))
        
        male_values.append(m_val)
        female_values.append(f_val)

    # 꺾은선 그래프 그리기
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(age_groups, male_values, marker='o', color='deeppink', linewidth=2, label='남성')
    ax.plot(age_groups, female_values, marker='s', color='green', linewidth=2, label='여성')

    ax.set_title(f"{selected_district} - {selected_year} 남녀 연령별 인구 분포", fontsize=14, pad=15)
    ax.set_xlabel("연령 구간", fontsize=12)
    ax.set_ylabel("인구수 (명)", fontsize=12)

    ax.grid(True, linestyle='--', alpha=0.6)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{int(x):,}'))
    ax.legend()

    plt.xticks(rotation=45)
    plt.tight_layout()

    st.pyplot(fig)

    # 데이터 테이블 표시
    chart_df = pd.DataFrame({
        '연령대': age_groups,
        '남성 인구수': male_values,
        '여성 인구수': female_values
    })
    with st.expander("📊 상세 데이터 확인하기"):
        st.dataframe(chart_df)

else:
    st.subheader("📊 특정 연령대별 자치구 인구 순위 (막대그래프)")

    st.sidebar.header("조회 옵션")
    selected_year = st.sidebar.selectbox("연도 선택", years, key='rank_year')
    selected_age = st.sidebar.selectbox("연령대 선택 (10살 단위)", age_groups, key='rank_age')
    
    gender_rank_options = {
        "총인구": "거주자",
        "남성": "남_거주자",
        "여성": "여_거주자"
    }
    selected_gender_label = st.sidebar.selectbox("성별 선택", list(gender_rank_options.keys()), key='rank_gender')
    selected_gender_code = gender_rank_options[selected_gender_label]

    target_col = f"{selected_year}_{selected_gender_code}_{selected_age}"

    # 데이터프레임 복사 후 인구수 정수형 변환
    rank_df = districts_df.copy()
    rank_df['인구수'] = rank_df[target_col].astype(str).str.replace(',', '').astype(int)
    
    # 인구수가 많은 구 순서대로 내림차순 정렬
    rank_df = rank_df.sort_values(by='인구수', ascending=False)

    # 구 이름 깔끔하게 정리 (예: '서울특별시 종로구 (1111000000)' -> '종로구')
    rank_df['구이름'] = rank_df['행정구역'].str.split().str[1]

    # 막대그래프 그리기
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(rank_df['구이름'], rank_df['인구수'], color='forestgreen')

    ax.set_title(f"서울시 자치구별 {selected_age} ({selected_gender_label}) 현황 - {selected_year}", fontsize=14, pad=15)
    ax.set_xlabel("자치구", fontsize=12)
    ax.set_ylabel("인구수 (명)", fontsize=12)

    ax.grid(axis='y', linestyle='--', alpha=0.6)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{int(x):,}'))

    plt.xticks(rotation=90)
    plt.tight_layout()

    st.pyplot(fig)

    # 순위 데이터 테이블 표시
    with st.expander("📊 자치구별 순위표 데이터 확인하기"):
        display_df = rank_df[['구이름', '인구수']].reset_index(drop=True)
        display_df.index = display_df.index + 1
        display_df.columns = ['자치구', '인구수 (명)']
        st.dataframe(display_df)
