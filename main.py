import streamlit as st
st.title('나의 첫 웹 서비스 만들기!')
a=st.text_input('이름을 입력하세요!')
b=st.selectbox('좋아하는 음식을 선택하세요',['마라탕','마라샹궈','마라떡볶이'])
if st.button('인사말 생성'):
  st.write('반갑습니다')
  st.info(a+'님, 안녕하세요!')
  st.warning(b+'를 좋아하시는군요!')
  st.error('잘부탁드려요!')
