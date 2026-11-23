import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
import matplotlib.font_manager as fm
import os
import urllib.request

# 스트림릿 클라우드(리눅스) 환경에서 나눔고딕 폰트 자동 다운로드 및 설정
@st.cache_resource
def setup_font():
    font_path = "NanumGothic.ttf"
    if not os.path.exists(font_path):
        # 폰트 파일이 없으면 깃허브 등에서 나눔고딕 다운로드
        url = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Regular.ttf"
        try:
            urllib.request.urlretrieve(url, font_path)
        except Exception:
            pass
            
    if os.path.exists(font_path):
        fm.fontManager.add_font(font_path)
        plt.rc("font", family="NanumGothic")
    else:
        # 다운로드 실패 시 시스템 기본 폰트 사용
        plt.rc("font", family="sans-serif")
        
    # 마이너스(-) 기호 깨짐 방지
    plt.rcParams["axes.unicode_minus"] = False

setup_font()

# 페이지 기본 설정
st.set_page_config(page_title="붓꽃(Iris) 품종 예측기", page_icon="🌸", layout="centered")

# 1. 데이터 로드 및 전처리 (캐싱 적용)
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
st.title("🌸 붓꽃(Iris) 품
