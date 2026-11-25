import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# 페이지 기본 설정
st.set_page_config(page_title="펭귄 종 예측기", page_icon="🐧", layout="wide")

st.title("🐧 펭귄 종(Species) 예측 머신러닝 앱")
st.markdown("왼쪽 사이드바에서 펭귄의 신체 치수를 조절하면, **랜덤 포레스트(Random Forest)** 모델이 펭귄의 종을 예측하고 데이터 분포를 보여줍니다.")

# 1. 데이터 로드 및 모델 학습 (캐싱을 통해 속도 최적화)
@st.cache_data
def load_and_train():
    # seaborn 내장 펭귄 데이터 로드 및 결측치 제거
    df = sns.load_dataset("penguins").dropna()
    
    # 사용할 특성(Feature)과 타겟(Target) 설정
    features = ['bill_length_mm', 'bill_depth_mm', 'flipper_length_mm', 'body_mass_g']
    X = df[features]
    y = df['species']
    
    # 학습 데이터와 테스트 데이터 분리 (8:2)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # 랜덤 포레스트 모델 학습
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # 정확도 계산
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    
    return df, model, acc

df, model, accuracy = load_and_train()

# 2. 사이드바: 사용자 입력 슬라이더
st.sidebar.header("📏 펭귄 신체 치수 입력")

def user_input_features():
    bill_length = st.sidebar.slider(
        "부리 길이 (Bill Length, mm)",
        float(df['bill_length_mm'].min()),
        float(df['bill_length_mm'].max()),
        float(df['bill_length_mm'].mean())
    )
    bill_depth = st.sidebar.slider(
        "부리 깊이 (Bill Depth, mm)",
        float(df['bill_depth_mm'].min()),
        float(df['bill_depth_mm'].max()),
        float(df['bill_depth_mm'].mean())
    )
    flipper_length = st.sidebar.slider(
        "날개 길이 (Flipper Length, mm)",
        float(df['flipper_length_mm'].min()),
        float(df['flipper_length_mm'].max()),
        float(df['flipper_length_mm'].mean())
    )
    body_mass = st.sidebar.slider(
        "몸무게 (Body Mass, g)",
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

# 3. 모델 예측 및 확률 계산
prediction = model.predict(input_df)
prediction_proba = model.predict_proba(input_df)

# 4. 메인 화면 레이아웃 구성 (2단 컬럼)
col1, col2 = st.columns([1, 1.3])

with col1:
    st.subheader("📊 모델 성능 및 예측 결과")
    
    # 모델 정확도 표시
    st.metric(label="랜덤 포레스트 모델 정확도 (Accuracy)", value=f"{accuracy * 100:.2f}%")
    
    st.divider()
    
    # 예측된 종 출력
    st.success(f"예측된 펭귄의 종: **{prediction[0]}**")
    
    # 종별 예측 확률 테이블 및 막대 차트
    st.write("**종별 예측 확률:**")
    proba_df = pd.DataFrame(prediction_proba, columns=model.classes_)
    proba_df_formatted = proba_df.T.rename(columns={0: "확률"})
    proba_df_formatted["확률 (%)"] = (proba_df_formatted["확률"] * 100).round(2)
    
    st.dataframe(proba_df_formatted[["확률 (%)"]], use_container_width=True)
    st.bar_chart(proba_df.T)

with col2:
    st.subheader("📍 기존 데이터 분포와 입력값 위치")
    
    # 산점도 축 선택 옵션 제공 (기본값: 부리 길이 vs 부리 깊이)
    axis_options = {
        "부리 길이 (mm)": "bill_length_mm",
        "부리 깊이 (mm)": "bill_depth_mm",
        "날개 길이 (mm)": "flipper_length_mm",
        "몸무게 (g)": "body_mass_g"
    }
    
    sub_col1, sub_col2 = st.columns(2)
    with sub_col1:
        x_label = st.selectbox("X축 선택", list(axis_options.keys()), index=0)
    with sub_col2:
        y_label = st.selectbox("Y축 선택", list(axis_options.keys()), index=1)
        
    x_col = axis_options[x_label]
    y_col = axis_options[y_label]
    
    # Matplotlib & Seaborn 산점도 그리기
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # 기존 데이터 분포
    sns.scatterplot(
        data=df,
        x=x_col,
        y=y_col,
        hue="species",
        style="species",
        s=80,
        alpha=0.75,
        palette="Set2",
        ax=ax
    )
    
    # 사용자 입력 위치 강조 (빨간색 별표)
    ax.scatter(
        input_df[x_col],
        input_df[y_col],
        color="red",
        s=300,
        marker="*",
        edgecolor="black",
        linewidth=1.5,
        label="Your Input",
        zorder=5
    )
    
    ax.set_title(f"Penguin Distribution: {x_col} vs {y_col}", fontsize=13, fontweight="bold")
    ax.set_xlabel(x_col, fontsize=11)
    ax.set_ylabel(y_col, fontsize=11)
    ax.legend(title="Species / Input")
    ax.grid(True, linestyle="--", alpha=0.4)
    
    st.pyplot(fig)

# 하단: 사용자 입력값 요약 표시
with st.expander("현재 입력된 수치 상세 보기"):
    st.dataframe(input_df, use_container_width=True)
