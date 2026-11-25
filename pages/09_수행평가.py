import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 기본 설정
st.set_page_config(page_title="🕊️ 국내 조류 분포 탐색기", page_icon="🐦", layout="wide")

st.title("🕊️ 국내 조류 분포 데이터 탐색기")
st.markdown("대한민국 국내 조류 분포 데이터를 바탕으로, 어떤 새들이 어디서 관찰되었는지 인터랙티브하게 살펴보자! 🌿")

# 1. 데이터 로드 함수 (캐싱 적용으로 속도 향상)
@st.cache_data
def load_data():
    # 공공데이터포털 CSV 파일은 인코딩이 'cp949' 또는 'euc-kr'인 경우가 많습니다.
    try:
        df = pd.read_csv("한국과학기술정보연구원_국내 조류분포_20211124.csv", encoding="cp949")
    except UnicodeDecodeError:
        df = pd.read_csv("한국과학기술정보연구원_국내 조류분포_20211124.csv", encoding="utf-8")
    return df

df = load_data()

# 2. 사이드바: 필터 설정
st.sidebar.header("🔍 조류 검색 및 필터")

# 보호종 여부 필터
protection_filter = st.sidebar.selectbox(
    "보호종 여부 선택",
    ["전체", "Y (보호종)", "N (일반)"]
)

if protection_filter == "Y (보호종)":
    filtered_df = df[df['보호종 여부'] == 'Y']
elif protection_filter == "N (일반)":
    filtered_df = df[df['보호종 여부'] == 'N']
else:
    filtered_df = df

# 조류 이름(국명) 검색
bird_name = st.sidebar.text_input("새 이름 검색 (예: 큰고니, 왜가리, 백로)", "")

if bird_name:
    filtered_df = filtered_df[filtered_df['국명(원병오2000)'].str.contains(bird_name, na=False)]

# 3. 메인 화면 레이아웃
st.subheader("📊 조류 관찰 데이터 요약")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="총 관찰 기록 건수", value=f"{len(filtered_df):,} 건")
with col2:
    st.metric(label="등장한 조류 종류(종 수)", value=f"{filtered_df['국명(원병오2000)'].nunique():,} 종")
with col3:
    st.metric(label="총 관찰 개체 수", value=f"{filtered_df['관찰개체수'].sum():,} 마리")

st.divider()

# 4. 시각화 영역 (Plotly 인터랙티브 그래프)
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("🏆 가장 많이 관찰된 조류 Top 10")
    top_birds = filtered_df.groupby('국명(원병오20000)' if '국명(원병오20000)' in filtered_df.columns else '국명(원병오20000)' not in filtered_df.columns and '국명(원병오2000)'['국명(원병오2000)'].name or '국명(원병오2000)')['관찰개체수'].sum().reset_index()
    # 상위 10개 정렬
    top_birds = filtered_df.groupby('국명(원병오20000)' if '국명(원병오20000)' in filtered_df.columns else '국명(원병오2000)')['관찰개체수'].sum().reset_index()
    top_birds = top_birds.sort_values(by='관찰개체수', ascending=False).head(10)
    
    fig_top = px.bar(
        top_birds,
        x='관찰개체수',
        y='국명(원병오2000)',
        orientation='h',
        title="조류별 총 관찰 개체 수 Top 10",
        labels={'관찰개체수': '총 관찰 개체 수', '국명(원병오2000)': '새 이름'},
        color='관찰개체수',
        color_continuous_scale='Reds'
    )
    fig_top.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_top, use_container_width=True)

with col_b:
    st.subheader("📍 주요 행정구역별 관찰 현황 Top 10")
    top_regions = filtered_df.groupby('행정구역')['관찰개체수'].sum().reset_index()
    top_regions = top_regions.sort_values(by='관찰개체수', ascending=False).head(10)
    
    fig_reg = px.bar(
        top_regions,
        x='관찰개체수',
        y='행정구역',
        orientation='h',
        title="지역별 조류 관찰 개체 수 Top 10",
        labels={'관찰개체수': '총 관찰 개체 수', '행정구역': '행정구역'},
        color='관찰개체수',
        color_continuous_scale='Blues'
    )
    fig_reg.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_reg, use_container_width=True)

# 5. 데이터 테이블 미리보기
st.subheader("📋 필터링된 조류 데이터 상세 보기")
st.dataframe(filtered_df[['자료번호', '보호종 여부', '국명(원병오2000)', '영문명(원병오2000)', '관찰개체수', '조사지역', '행정구역', '관찰시기']], use_container_width=True)

# 하단 팁
st.divider()
st.caption("💡 팁: 왼쪽 사이드바에서 보호종 여부를 선택하거나 특정 새 이름을 검색해서 원하는 데이터를 자세히 살펴보세요!")
