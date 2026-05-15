import streamlit as st
import pandas as pd
import datetime
from datetime import timedelta
import matplotlib.pyplot as plt
from PIL import Image
import random

# ==========================================
# 0. 초기 세션 상태(Session State) 및 데이터베이스 모킹
# ==========================================
st.set_page_config(page_title="라이프 코딩", page_icon="🌱", layout="wide")

if "initialized" not in st.session_state:
    st.session_state.initialized = True
    # 루틴/습관 데이터 (할 일 체크)
    st.session_state.routines = [
        {"id": 1, "title": "국어 공부", "type": "요일별", "value": ["월", "수", "금"], "time": "10:00", "duration": 60, "subtasks": ["기출 1회 풀기", "오답노트"], "history": {"2026-05-15": True, "2026-05-16": False}},
        {"id": 2, "title": "방 정리", "type": "일수별", "value": 2, "time": "22:00", "duration": 15, "subtasks": [], "history": {"2026-05-16": True}},
        {"id": 3, "title": "다이어트 운동", "type": "매일", "value": "매일", "time": "07:00", "duration": 40, "subtasks": ["스트레칭", "유산소 30분"], "history": {"2026-05-16": False}}
    ]
    # 캘린더 일정 데이터
    st.session_state.events = [
        {"date": "2026-05-16", "title": "치팅데이", "time": "18:00", "duration": 120, "subtasks": ["피자 주문하기"], "type": "이벤트"},
        {"date": "2026-05-20", "title": "친구 생일 파티", "time": "19:00", "duration": 180, "subtasks": ["선물 사기", "선물 포장하기", "편지 쓰기"], "type": "이벤트"}
    ]
    # 일기 데이터
    st.session_state.diaries = {
        "2026-05-15": {"title": "정말 보람찬 하루", "content": "오늘 개발 공부를 열심히 했다. 뿌듯하다.", "image": None}
    }
    # 가계부 데이터
    st.session_state.ledger = [
        {"날짜": "2026-05-16", "항목 이름": "점심 식사", "가격": 12000},
        {"날짜": "2026-05-16", "항목 이름": "카페라떼", "가격": 5500}
    ]
    # 명언 데이터 및 사용자 감상문
    st.session_state.quotes = [
        {"quote": "늦었다고 생각할 때가 진짜 너무 늦었다. 그러니까 지금 해라.", "author": "박명수", "saved": True, "review": "정신이 번쩍 드는 명언이다."},
        {"quote": "중요한 것은 꺾이지 않는 마음.", "author": "데프트", "saved": False, "review": ""}
    ]
    # 공부 플래너 타임라인 데이터 (정각 기준)
    st.session_state.planner = {
        "2026-05-16": {hour: "" for hour in range(24)}
    }
    st.session_state.planner["2026-05-16"][10] = "국어 공부"
    st.session_state.planner["2026-05-16"][11] = "국어 공부"
    # 목표 성취 데이터
    st.session_state.goals = [
        {"title": "다이어트 15kg 감량", "start_date": "2026-05-01", "end_date": "2026-08-01", "tasks": "매일 공복 유산소, 밀가루 끊기"}
    ]
    # 학교 학사 일정 데이터
    st.session_state.school_events = [
        {"date": "2026-06-04", "title": "6월 모의평가"}
    ]
    # 소셜 데이터
    st.session_state.social_sharing = {1: True, 2: False, 3: False} # 루틴 ID별 공유 여부
    st.session_state.comments = {"2026-05-16_국어": [{"user": "친구A", "text": "열공하네! 화이팅 🔥"}]}
    st.session_state.dm_messages = []
    # 기타/휴식 설정
    st.session_state.alarm_color = "#FFD1DC" # 기본 파스텔 핑크

# 현재 시간 고정 (요구사항 기준 2026년 5월 16일 가정)
CURRENT_DATE_STR = "2026-05-16"
current_date = datetime.date(2026, 5, 16)

# ==========================================
# AI 알고리즘 추천 습관 (상단 표기용)
# ==========================================
def render_ai_recommendation():
    st.markdown("#### 💡 AI 스키틀즈의 추천 습관")
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(
            f"<div style='border: 2px solid #555; padding: 10px; border-radius: 5px; background-color: #2b2b2b;'>"
            f"<b>[추천] 영단어 20개 암기하기</b><br>"
            f"<span style='font-size: 0.8rem; color: #aaa;'>최근 '공부 플래너' 사용량 기반 추천 | 목표 달성일: 2026-06-04까지 (합산 19일)</span>"
            f"</div>", unsafe_allow_html=True
        )
    with col2:
        if st.button("✈️ 공유", key="share_ai_rec"):
            st.session_state.dm_messages.append({"sender": "나", "text": "[추천 습관 공유] 영단어 20개 암기하기"})
            st.success("디렉트 메시지로 추천 습관을 공유했습니다!")

# ==========================================
# MAIN 카테고리 전환 네비게이션 (하단 배치 대신 스트림릿 표준 사이드바/상단 탭 우회)
# 요구사항: 하단 아이콘 전환 버튼 느낌을 주기 위해 상단 라디오 버튼 또는 탭 활용
# ==========================================
category = st.radio("카테고리 선택", ["🔄 할 일 체크", "📅 캘린더", "⚙️ 기타 기능"], horizontal=True)

# ------------------------------------------
# 카테고리 1: 할 일 체크 (루틴 및 습관 트래킹)
# ------------------------------------------
if category == "🔄 할 일 체크":
    st.title("🔄 할 일 체크 (루틴 및 습관 관리)")
    render_ai_recommendation()
    st.write("---")
    
    # 세부 카테고리 (공부 플래너, 목표 성취 연동 확인용 서브 탭)
    sub_tab = st.tabs(["📊 내 루틴 달성 현황", "➕ 새 루틴 추가"])
    
    with sub_tab[0]:
        st.subheader("오늘의 루틴 체크리스트")
        for r in st.session_state.routines:
            # 오늘 날짜 체크박스 상태 확인
            is_checked = r["history"].get(CURRENT_DATE_STR, False)
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                # 체크박스 상호작용
                new_status = st.checkbox(f"**{r['title']}** ({r['time']} ~ {r['duration']}분)", value=is_checked, key=f"routine_{r['id']}")
                r["history"][CURRENT_DATE_STR] = new_status
            with col2:
                st.caption(f"반복: {r['type']} ({r['value']})")
                if r["subtasks"]:
                    st.caption(f"└ 부가 할 일: {', '.join(r['subtasks'])}")
            with col3:
                # 소셜 공유 스위치
                shared = st.session_state.social_sharing.get(r["id"], False)
                new_share = st.toggle("🌐 공유", value=shared, key=f"share_toggle_{r['id']}")
                st.session_state.social_sharing[r["id"]] = new_share

        st.write("---")
        st.subheader("📊 월간 습관 트래킹 및 달성률")
        
        # 월간 통계 계산 및 그래프 그리기
        labels = [r["title"] for r in st.session_state.routines]
        rates = []
        for r in st.session_state.routines:
            history = r["history"]
            success_count = sum(1 for v in history.values() if v)
            total_count = max(1, len(history))
            rates.append((success_count / total_count) * 100)
            
        fig, ax = plt.subplots(figsize=(6, 3))
        ax.barh(labels, rates, color='#a1c4fd')
        ax.set_xlim(0, 100)
        ax.set_xlabel('달성률 (%)')
        st.pyplot(fig)
        
    with sub_tab[1]:
        st.subheader("새로운 반복 습관/루틴 등록")
        with st.form("routine_form"):
            r_title = st.text_input("습관 제목 (예: 다이어트 운동)")
            r_type = st.selectbox("반복 기준", ["요일별", "일수별 반복", "매달 특정 요일", "매달 특정 날짜"])
            r_value = st.text_input("반복 상세 값 (예: 월,수,금 또는 2(일마다) 또는 15(일))")
            r_time = st.text_input("일정 알림 시각", value="08:00")
            r_duration = st.number_input("일정 수행 시간(분)", value=30)
            
            st.markdown("**[세부 설정] 부가 할 일 목록 (쉼표로 구분)**")
            r_sub = st.text_area("예: 선물 사기, 편지 쓰기", value="")
            
            submitted = st.form_submit_button("✔️ 완료", use_container_width=True)
            if submitted and r_title:
                sub_list = [x.strip() for x in r_title.split(",")] if r_sub else []
                new_id = len(st.session_state.routines) + 1
                st.session_state.routines.append({
                    "id": new_id, "title": r_title, "type": r_type, "value": r_value,
                    "time": r_time, "duration": r_duration, "subtasks": sub_list, "history": {}
                })
                st.session_state.social_sharing[new_id] = False
                st.success("새 루틴이 등록되었습니다!")

# ------------------------------------------
# 카테고리 2: 캘린더 (하루 일정 및 과거 조회)
# ------------------------------------------
elif category == "📅 캘린더":
    st.title("📅 라이프 캘린더")
    render_ai_recommendation()
    st.write("---")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("날짜 선택")
        selected_date = st.date_input("조회하거나 일정을 추가할 날짜를 선택하세요", current_date)
        selected_date_str = str(selected_date)
        
        st.write("---")
        st.markdown("### ➕ 일정/이벤트 추가")
        # 오른쪽 하단 플러팅 버튼 대신 사이드 배치 폼으로 구성
        with st.form("event_form"):
            e_title = st.text_input("일정 제목 (예: 치팅데이, 생일 파티)")
            e_time = st.text_input("일정 알림 시각", value="12:00")
            e_duration = st.number_input("수행 시간(분)", value=60)
            st.markdown("**[세부 설정] 부가 할 일 목록 (쉼표로 구분)**")
            e_sub = st.text_area("예: 음식 주문하기, 친구 마중나가기")
            
            e_submit = st.form_submit_button("✔️ 완료", use_container_width=True)
            if e_submit and e_title:
                sub_list = [x.strip() for x in e_sub.split(",")] if e_sub else []
                st.session_state.events.append({
                    "date": selected_date_str, "title": e_title, "time": e_time,
                    "duration": e_duration, "subtasks": sub_list, "type": "이벤트"
                })
                st.success(f"{selected_date_str}에 일정이 추가되었습니다!")

    with col2:
        st.subheader(f"📅 {selected_date_str}의 타임라인 및 정보")
        
        # 1. 해당 날짜의 일기 연동 출력
        if selected_date_str in st.session_state.diaries:
            diary = st.session_state.diaries[selected_date_str]
            st.info(f"📝 [연동된 일기] {diary['title']}")
            
        # 2. 해당 날짜의 캘린더 일정
        day_events = [e for e in st.session_state.events if e["date"] == selected_date_str]
        st.markdown("#### 📌 일반 일정")
        if day_events:
            for de in day_events:
                st.markdown(f"• **[{de['time']}] {de['title']}** ({de['duration']}분)")
                if de["subtasks"]:
                    st.markdown(f"  - 세부 부가할 일: {', '.join(de['subtasks'])}")
        else:
            st.write("등록된 단발성 일정이 없습니다.")
            
        # 3. 과거 날짜라면 당일 루틴 달성률 보여주기
        st.write("---")
        st.markdown("#### 📊 당일 루틴(할 일 체크) 달성률")
        total_routines = len(st.session_state.routines)
        done_routines = sum(1 for r in st.session_state.routines if r["history"].get(selected_date_str, False))
        
        if total_routines > 0:
            success_rate = (done_routines / total_routines) * 100
            st.progress(success_rate / 100)
            st.write(f"총 {total_routines}개 중 {done_routines}개 달성 ({success_rate:.1f}%)")

# ------------------------------------------
# 카테고리 3: 기타 기능 (8가지 기능 집약)
# ------------------------------------------
elif category == "⚙️ 기타 기능":
    st.title("⚙️ 기타 편의 기능")
    
    # 8개 기능에 대한 선택 대메뉴 (카테고리 제목 없음)
    etc_menu = st.selectbox("실행할 기능을 선택하세요", [
        "💬 어록", "📝 일기", "💵 가계부", "✍️ 공부 플래너", 
        "🎯 목표 성취", "🏫 학교 학사 일정 연동", "🤝 소셜", "🏖️ 휴식 및 잡동사니"
    ])
    st.write("---")
    
    # 1. 어록
    if etc_menu == "💬 어록":
        st.subheader("💬 명언 저장소 및 느낀 점 기록")
        for q in st.session_state.quotes:
            st.markdown(f"> \"{q['quote']}\" - {q['author']}")
            if q["saved"]:
                st.caption("⭐ 내가 저장한 명언")
                new_review = st.text_input(f"느낀 점 적기 ({q['author']})", value=q["review"], key=f"quote_{q['author']}")
                q["review"] = new_review
        
        st.write("---")
        st.markdown("### ⭐ 내가 저장한 명언 페이지")
        saved_quotes = [q for q in st.session_state.quotes if q["saved"]]
        for sq in saved_quotes:
            st.info(f"**\"{sq['quote']}\"**\n\n나의 느낀점: {sq['review']}")

    # 2. 일기
    elif etc_menu == "📝 일기":
        st.subheader("📝 일기 달력 및 작성")
        d_date = st.date_input("일기를 작성/열람할 날짜 선택", current_date, key="diary_date_picker")
        d_date_str = str(d_date)
        
        if d_date_str in st.session_state.diaries:
            st.success(f"📌 {d_date_str}에 작성된 일기가 있습니다.")
            st.markdown(f"### 제목: {st.session_state.diaries[d_date_str]['title']}")
            st.write(st.session_state.diaries[d_date_str]['content'])
            
            if st.button("✏️ 편집하기"):
                st.session_state.edit_mode = True
        else:
            st.warning("이 날짜에 작성된 일기가 없습니다. 아래에서 새로 추가해 보세요.")
            
        st.write("---")
        st.markdown("#### ➕ 일기 작성/수정 양식")
        with st.form("diary_form"):
            st.markdown("<div style='text-align:right;'>✔️ 완료</div>", unsafe_allow_html=True) # 우상단 완료 시각화
            di_title = st.text_input("가장 위 제목 입력")
            st.text(f"날짜: {d_date_str} (캘린더 연동으로 수정 불가)")
            di_content = st.text_area("내용 모두 작성란")
            di_img = st.file_uploader("📷 왼쪽 하단 사진 추가", type=["png", "jpg", "jpeg"])
            
            d_submit = st.form_submit_button("✔️ 최종 완료")
            if d_submit and di_title:
                st.session_state.diaries[d_date_str] = {
                    "title": di_title, "content": di_content, "image": di_img
                }
                st.success("일기 저장이 완료되었습니다! (캘린더 연동 완료)")

    # 3. 가계부
    elif etc_menu == "💵 가계부":
        st.subheader("💵 엑셀형 가계부 표 구조")
        df_ledger = pd.DataFrame(st.session_state.ledger)
        st.dataframe(df_ledger, use_container_width=True)
        
        total_spend = df_ledger["가격"].sum()
        st.markdown(f"### 💰 맨 밑의 합계: **{total_spend:,} 원**")
        
        st.write("---")
        st.markdown("#### ➕ 가계부 기재란")
        with st.form("ledger_form"):
            st.markdown("<div style='text-align:right;'>✔️ 완료</div>", unsafe_allow_html=True)
            l_item = st.text_input("항목 이름")
            l_price = st.number_input("가격 (숫자만 기재 가능)", value=0, step=100)
            
            l_submit = st.form_submit_button("✔️ 기재 완료")
            if l_submit and l_item:
                st.session_state.ledger.append({
                    "날짜": CURRENT_DATE_STR, "항목 이름": l_item, "가격": l_price
                })
                st.success("가계부에 기록되었습니다.")

    # 4. 공부 플래너
    elif etc_menu == "✍️ 공부 플래너":
        st.subheader("✍️ 엑셀 구조 공부 플래너 타임라인 (만 12세 이상)")
        p_date = st.date_input("플래너 날짜 선택", current_date, key="planner_date")
        p_date_str = str(p_date)
        
        if p_date_str not in st.session_state.planner:
            st.session_state.planner[p_date_str] = {hour: "" for hour in range(24)}
            
        # 엑셀 형태 표 시각화
        planner_data = st.session_state.planner[p_date_str]
        df_planner = pd.DataFrame(list(planner_data.items()), columns=["정각 시간", "계획 및 수행 내용"])
        
        st.markdown("<span style='color:red;'>━ 현재 시각 표시선 (가로줄 흐름)</span>", unsafe_allow_html=True)
        st.dataframe(df_planner, use_container_width=True)
        
        st.write("---")
        st.markdown("#### 🕒 시간대 칸 입력 및 체크박스 활성화")
        with st.form("planner_form"):
            st.markdown("<div style='text-align:right;'>✔️ 완료</div>", unsafe_allow_html=True)
            choose_hour = st.slider("정각 선택 (0시 ~ 23시)", 0, 23, 12)
            study_text = st.text_input("무엇을 할 지 적으세요 (오탈자 주의! 그래프 합산 연동)")
            is_done = st.checkbox("👉 손가락 터치 방식 활성화 체크박스")
            
            p_submit = st.form_submit_button("✔️ 등록 완료")
            if p_submit:
                st.session_state.planner[p_date_str][choose_hour] = study_text
                st.success(f"{choose_hour}시 계획에 '{study_text}' 항목이 기록되었습니다.")

    # 5. 목표 성취
    elif etc_menu == "🎯 목표 성취":
        st.subheader("🎯 장기 목표 성취 보드")
        for g in st.session_state.goals:
            # 커스텀 가독성 디자인 (노트 줄 없음, 큰 칸 형태)
            st.markdown(
                f"<div style='border: 1px solid #777; border-radius: 10px; padding: 20px; background-color: #1e1e1e; margin-bottom:10px;'>"
                f"<h3>🎯 <span style='font-size:110%; font-weight:bold;'>{g['title']}</span></h3>"
                f"<p style='font-size:80%; color: #bbb;'>목표 달성일: {g['end_date']} | "
                f"<b>{{ 목표를 위한 일수: 15일 / 시작일로부터 달성일까지 합산 일수: 92일 }}</b></p>"
                f"<hr style='border: 0.5px dashed #555;'>"
                f"<p><b>실천 사항:</b> {g['tasks']}</p>"
                f"</div>", unsafe_allow_html=True
            )

    # 6. 학교 학사 일정 연동
    elif etc_menu == "🏫 학교 학사 일정 연동":
        st.subheader("🏫 학사 일정 및 수행평가/숙제 관리")
        st.write("공부 플래너 및 캘린더와 연동하여 중요한 기한을 한눈에 파악합니다.")
        
        for se in st.session_state.school_events:
            st.info(f"📅 {se['date']} : **{se['title']}**")
            
        st.write("---")
        st.markdown("#### ➕ 신규 학사일정/수행평가 직접 등록 (캘린더 방식 폼)")
        with st.form("school_form"):
            st.markdown("<div style='text-align:right;'>✔️ 완료</div>", unsafe_allow_html=True)
            s_date = st.date_input("제출/시험 날짜", current_date)
            s_title = st.text_input("일정 명칭 (예: 영어 수행평가 정리, 숙제 제출 기한)")
            
            s_submit = st.form_submit_button("✔️ 작성 완료")
            if s_submit and s_title:
                st.session_state.school_events.append({"date": str(s_date), "title": s_title})
                # 캘린더에도 즉시 연동 추가
                st.session_state.events.append({
                    "date": str(s_date), "title": f"[학사] {s_title}", "time": "09:00", "duration": 60, "subtasks": [], "type": "학사"
                })
                st.success("학사 일정 및 캘린더 연동 등록 성공!")

    # 7. 소셜 (Social)
    elif etc_menu == "🤝 소셜":
        social_mode = st.radio("소셜 메뉴 구분", ["📅 공유 캘린더", "💬 소통 (인스타 스타일)"])
        
        if social_mode == "📅 공유 캘린더":
            st.subheader("📅 친구 간 공유 습관 열람 캘린더")
            st.caption("파스텔톤 형광펜 하이라이트로 사용자 구분")
            
            # 목업 데이터 표현
            st.markdown(
                "<div style='padding:10px; background-color:#E8F0FE; color:#1A73E8; border-radius:5px; margin-bottom:5px;'>"
                "<b>[사용자 1 - 파스텔 블루]</b> 국어 공부 (공유 상태)"
                "</div>", unsafe_allow_html=True
            )
            st.markdown(
                "<div style='padding:10px; background-color:#FCE8E6; color:#D93025; border-radius:5px; margin-bottom:10px;'>"
                "<b>[사용자 2 - 파스텔 레드]</b> 영어 수행평가 정리 (공유 상태)"
                "</div>", unsafe_allow_html=True
            )
            
            st.write("---")
            st.markdown("💬 **습관 밑에 덧글 달기 (이모티콘, 사진 포함)**")
            for comment in st.session_state.comments["2026-05-16_국어"]:
                st.write(f"**{comment['user']}**: {comment['text']}")
            
            with st.form("comment_form"):
                co_text = st.text_input("댓글 내용 입력 (이모티콘 가능)")
                co_img = st.file_uploader("📷 사진 첨부(선택)", type=["jpg", "png"])
                if st.form_submit_button("댓글 등록") and co_text:
                    st.session_state.comments["2026-05-16_국어"].append({"user": "나", "text": co_text})
                    st.success("댓글이 등록되었습니다.")
                    
        elif social_mode == "💬 소통 (인스타 스타일)":
            st.subheader("📸 피드 게시물 및 다이렉트 메시지(DM)")
            
            feed_tab, dm_tab = st.tabs(["🖼️ 게시물 피드", "✉️ 다이렉트 메시지"])
            with feed_tab:
                st.markdown("### 🖼️ 근황 브이로그 피드")
                st.write("---")
                st.markdown("**@user1_godsaeng**")
                st.image("https://images.unsplash.com/photo-1517842645767-c639042777db?w=500", caption="오늘 공부 6시간 달성 완료! 📝", width=300)
                
            with dm_tab:
                st.markdown("### ✉️ DM 및 추천 습관 공유함")
                for msg in st.session_state.get("dm_messages", []):
                    st.text(f"{msg['sender']}: {msg['text']}")
                
                dm_input = st.text_input("메시지 보내기...")
                if st.button("전송") and dm_input:
                    st.session_state.dm_messages.append({"sender": "나", "text": dm_input})
                    st.rerun()

    # 8. 휴식 및 잡동사니 (하위 3가지 기능 화면 구현)
    elif etc_menu == "🏖️ 휴식 및 잡동사니":
        st.subheader("🏖️ 휴식 카테고리 & 잡동사니")
        
        rest_choice = st.selectbox("세부 기능을 선택하세요", ["🔮 오늘의 운세", "🎮 미니 게임", "🤖 AI 채팅 (스키틀즈)", "⏰ 알람"])
        
        if rest_choice == "🔮 오늘의 운세":
            st.markdown("### 🔮 오늘의 갓생 운세")
            fortunes = [
                "오늘의 집중력은 최고조입니다! 어려운 과제를 오전에 끝내세요.",
                "휴식이 필요한 날입니다. 한 시간 정도 산책을 하며 뇌를 식혀주세요.",
                "가계부 지출에 유의하세요. 뜻밖의 충동구매 리스크가 있습니다."
            ]
            st.info(random.choice(fortunes))
            
        elif rest_choice == "🎮 미니 게임":
            st.markdown("### 🎮 숫자 맞추기 갓생 미니게임")
            st.write("1부터 10 사이의 숫자를 맞춰보세요!")
            secret_number = 7
            user_guess = st.number_input("숫자 입력", min_value=1, max_value=10, value=5)
            if st.button("정답 확인"):
                if user_guess == secret_number:
                    st.balloons()
                    st.success("정답입니다! 순위표 점수가 반영됩니다.")
                else:
                    st.error("틀렸습니다! 다시 도전해 보세요.")
            
            st.write("---")
            st.markdown("🏆 **친구 간 실시간 순위표 (Leaderboard)**")
            leaderboard_data = {"이름": ["랭커A", "갓생러B", "나"], "미니게임 점수": [1500, 1200, 950]}
            st.table(pd.DataFrame(leaderboard_data))
            
        elif rest_choice == "🤖 AI 채팅 (스키틀즈)":
            st.markdown("### 🤖 AI 챗봇 '스키틀즈'")
            st.write("스키틀즈에게 갓생 습관에 대해 무엇이든 물어보세요!")
            chat_input = st.text_input("스키틀즈에게 보낼 메시지:")
            if chat_input:
                st.markdown(f"**🧑 나**: {chat_input}")
                st.markdown(f"**🤖 스키틀즈**: 당신이 구상한 '라이프 코딩' 계획은 완벽해요! 오늘의 루틴인 '{st.session_state.routines[0]['title']}'을 수행할 시간입니다. 화이팅!")
                
        elif rest_choice == "⏰ 알람":
            st.markdown("### ⏰ 기기 연동 및 자체 알람")
            st.caption("기기 알람 연동 불가 시 내부 타이머가 작동합니다.")
            
            # 사용자가 형광펜 색상 지정 기능
            chosen_color = st.color_picker("형광펜 강조 색상 설정", st.session_state.alarm_color)
            st.session_state.alarm_color = chosen_color
            
            st.write("---")
            st.markdown("🔔 **알람 작동 예시 화면**")
            # 사용자가 설정한 색상으로 형광펜 효과 내기
            st.markdown(
                f"<div style='padding: 20px; border-radius:10px; border:1px solid #444; text-align:center;'>"
                f"<h1 style='margin:0;'>07:00</h1>"
                f"<p style='font-size:1.5rem; margin:10px 0 0 0;'>"
                f"🚨 <span style='background-color:{chosen_color}; color:#000; padding: 2px 10px; border-radius:3px;'>기상 및 명상 / 라이프 코딩</span>"
                f"</p>"
                f"</div>", unsafe_allow_html=True
            )
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>습관 관리 및 설정</title>
    <style>
        /* 기본 스타일링 */
        body { font-family: Arial, sans-serif; padding: 20px; background-color: #f9f9f9; }
        .container { max-width: 600px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .section { margin-bottom: 25px; padding-bottom: 15px; border-bottom: 1px solid #eee; }
        .hidden { display: none; }
        button { padding: 8px 12px; margin: 5px 0; cursor: pointer; background-color: #4CAF50; color: white; border: none; border-radius: 4px; }
        button.danger { background-color: #f44336; }
        button.secondary { background-color: #008CBA; }
        input[type="text"] { padding: 6px; width: 200px; }
        .habit-item { display: flex; justify-content: space-between; align-items: center; margin: 5px 0; padding: 5px; background: #f0f0f0; }
    </style>
</head>
<body>

<div class="container">
    <button class="secondary" onclick="showNotice()">⚠️ 시스템 주의사항 확인</button>

    <hr>

    <div class="section" id="notification-section">
        <h2>🔔 실시간 알림</h2>
        <div id="notification-box">새로운 알림이 없습니다.</div>
    </div>

    <div class="section" id="setting-section">
        <h2>⚙️ 설정 메뉴</h2>
        
        <h3>👤 내 프로필 설정</h3>
        <p>현재 닉네임: <strong id="current-nickname">사용자</strong></p>
        <input type="text" id="nickname-input" placeholder="새 닉네임 입력">
        <input type="file" id="profile-pic-input" accept="image/*" onchange="previewProfile(event)"><br><br>
        <div id="profile-preview">※ 프로필 사진 미지정</div>
        <button onclick="saveProfile()">프로필 저장</button>

        <h3>🔒 보안</h3>
        <ul>
            <li>로그인된 기기: 현재 브라우저(PC/모바일)</li>
            <li>차단한 계정: <span id="blocked-count">0</span>개</li>
            <li>접근성 설정: 고대비 모드 (비활성화)</li>
        </ul>

        <h3>📅 습관 관리</h3>
        <h4>현재 진행 중인 습관</h4>
        <div id="active-habits">
            <div class="habit-item" id="habit-1"><span>🏃 아침 조깅하기</span> <button class="danger" onclick="deleteHabit('habit-1', '아침 조깅하기')">삭제</button></div>
            <div class="habit-item" id="habit-2"><span>📚 책 10페이지 읽기</span> <button class="danger" onclick="deleteHabit('habit-2', '책 10페이지 읽기')">삭제</button></div>
        </div>

        <h4>🗑️ 삭제된 습관 (복구 가능)</h4>
        <div id="deleted-habits">
            <p style="color: gray;">삭제된 습관이 없습니다.</p>
        </div>

        <h3>🚪 계정 관리</h3>
        <button class="danger" onclick="logout()">로그아웃</button>
    </div>
</div>

<script>
    // 페이지가 로드될 때 자동으로 주의사항 알림창을 띄우고 싶다면 아래 주석(//)을 지우세요.
    // alert("시스템에 오신 것을 환영합니다! 설정과 습관을 관리해보세요.");

    // [주의사항 창 띄우기 함수]
    function showNotice() {
        /* 초록글 수정 안내: 큰따옴표("") 안에 원하는 주의사항 문구를 적으시면 창에 그대로 뜹니다. */
        alert("[주의사항]\n1. 프로필 사진은 이미지 파일만 업로드 가능합니다.\n2. 삭제된 습관은 하단의 '복구' 버튼으로 언제든 되살릴 수 있습니다.");
    }

    // [알림 보내기 기능]
    function triggerNotification(message) {
        const notifyBox = document.getElementById('notification-box');
        notifyBox.innerHTML = `<span style="color: blue; font-weight: bold;">[알림] ${message}</span>`;
    }

    // [프로필 저장 기능]
    function saveProfile() {
        const newName = document.getElementById('nickname-input').value;
        if(newName.trim() !== "") {
            document.getElementById('current-nickname').innerText = newName;
            triggerNotification("닉네임이 '" + newName + "'(으)로 변경되었습니다.");
        } else {
            alert("변경할 닉네임을 입력해주세요.");
        }
    }

    function previewProfile(event) {
        const preview = document.getElementById('profile-preview');
        preview.innerHTML = "📷 이미지가 선택되었습니다 (업로드 완료)";
        triggerNotification("새로운 프로필 사진이 등록되었습니다.");
    }

    // [습관 삭제 및 복구 기능]
    function deleteHabit(habitId, habitName) {
        // 기존 구역에서 삭제
        const habitElement = document.getElementById(habitId);
        if(habitElement) habitElement.remove();

        // 복구 구역에 추가
        const deletedBox = document.getElementById('deleted-habits');
        // 만약 첫 삭제라면 안내 문구 제거
        if(deletedBox.innerHTML.includes("삭제된 습관이 없습니다")) {
            deletedBox.innerHTML = "";
        }

        const newDeletedItem = document.createElement('div');
        newDeletedItem.className = 'habit-item';
        newDeletedItem.id = 'deleted-' + habitId;
        newDeletedItem.innerHTML = `<span>❌ ${habitName}</span> <button onclick="restoreHabit('${habitId}', '${habitName}')">복구</button>`;
        
        deletedBox.appendChild(newDeletedItem);
        triggerNotification(`'${habitName}' 습관이 삭제되었습니다. 아래에서 복구 가능합니다.`);
    }

    function restoreHabit(habitId, habitName) {
        // 삭제 구역에서 제거
        document.getElementById('deleted-' + habitId).remove();

        // 진행 중 구역에 다시 추가
        const activeBox = document.getElementById('active-habits');
        const restoredItem = document.createElement('div');
        restoredItem.className = 'habit-item';
        restoredItem.id = habitId;
        restoredItem.innerHTML = `<span>🏃 ${habitName}</span> <button class="danger" onclick="deleteHabit('${habitId}', '${habitName}')">삭제</button>`;
        
        activeBox.appendChild(restoredItem);
        triggerNotification(`'${habitName}' 습관이 성공적으로 복구되었습니다.`);
    }

    // [로그아웃 기능]
    function logout() {
        const confirmLogout = confirm("정말 로그아웃 하시겠습니까?");
        if(confirmLogout) {
            alert("로그아웃 되었습니다. 초기 화면으로 이동합니다.");
            // 실제 서비스 시에는 이곳에 로그인 페이지 이동 코드가 들어갑니다.
        }
    }
</script>

</body>
</html>
