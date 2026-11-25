import streamlit as st
import pandas as pd
import seaborn as sns
import plotly.express as px
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# 페이지 기본 설정
st.set_page_config(page_title="🐧 펭귄 종 맞추기 마법사", page_icon="🐧", layout="wide")

st.title("🐧 안녕! 나는 펭귄 박사 봇이야! 👋")
st.markdown("왼쪽 사이드바에서 펭귄의 신체 치수를 요리조리 조절해봐! 어떤 펭귄인지 척척 맞춰줄게! ✨")

# 1. 데이터 로드 및 모델 학습 (캐싱 적용으로 빠르게 동작!)
@st.cache_data
def load_and_train():
    # 펭귄 데이터를 불러오고 빈칸(결측치) 제거
    df = sns.load_dataset("penguins").dropna()
    
    # 사용할 특징과 정답(종) 분리
    features = ['bill_length_mm', 'bill_depth_mm', 'flipper_length_mm', 'body_mass_g']
    X = df[features]
    y = df['species']
    
    # 학습/테스트 셋 나누기
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # 랜덤 포레스트 모델 훈련
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # 모델 정확도 측정
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    
    return df, model, acc

df, model, accuracy = load_and_train()

# 2. 사이드바: 슬라이더로 입력받기
st.sidebar.header("🎛️ 펭귄 신체 치수를 조절해봐!")

def user_input_features():
    bill_length = st.sidebar.slider(
        "📏 부리 길이 (Bill Length, mm)",
        float(df['bill_length_mm'].min()),
        float(df['bill_length_mm'].max()),
        float(df['bill_length_mm'].mean())
    )
    bill_depth = st.sidebar.slider(
        "📐 부리 깊이 (Bill Depth, mm)",
        float(df['bill_depth_mm'].min()),
        float(df['bill_depth_mm'].max()),
        float(df['bill_depth_mm'].mean())
    )
    flipper_length = st.sidebar.slider(
        "🏊 날개 길이 (Flipper Length, mm)",
        float(df['flipper_length_mm'].min()),
        float(df['flipper_length_mm'].max()),
        float(df['flipper_length_mm'].mean())
    )
    body_mass = st.sidebar.slider(
        "⚖️ 몸무게 (Body Mass, g)",
        float(df['body_mass_g'].min()),
        float(df['body_mass_g'].max()),
        float(df['body_mass_g'].mean())
    )
    
    data = {
        'bill_length_mm': bill_length,
        'bill_depth_mm': bill_depth,
        'flipper_length_mm': flipper_length,
        'body_mass_g': body_mass
    }
    return pd.DataFrame(data, index=[0])

input_df = user_input_features()

# 3. 예측 실행
prediction = model.predict(input_df)
prediction_proba = model.predict_proba(input_df)

# 4. 화면 레이아웃 (2단 구성)
col1, col2 = st.columns([1, 1.4])

with col1:
    st.subheader("🎯 예측 결과 및 모델 성능")
    
    # 모델 정확도 표시
    st.info(f"🤖 AI 모델 정확도(Accuracy): **{accuracy * 100:.2f}%**")
    
    # 예측된 펭귄 종 안내
    st.success(f"🎉 짜잔! 이 펭귄의 종은 **{prediction[0]}** 이야!")
    
    st.write("📊 **종별 예측 확률을 확인해봐:**")
    proba_df = pd.DataFrame(prediction_proba, columns=model.classes_)
    proba_df_formatted = proba_df.T.rename(columns={0: "확률"})
    proba_df_formatted["확률 (%)"] = (proba_df_formatted["확률"] * 100).round(2)
    
    st.dataframe(proba_df_formatted[["확률 (%)"]], use_container_width=True)
    st.bar_chart(proba_df.T)

with col2:
    st.subheader("🗺️ 데이터 속 나의 펭귄 위치 찾기")
    st.markdown("마우스로 그래프를 확대·축소해 볼 수 있어! 빨간색 별표(*)가 지금 네가 입력한 펭귄이야. 🌟")
    
    # 사용자가 직접 축을 바꿔가며 볼 수 있게 선택 박스 제공
    axis_options = {
        "부리 길이 (mm)": "bill_length_mm",
        "부리 깊이 (mm)": "bill_depth_mm",
        "날개 길이 (mm)": "flipper_length_mm",
        "몸무게 (g)": "body_mass_g"
    }
    
    sub_col1, sub_col2 = st.columns(2)
    with sub_col1:
        x_label = st.selectbox("X축 데이터 선택", list(axis_options.keys()), index=0)
    with sub_col2:
        y_label = st.selectbox("Y축 데이터 선택", list(axis_options.keys()), index=1)
        
    x_col = axis_options[x_label]
    y_col = axis_options[y_label]
    
    # Plotly 인터랙티브 산점도 그리기
    fig = px.scatter(
        df, 
        x=x_col, 
        y=y_col, 
        color="species",
        symbol="species",
        title=f"펭귄 분포 지도: {x_label} vs {y_label}",
        labels={x_col: x_label, y_col: y_label, "species": "펭귄 종"}
    )
    
    # 사용자가 입력한 포인트를 빨간색 큰 별표로 추가
    user_point = pd.DataFrame({
        x_col: input_df[x_col],
        y_col: input_df[y_col],
        "species": ["✨ 내 입력값"]
    })
    
    fig_user = px.scatter(
        user_point,
        x=x_col,
        y=y_col,
        color_discrete_sequence=["red"],
        symbol_sequence=["star"]
    )
    
    # 그래프 합치기
    fig.add_trace(fig_user.data[0])
    fig.update_traces(marker=dict(size=18), selector=dict(mode='markers', name='✨ 내 입력값'))
    
    st.plotly_chart(fig, use_container_width=True)

# 하단 팁
st.divider()
st.caption("💡 팁: 사이드바의 슬라이더 숫자를 조금씩 바꿔가면서 펭귄의 종이 어떻게 바뀌는지 관찰해봐!")
