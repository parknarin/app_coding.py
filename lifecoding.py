import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from PIL import Image

# --- 기본 설정 ---
st.set_page_config(page_title="라이프 코딩", layout="wide")

if 'db' not in st.session_state:
    st.session_state.db = {
        'routines': [],
        'events': [],
        'diaries': {},
        'accounts': {},
        'study_logs': {},
        'goals': [],
        'quotes': []  # 직접 입력한 어록 저장소
    }

# --- 사이드바 메뉴 ---
menu = st.sidebar.radio("메인 카테고리", ["할 일 체크", "캘린더", "기타 기능"])

# --- [기능 1] 할 일 체크 ---
if menu == "할 일 체크":
    st.header("✅ 할 일 체크")
    with st.expander("➕ 새 습관 추가"):
        with st.form("routine_form"):
            r_name = st.text_input("습관 이름")
            r_type = st.selectbox("반복 설정", ["요일별", "일수별", "매달 특정일"])
            r_time = st.time_input("알림 시각")
            r_share = st.toggle("친구와 공유")
            if st.form_submit_button("완료"):
                st.session_state.db['routines'].append({"name": r_name, "type": r_type, "time": str(r_time), "count": 0})
                st.rerun()

    for i, r in enumerate(st.session_state.db['routines']):
        col1, col2 = st.columns([4, 1])
        with col1: st.write(f"**{r['name']}** ({r['type']} / ⏰ {r['time']})")
        with col2:
            if st.button("체크", key=f"r_chk_{i}"):
                r['count'] += 1
                st.rerun()

# --- [기능 2] 캘린더 ---
elif menu == "캘린더":
    st.header("📅 캘린더")
    sel_date = st.date_input("날짜 선택", datetime.now())
    with st.expander(f"➕ {sel_date} 일정 추가"):
        with st.form("cal_form"):
            c_title = st.text_input("일정 제목")
            c_sub = st.text_area("세부 할 일")
            c_time = st.time_input("일정 시각")
            if st.form_submit_button("완료"):
                st.session_state.db['events'].append({"date": sel_date, "title": c_title, "sub": c_sub, "time": c_time})
                st.rerun()

    for e in st.session_state.db['events']:
        if e['date'] == sel_date:
            st.info(f"**[{e['time']}] {e['title']}**\n\n{e['sub']}")

# --- [기능 3] 기타 기능 ---
elif menu == "기타 기능":
    sub = st.selectbox("세부 기능 선택", ["명언", "일기", "가계부", "공부 플래너", "목표 성취", "학사 일정", "소셜", "휴식", "잡동사니"])

    if sub == "어록":
        st.subheader("📜 어록 수집 및 기록")
        with st.form("quote_form"):
            q_text = st.text_input("찾아본 명언 입력")
            q_author = st.text_input("인물/출처")
            q_memo = st.text_area("내 생각 기록")
            if st.form_submit_button("완료"):
                st.session_state.db['quotes'].append({"text": q_text, "author": q_author, "memo": q_memo})
                st.rerun()
        
        for q in st.session_state.db['quotes']:
            st.warning(f"\"{q['text']}\" - {q['author']}")
            st.write(f"💭 내 생각: {q['memo']}")

    elif sub == "일기":
        d_date = st.date_input("날짜", key="d_date")
        d_title = st.text_input("제목")
        d_content = st.text_area("내용")
        d_img = st.file_uploader("사진 추가", type=['png', 'jpg'])
        if st.button("완료"):
            st.session_state.db['diaries'][d_date] = {"title": d_title, "content": d_content}
            st.success("저장되었습니다.")

    elif sub == "가계부":
        st.subheader("💰 가계부")
        a_date = st.date_input("날짜", key="a_date")
        if a_date not in st.session_state.db['accounts']: st.session_state.db['accounts'][a_date] = []
        c1, c2 = st.columns(2)
        item = c1.text_input("항목")
        price = c2.number_input("가격", step=1)
        if st.button("추가"):
            st.session_state.db['accounts'][a_date].append({"항목": item, "가격": price})
        df = pd.DataFrame(st.session_state.db['accounts'][a_date])
        if not df.empty:
            st.table(df)
            st.write(f"**합계: {df['가격'].sum()}**")

    elif sub == "공부 플래너":
        st.subheader("✍️ 공부 플래너")
        st.warning("⚠️ **주의:** 과목명을 입력할 때 오탈자가 나면 각각 다른 습관으로 측정되어 합산되지 않으니 정확히 입력하세요!")
        now_h = datetime.now().hour
        for h in range(24):
            if h == now_h: st.markdown("<hr style='border:2px solid red'>", unsafe_allow_html=True)
            c1, c2, c3 = st.columns([1, 3, 1])
            c1.write(f"{h:02d}:00")
            c2.text_input("계획", key=f"s_{h}")
            c3.checkbox("완료", key=f"sc_{h}")

    elif sub == "목표 성취":
        with st.form("g_form"):
            g_t = st.text_input("목표명")
            g_d = st.date_input("달성 목표일")
            if st.form_submit_button("완료"):
                st.session_state.db['goals'].append({"title": g_t, "end": g_d, "start": datetime.now().date()})
        for g in st.session_state.db['goals']:
            st.markdown(f"### **{g['title']}**")
            st.write(f"기한: {g['end']}")

    elif sub == "학사 일정":
        st.date_input("일정 날짜")
        st.text_input("내용")
        st.button("완료")

    elif sub == "소셜":
        st.write("공유된 습관 열람")
        st.text_input("댓글")
        st.button("완료")

    elif sub == "휴식":
        st.subheader("🎡 휴식")
        st.write("오늘의 운세 / 게임")

    elif sub == "잡동사니":
        st.subheader("📦 잡동사니")
        st.write("스키틀즈 AI 채팅 / 알람")
        st.text_input("메시지 입력")
        st.button("전송")
