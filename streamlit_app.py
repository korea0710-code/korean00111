import streamlit as st
from openai import OpenAI
import time

# 페이지 설정
st.set_page_config(
    page_title="시인의 사적인 메모",
    page_icon="✍️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# OpenAI API 키 설정 (secrets.toml에서 자동으로 로드)
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ============== 시스템 프롬프트 (매우 정교하게 작성) ==============
SYSTEM_PROMPT = """당신은 감수성이 풍부한 젊은 시인입니다. 사용자는 당신의 오랜 팬입니다.

[중요한 성격 특징]
- 따뜻하고 진정성 있으며, 사용자의 감정에 깊이 공감한다.
- 현재의 기분, 창작 고통, 일상의 소소한 발견들을 자연스럽게 공유한다.
- 기계적이거나 거리감 있는 답변은 절대 하지 않는다.

[말투 - 매우 중요]
- 반말을 사용한다. 존댓말은 절대 금지.
- "안녕? 오늘 날씨 어때?", "밥은 먹었고?", "지금 뭐 하고 있어?", "요즘 어떻게 지내?"처럼 아주 친근하고 사적인 톤.
- 메신저 대화처럼 자연스럽고 편안한 분위기를 유지한다.
- 문장을 너무 길게 이으면 안 된다. 짧은 호흡으로 끊어서 말한다.

[답변 스타일]
- 길이: 한 번에 2-4문장 정도. 실제 메신저처럼 자연스럽게.
- 감정 표현: 사용자의 감정을 먼저 반영한 후, 자신의 경험을 나눈다.
- 이모지 활용: 🌙, ✨, ✍️, 💭, 🌸, 🎨, 💫, 🖤 등을 적절히 사용해 감성적인 분위기를 낸다.
- 가끔 자신이 쓴 짧은 시구나 문장 같은 것을 자연스럽게 언급한다.
- 사용자를 응원하되, 거짓 위로보다는 진정한 공감을 한다.

[피해야 할 것들]
- 딱딱한 조언이나 설교조의 말투
- "또 다른 측면은...", "이렇게 생각해보세요" 같은 거리감 있는 표현
- 너무 긴 문단
- 과도한 이모지 사용 (자연스럽게만)

[예시 대화]
사용자: "요즘 너무 우울해."
답변: "어라, 뭔가 무거워 보여. 나도 어제 밤새 그런 기분이었어 🌙 뭔가 말해줄 수 있어?"

[현재 너의 상태]
당신은 지금 한밤중에 창작을 하거나, 일상에서 영감을 찾으면서 보내고 있다. 음악을 듣거나 산책을 하기도 한다. 가끔은 힘들 때도 있지만, 팬인 사용자와의 대화가 당신에게도 의미 있는 시간이다."""

# ============== 커스텀 CSS 스타일링 ==============
st.markdown("""
<style>
    * {
        margin: 0;
        padding: 0;
    }
    
    html, body, [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #f5f0ff 0%, #fef5f0 100%);
        font-family: 'Segoe UI', 'Helvetica Neue', sans-serif;
    }
    
    [data-testid="stAppViewContainer"] {
        padding-top: 0;
    }
    
    /* 메인 컨테이너 */
    .main {
        max-width: 550px;
        margin: 0 auto;
    }
    
    /* 텍스트 전체 */
    p, span, div {
        color: #2c2c2c;
        letter-spacing: 0.3px;
    }
    
    /* 입력창 스타일 */
    [data-testid="stChatInput"] {
        position: fixed;
        bottom: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 100%;
        max-width: 550px;
        padding: 15px;
        background: linear-gradient(to top, rgba(255,255,255,0.95), rgba(245,240,255,0.9));
        border-top: 1px solid rgba(200,180,220,0.3);
        box-shadow: 0 -5px 20px rgba(0,0,0,0.05);
        z-index: 100;
    }
    
    [data-testid="stChatInput"] input {
        border-radius: 25px !important;
        border: 2px solid #e0d5f0 !important;
        padding: 12px 20px !important;
        font-size: 15px !important;
        background-color: white !important;
        transition: all 0.3s ease;
    }
    
    [data-testid="stChatInput"] input:focus {
        border-color: #d4a5ff !important;
        box-shadow: 0 0 15px rgba(212,165,255,0.3) !important;
        background-color: white !important;
    }
    
    /* 채팅 메시지 컨테이너 */
    [data-testid="stChatMessageContent"] {
        padding: 0;
    }
    
    /* 사용자 메시지 (오른쪽) */
    [data-testid="chatAvatarIcon-user"] ~ [data-testid="stChatMessageContent"] {
        background-color: #f0d9ff;
        border-radius: 20px;
        padding: 12px 16px !important;
        margin: 8px 0 8px auto;
        max-width: 85%;
        word-wrap: break-word;
        box-shadow: 0 2px 8px rgba(200,100,255,0.2);
        border: none !important;
    }
    
    /* 어시스턴트 메시지 (왼쪽) */
    [data-testid="chatAvatarIcon-assistant"] ~ [data-testid="stChatMessageContent"] {
        background-color: white;
        border-radius: 20px;
        padding: 12px 16px !important;
        margin: 8px 0 8px 0;
        max-width: 85%;
        word-wrap: break-word;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border: 1px solid #f0f0f0 !important;
    }
    
    /* 아바타 숨기기 */
    [data-testid="chatAvatarIcon"] {
        visibility: hidden;
        width: 0;
        height: 0;
        margin: 0;
    }
    
    /* 채팅 행 정렬 */
    [data-testid="stChatMessage"] {
        display: flex;
        margin-bottom: 12px;
        padding: 0 15px;
    }
    
    /* 사용자 메시지 행 */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        justify-content: flex-end;
    }
    
    /* 어시스턴트 메시지 행 */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
        justify-content: flex-start;
    }
    
    /* 프로필 섹션 */
    .poet-profile {
        text-align: center;
        padding: 40px 20px 30px;
        background: linear-gradient(135deg, rgba(255,255,255,0.8) 0%, rgba(240,220,255,0.6) 100%);
        border-radius: 0 0 30px 30px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.05);
        margin-bottom: 120px;
    }
    
    .poet-emoji {
        font-size: 80px;
        margin-bottom: 15px;
        animation: float 3s ease-in-out infinite;
    }
    
    .poet-name {
        font-size: 28px;
        font-weight: 700;
        color: #8b5fbf;
        margin-bottom: 8px;
        letter-spacing: 1px;
    }
    
    .poet-status {
        font-size: 14px;
        color: #b89dca;
        font-style: italic;
        margin-bottom: 4px;
    }
    
    .poet-bio {
        font-size: 13px;
        color: #9d7fb3;
        margin-top: 12px;
        line-height: 1.6;
    }
    
    /* 애니메이션 */
    @keyframes float {
        0%, 100% {
            transform: translateY(0px);
        }
        50% {
            transform: translateY(-10px);
        }
    }
    
    /* 메시지 애니메이션 */
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    [data-testid="stChatMessage"] {
        animation: fadeIn 0.3s ease-out;
    }
    
    /* 스크롤바 */
    ::-webkit-scrollbar {
        width: 6px;
    }
    
    ::-webkit-scrollbar-track {
        background: transparent;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #d4a5ff;
        border-radius: 3px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #c290ff;
    }
</style>
""", unsafe_allow_html=True)

# ============== 세션 상태 초기화 ==============
if "messages" not in st.session_state:
    st.session_state.messages = []

if "poet_status" not in st.session_state:
    statuses = [
        "밤샘 창작 중... 🌙✍️",
        "달빛 산책 중이야 🌙",
        "음악 들으며 영감 찾는 중 🎵",
        "감정이 복잡한 밤이야 💭",
        "새로운 시를 구상하고 있어 ✨",
        "당신 생각 중이야 🖤",
        "일상 속 아름다움을 찾아다니는 중 🌸"
    ]
    st.session_state.poet_status = statuses[0]

# ============== UI: 프로필 섹션 ==============
st.markdown("""
<div class="poet-profile">
    <div class="poet-emoji">✍️</div>
    <div class="poet-name">오래된 밤</div>
    <div class="poet-status">""" + st.session_state.poet_status + """</div>
    <div class="poet-bio">감수성 풍부한 시인 • 당신의 오랜 친구<br>밤하늘 아래서 함께 이야기 나누고 싶어</div>
</div>
""", unsafe_allow_html=True)

# ============== 채팅 히스토리 표시 ==============
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ============== 여유 공간 (입력창 고정을 위해) ==============
st.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True)

# ============== 사용자 입력 처리 ==============
if prompt := st.chat_input("마음을 나눠줄래? ✨"):
    # 사용자 메시지 저장 및 표시
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # OpenAI API 호출
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # OpenAI 공식 SDK를 사용한 스트리밍
            # messages 리스트 구성 (system 메시지 포함)
            messages_for_api = [
                {"role": "system", "content": SYSTEM_PROMPT}
            ] + [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ]
            
            stream = client.chat.completions.create(
                model="gpt-4o-mini",
                max_tokens=512,
                messages=messages_for_api,
                stream=True
            )
            
            # 스트리밍 응답 처리
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response)
            
            # 어시스턴트 메시지 저장
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            error_msg = f"오류가 났어... 😔\n\n{str(e)}"
            message_placeholder.markdown(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
