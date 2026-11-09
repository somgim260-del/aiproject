import os
import streamlit as st
import pandas as pd
import plotly.express as px

# 스트림릿 페이지 설정
st.set_page_config(
    page_title="MBTI별 국가 순위 분석",
    page_icon="🏆",
    layout="wide"
)

# 데이터 로드 (상위 폴더의 CSV 파일 참조)
@st.cache_data
def load_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "..", "countriesMBTI_16types.csv")
    df = pd.read_csv(file_path)
    return df

df = load_data()

st.title("🏆 MBTI 유형별 전 세계 국가 순위")
st.write("원하는 MBTI 유형을 선택하면, 해당 비율이 높은 국가부터 낮은 국가까지 순서대로 막대그래프로 보여줍니다.")

# MBTI 16가지 유형 리스트
mbti_columns = [
    'INFJ', 'ISFJ', 'INTP', 'ISFP', 'ENTP', 'INFP', 'ENTJ', 'ISTP',
    'INTJ', 'ESFP', 'ESTJ', 'ENFP', 'ESTP', 'ISTJ', 'ENFJ', 'ESFJ'
]

# 화면 레이아웃 구성 (선택 박스 및 슬라이더)
col1, col2 = st.columns([1, 1])
with col1:
    selected_mbti = st.selectbox("조회할 MBTI 유형을 선택하세요:", options=mbti_columns, index=0)
with col2:
    top_n = st.slider("표시할 상위 국가 수:", min_value=5, max_value=len(df), value=20)

if selected_mbti:
    # 선택된 MBTI 기준으로 내림차순 정렬 (높은 나라 -> 낮은 나라)
    sorted_df = df[['Country', selected_mbti]].sort_values(by=selected_mbti, ascending=False).head(top_n)
    sorted_df.columns = ["Country", "Ratio"]
    
    # Plotly 막대그래프 생성 (세련된 퍼플 그라데이션 컬러 적용)
    fig = px.bar(
        sorted_df,
        x="Country",
        y="Ratio",
        color="Ratio",
        color_continuous_scale="Purples",
        title=f"📊 '{selected_mbti}' 비율이 높은 상위 {top_n}개 국가 순위",
        text_auto=".2%"
    )
    
    fig.update_layout(
        xaxis_title="국가",
        yaxis_title="비율",
        yaxis_tickformat=".1%",
        xaxis_tickangle=-45,
        height=600,
        coloraxis_showscale=False
    )
    
    st.plotly_chart(fig, use_container_width=True)

    # 세부 데이터 표 출력 (전체 순위 확인 가능)
    with st.expander("📄 전체 국가 순위 데이터 상세 보기"):
        full_sorted_df = df[['Country', selected_mbti]].sort_values(by=selected_mbti, ascending=False).reset_index(drop=True)
        full_sorted_df.columns = ["Country", "Ratio"]
        full_sorted_df.index = full_sorted_df.index + 1
        st.dataframe(full_sorted_df.style.format({"Ratio": "{:.2%}"}), use_container_width=True)
