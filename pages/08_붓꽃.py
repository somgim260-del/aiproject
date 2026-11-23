import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
import platform

# 운영체제별 기본 한글 폰트 설정 (koreanize-matplotlib 대체)
def set_font():
    system_name = platform.system()
    if system_name == "Windows":
        plt.rc("font", family="Malgun Gothic")
    elif system_name == "Darwin":  # Mac
        plt.rc("font", family="AppleGothic")
    else:  # Linux (Streamlit Cloud 환경)
        # 리눅스 환경에서 기본 제공되는 Nanum 폰트 등 설정 시도
        plt.rc("font", family="NanumGothic")
    
    # 마이너스(-) 기호 깨짐 방지
    plt.rcParams["axes.unicode_minus"] = False

set_font()

# 페이지 기본 설정
st.set_page_config(page_title="붓꽃(Iris) 품종 예측기", page_icon="🌸", layout="centered")

# 1. 데이터 로드 및 전처리 (캐싱으로 속도 최적화)
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("Iris.csv", encoding="cp949")
    except UnicodeDecodeError:
        df = pd.read_csv("Iris.csv", encoding="utf-8")
    
    # 컬럼명 앞뒤 공백 제거 ('꽃잎 너비 ' -> '꽃잎 너비')
    df.columns = df.columns.str.strip()
    return df

# 2. 머신러닝 모델 학습 (Random Forest)
@st.cache_resource
def train_model(df):
    X = df[["꽃잎 길이", "꽃잎 너비"]]
    y = df["품종"]
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    return model

df = load_data()
model = train_model(df)

# 데이터 기반 입력 허용 범위 계산
min_len, max_len = float(df["꽃잎 길이"].min()), float(df["꽃잎 길이"].max())
min_wid, max_wid = float(df["꽃잎 너비"].min()), float(df["꽃잎 너비"].max())

# UI 구성
st.title("🌸 붓꽃(Iris) 품종 예측 웹 앱")
st.write("꽃잎의 길이와 너비를 입력하면 **랜덤 포레스트(Random Forest)** 알고리즘으로 붓꽃의 품종을 예측합니다.")

st.divider()

# 4. 입력 가능한 값의 범위 안내
st.subheader("📏 입력 가능 범위 안내")
st.info(
    f"- **꽃잎 길이 (Petal Length):** `{min_len} cm` ~ `{max_len} cm`\n"
    f"- **꽃잎 너비 (Petal Width):** `{min_wid} cm` ~ `{max_wid} cm`"
)

# 2. 사용자 입력 받기
col1, col2 = st.columns(2)
with col1:
    petal_length = st.number_input(
        "꽃잎 길이 (cm) 입력",
        min_value=min_len,
        max_value=max_len,
        value=3.8,
        step=0.1,
        format="%.1f"
    )
with col2:
    petal_width = st.number_input(
        "꽃잎 너비 (cm) 입력",
        min_value=min_wid,
        max_value=max_wid,
        value=1.2,
        step=0.1,
        format="%.1f"
    )

# 3. 품종 예측 실행
input_data = pd.DataFrame([[petal_length, petal_width]], columns=["꽃잎 길이", "꽃잎 너비"])
prediction = model.predict(input_data)[0]
prediction_proba = model.predict_proba(input_data)[0]

st.divider()
st.subheader("🔮 예측 결과")
st.success(f"입력하신 조건의 붓꽃은 **{prediction}** 품종으로 예측됩니다!")

# 품종별 예측 확률 표시
proba_df = pd.DataFrame(
    [prediction_proba * 100],
    columns=model.classes_,
    index=["예측 확률 (%)"]
)
st.dataframe(proba_df.style.format("{:.1f}%"), use_container_width=True)

# 5. 산점도 시각화 (사용자 입력값: 노란색 별)
st.divider()
st.subheader("📊 데이터 분포 및 입력 위치 시각화")

fig, ax = plt.subplots(figsize=(8, 5))

# 기존 데이터 품종별 산점도 그리기
sns.scatterplot(
    data=df,
    x="꽃잎 길이",
    y="꽃잎 너비",
    hue="품종",
    palette="Set2",
    s=70,
    alpha=0.8,
    ax=ax
)

# 사용자 입력값을 노란색 별(*)로 표시
ax.scatter(
    petal_length,
    petal_width,
    color="gold",
    edgecolor="black",
    marker="*",
    s=450,
    zorder=10,
    label="사용자 입력값"
)

ax.set_title("품종별 꽃잎 길이 vs 꽃잎 너비 분포", fontsize=14, fontweight="bold")
ax.set_xlabel("꽃잎 길이 (cm)", fontsize=11)
ax.set_ylabel("꽃잎 너비 (cm)", fontsize=11)
ax.legend(title="구분", loc="upper left")
ax.grid(True, linestyle="--", alpha=0.4)

st.pyplot(fig)
