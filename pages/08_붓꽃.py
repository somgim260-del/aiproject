import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score

# 페이지 기본 설정
st.set_page_config(page_title="Iris Species Predictor", page_icon="🌸", layout="centered")

# 1. 데이터 로드 및 전처리
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("Iris.csv", encoding="cp949")
    except UnicodeDecodeError:
        df = pd.read_csv("Iris.csv", encoding="utf-8")
    
    df.columns = df.columns.str.strip()
    return df

df = load_data()

# 2. 3개의 머신러닝 모델 학습
@st.cache_resource
def train_models(df):
    X = df[["꽃잎 길이", "꽃잎 너비"]]
    y = df["품종"]
    
    # 모델 3개 정의
    models = {
        "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42),
        "Logistic Regression": LogisticRegression(max_iter=200, random_state=42),
        "Support Vector Machine": SVC(probability=True, random_state=42)
    }
    
    # 학습
    for name, model in models.items():
        model.fit(X, y)
        
    return models

models = train_models(df)

# 데이터 기반 입력 허용 범위 계산
min_len, max_len = float(df["꽃잎 길이"].min()), float(df["꽃잎 길이"].max())
min_wid, max_wid = float(df["꽃잎 너비"].min()), float(df["꽃잎 너비"].max())

# UI 구성
st.title("🌸 Multi-Model Iris Species Predictor")
st.write("Compare predictions and performance across **3 different classification algorithms** based on petal dimensions.")

st.divider()

# 입력 범위 안내
st.subheader("📏 Allowed Input Range")
st.info(
    f"- **Petal Length:** `{min_len} cm` ~ `{max_len} cm`\n"
    f"- **Petal Width:** `{min_wid} cm` ~ `{max_wid} cm`"
)

# 사용자 입력 받기
col1, col2 = st.columns(2)
with col1:
    petal_length = st.number_input(
        "Petal Length (cm)",
        min_value=min_len,
        max_value=max_len,
        value=3.8,
        step=0.1,
        format="%.1f"
    )
with col2:
    petal_width = st.number_input(
        "Petal Width (cm)",
        min_value=min_wid,
        max_value=max_wid,
        value=1.2,
        step=0.1,
        format="%.1f"
    )

# 3개의 알고리즘으로 예측 수행 및 결과 비교 데이터 만들기
input_data = pd.DataFrame([[petal_length, petal_width]], columns=["꽃잎 길이", "꽃잎 너비"])

comparison_results = []
for name, model in models.items():
    pred = model.predict(input_data)[0]
    proba = model.predict_proba(input_data)[0]
    max_proba = max(proba) * 100
    comparison_results.append({
        "Algorithm": name,
        "Predicted Species": pred,
        "Confidence (%)": f"{max_proba:.1f}%"
    })

comparison_df = pd.DataFrame(comparison_results)

st.divider()
st.subheader("🔮 Comparison of 3 Algorithm Results")
st.dataframe(comparison_df, use_container_width=True)

# 4. 시각화 (그래프 내부 한글 제거 완료)
st.divider()
st.subheader("📊 Data Distribution & User Input Location")

fig, ax = plt.subplots(figsize=(8, 5))
colors = {"Iris-setosa": "#66c2a5", "Iris-versicolor": "#fc8d62", "Iris-virginica": "#8da0cb"}

for species, group in df.groupby("품종"):
    ax.scatter(
        group["꽃잎 길이"],
        group["꽃잎 너비"],
        color=colors.get(species, "gray"),
        label=species,
        s=70,
        alpha=0.8,
        edgecolors="none"
    )

# 사용자 입력값 노란색 별 표시
ax.scatter(
    petal_length,
    petal_width,
    color="gold",
    edgecolor="black",
    marker="*",
    s=450,
    zorder=10,
    label="User Input"
)

ax.set_title("Petal Length vs Petal Width Distribution", fontsize=14, fontweight="bold")
ax.set_xlabel("Petal Length (cm)", fontsize=11)
ax.set_ylabel("Petal Width (cm)", fontsize=11)
ax.legend(title="Classes", loc="upper left")
ax.grid(True, linestyle="--", alpha=0.4)

st.pyplot(fig)

# 5. 3가지 알고리즘 작동 원리 설명
st.divider()
st.subheader("💡 How the 3 Algorithms Work")

st.markdown("""
1. **🌲 랜덤 포레스트 (Random Forest)**
   * **작동 원리:** 여러 개의 **결정 트리(Decision Tree)**를 무작위로 생성한 뒤, 각 트리가 내린 예측 결과를 모아 **다수결 투표(Majority Voting)** 방식으로 최종 품종을 결정합니다. 
   * **특징:** 과적합(Overfitting)에 강하고 직관적이며 정확도가 높습니다.

2. **📈 로지스틱 회귀 (Logistic Regression)**
   * **작동 원리:** 이름은 '회귀'이지만 실제로는 **분류(Classification)** 알고리즘입니다. 입력 데이터에 가중치를 곱해 선형 방정식을 세운 뒤, **시그모이드(Sigmoid) 또는 소프트맥스(Softmax) 함수**를 통과시켜 각 품종에 속할 확률(0~1 사이 값)을 계산합니다.
   * **특징:** 결과 도출 과정이 투명하고 계산 속도가 매우 빠릅니다.

3. **📐 서포트 벡터 머신 (SVM - Support Vector Machine)**
   * **작동 원리:** 데이터들을 공간상에 좌표로 찍은 후, 품종 간의 경계선(초평면, Hyperplane)을 그어 분류합니다. 이때 서로 다른 품종 간의 **마진(Margin, 여백)이 최대가 되는 최적의 경계선**을 찾아내는 것이 핵심입니다.
   * **특징:** 데이터 군집 간의 경계가 명확할 때 뛰어난 분류 성능을 보여줍니다.
""")
