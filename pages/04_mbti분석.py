import os
import streamlit as st
import pandas as pd
import plotly.express as px

# 스트림릿 페이지 설정
st.set_page_config(
    page_title="국가별 MBTI 비율 분석",
    page_icon="🌍",
    layout="wide"
)

# 데이터 로드 (상위 폴더의 CSV 파일 참조)
@st.cache_data
def load_data():
    # 현재 파일(app.py)의 디렉토리 기준으로 상위 폴더 경로 설정
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "..", "countriesMBTI_16types.csv")
    
    df = pd.read_csv(file_path)
    return df

df = load_data()

st.title("🌍 국가별 MBTI 비율 시각화")
st.write("국가를 선택하면 16가지 MBTI 유형의 비율을 막대그래프로 확인할 수 있습니다.")

# 국가 선택 드롭다운 (기본값: South Korea 또는 첫 번째 국가)
default_idx = 0
if "South Korea" in df["Country"].values:
    default_idx = int(df[df["Country"] == "South Korea"].index[0])

selected_country = st.selectbox(
    "국가를 선택하세요:",
    options=df["Country"].unique(),
    index=default_idx
)

if selected_country:
    # 선택된 국가 데이터 추출
    country_data = df[df["Country"] == selected_country].drop(columns=["Country"]).iloc[0]
    
    # 비율 기준 내림차순 정렬
    sorted_mbti = country_data.sort_values(ascending=False).reset_index()
    sorted_mbti.columns = ["MBTI", "Ratio"]
    
    # ----------------------------------------------------
    # 색상 할당: 1위는 빨간색, 2~16위는 파란색 그라데이션
    # ----------------------------------------------------
    blue_gradient = [
        "#1E3A8A", "#1D4ED8", "#2563EB", "#3B82F6", "#60A5FA",
        "#6B7280", "#7C3AED", "#6366F1", "#4F46E5", "#4338CA",
        "#3730A3", "#312E81", "#60A5FA", "#93C5FD", "#BFDBFE"
    ]
    
    # 1위: Red (#E63946), 나머지 15개: 파란색 그라데이션
    color_discrete_sequence = ["#E63946"] + blue_gradient[:15]
    
    # Plotly 막대그래프 생성
    fig = px.bar(
        sorted_mbti,
        x="MBTI",
        y="Ratio",
        color="MBTI",
        color_discrete_sequence=color_discrete_sequence,
        title=f"📊 {selected_country}의 MBTI 비율 분포 (1위 강조 및 순위별 색상)",
        text_auto=".2%"
    )
    
    fig.update_layout(
        xaxis_title="MBTI 유형",
        yaxis_title="비율",
        yaxis_tickformat=".1%",
        showlegend=False,
        height=550
    )
    
    st.plotly_chart(fig, use_container_width=True)

    # 세부 데이터 표 출력
    with st.expander("📄 데이터 상세 보기"):
        st.dataframe(sorted_mbti.style.format({"Ratio": "{:.2%}"}), use_container_width=True)
