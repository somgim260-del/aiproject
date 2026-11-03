import streamlit as st
import folium
from streamlit_folium import st_folium

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="서울 주요 관광지 TOP 10",
    page_icon="🗽",
    layout="wide"
)

st.title("🗽 외국인이 사랑하는 서울 주요 관광지 TOP 10")
st.markdown("지도의 마커를 클릭하거나 아래 상세 설명을 통해 서울의 대표 관광지를 확인해 보세요.")

# 2. 관광지 데이터 (좌표, 이름, 간단한 설명)
tourist_spots = [
    {
        "name": "경복궁 (Gyeongbokgung Palace)",
        "lat": 37.5796,
        "lon": 126.9770,
        "desc": "조선 시대의 대표적인 궁궐로, 한국의 전통 건축과 역사를 느껴볼 수 있는 최고의 랜드마크입니다. 수문장 교대식과 한복 체험이 외국인들에게 매우 높은 인기를 끌고 있습니다."
    },
    {
        "name": "N서울타워 (N Seoul Tower)",
        "lat": 37.5512,
        "lon": 126.9882,
        "desc": "남산 정상에 위치하여 서울 도심의 전경을 한눈에 감상할 수 있는 명소입니다. 케이블카와 사랑의 자물쇠 존으로 잘 알려져 있습니다."
    },
    {
        "name": "북촌한옥마을 (Bukchon Hanok Village)",
        "lat": 37.5826,
        "lon": 126.9831,
        "desc": "조선 시대 고위 관료들이 거주하던 실제 한옥들이 잘 보존된 골목길입니다. 전통적인 미와 현대 도시의 대비를 선사합니다."
    },
    {
        "name": "명동 쇼핑거리 (Myeongdong)",
        "lat": 37.5636,
        "lon": 126.9822,
        "desc": "K-뷰티 제품, 패션 쇼핑몰, 그리고 다양한 길거리 음식(Street Food)을 즐길 수 있어 방문 필수 코스로 꼽힙니다."
    },
    {
        "name": "홍대 거리 (Hongdae)",
        "lat": 37.5563,
        "lon": 126.9226,
        "desc": "젊음과 인디 문화의 중심지로, 버스킹 공연, 개성 넘치는 카페, 라이브 클럽 등 밤낮으로 활기찬 분위기를 보여줍니다."
    },
    {
        "name": "동대문디자인플라자 (DDP)",
        "lat": 37.5665,
        "lon": 127.0092,
        "desc": "자하 하디드가 설계한 곡선 형태의 독특한 미래형 건축물입니다. 패션쇼, 전시회, 디자인 마켓이 상시 열립니다."
    },
    {
        "name": "인사동 (Insadong)",
        "lat": 37.5743,
        "lon": 126.9856,
        "desc": "전통 공예품, 골동품, 한지, 찻집 등이 집결되어 있는 곳으로 전통 문화를 체험하고 기념품을 사기에 좋습니다."
    },
    {
        "name": "롯데월드타워 & 서울스카이 (Lotte World Tower)",
        "lat": 37.5137,
        "lon": 127.1025,
        "desc": "123층, 높이 555m에 달하는 국내 최고층 빌딩으로, 전망대인 서울스카이에서 아찔한 전경을 감상할 수 있습니다."
    },
    {
        "name": "이태원 (Itaewon)",
        "lat": 37.5345,
        "lon": 126.9946,
        "desc": "다양한 국적의 다문화 레스토랑과 바, 특색 있는 상점들이 모여 있어 글로벌 문화를 쉽게 체감할 수 있는 지역입니다."
    },
    {
        "name": "청계천 (Cheonggyecheon Stream)",
        "lat": 37.5691,
        "lon": 126.9778,
        "desc": "도심 한복판을 흐르는 휴식공간으로, 산책로를 따라 야경을 즐기거나 등불 축제 등 계절별 행사를 즐기기에 유용합니다."
    }
]

# 3. 지도 생성 (서울 중심 coordinate)
m = folium.Map(location=[37.5512, 126.9882], zoom_start=12)

# 마커 추가
for spot in tourist_spots:
    folium.Marker(
        location=[spot["lat"], spot["lon"]],
        popup=folium.Popup(f"<b>{spot['name']}</b>", max_width=200),
        tooltip=spot["name"],
        icon=folium.Icon(color="red", icon="info-sign")
    ).add_to(m)

# 4. 지도 출력
st.subheader("📍 서울 지도")
st_folium(m, width=1000, height=500)

st.divider()

# 5. 관광지 설명 카드/목록 출력
st.subheader("ℹ️ 관광지 상세 설명")

cols = st.columns(2)  # 2열 레이아웃 배치

for idx, spot in enumerate(tourist_spots):
    col = cols[idx % 2]
    with col:
        with st.expander(f"**{idx + 1}. {spot['name']}**", expanded=True):
            st.write(spot["desc"])
