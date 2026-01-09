# UI Text Dictionary (i18n)
UI_TEXTS = {
    "en": {
        "page_title": "LawGPT - Agentic Legal Assistant",
        "sidebar_title": "⚙️ Settings",
        "lang_select": "Interface & Response Language",
        "new_chat": "➕ New Chat",
        "history": "Chat History",
        "select_chat": "Select Chat",
        "delete_chat": "🗑️ Delete Current Chat",
        "show_graph": "Show Reasoning Graph",
        "multimodal_title": "### Multimodal Capabilities",
        "multimodal_desc": "You can upload images of legal documents for analysis.",
        "main_title": "⚖️ LawGPT: German Law Assistant",
        "main_caption": "Ask anything about German Statutory Law (BGB). Input can be in any language.",
        "input_placeholder": "Ask a legal question...",
        "upload_label": "Upload an image (optional)",
        "source_preview": "📚 Source Preview (Legal Text)",
        "graph_expander": "Show Reasoning Graph",
        "analyzing": "Analyzing legal context...",
        "error_prefix": "Error: ",
        "disclaimer": "Disclaimer: This AI assistant provides information for educational purposes only and does not constitute legal advice."
    },
    "de": {
        "page_title": "LawGPT - Agentischer Rechtsassistent",
        "sidebar_title": "⚙️ Einstellungen",
        "lang_select": "Sprache (Interface & Antwort)",
        "new_chat": "➕ Neuer Chat",
        "history": "Chat-Verlauf",
        "select_chat": "Chat auswählen",
        "delete_chat": "🗑️ Aktuellen Chat löschen",
        "show_graph": "Entscheidungsgraph anzeigen",
        "multimodal_title": "### Multimodale Fähigkeiten",
        "multimodal_desc": "Sie können Bilder von Rechtsdokumenten zur Analyse hochladen.",
        "main_title": "⚖️ LawGPT: Dein BGB-Assistent",
        "main_caption": "Fragen Sie alles zum deutschen Recht. Eingabe in jeder Sprache möglich.",
        "input_placeholder": "Stellen Sie eine Rechtsfrage...",
        "upload_label": "Bild hochladen (optional)",
        "source_preview": "📚 Quellenvorschau (Gesetzestext)",
        "graph_expander": "Entscheidungsgraph anzeigen",
        "analyzing": "Analysiere rechtlichen Kontext...",
        "error_prefix": "Fehler: ",
        "disclaimer": "Haftungsausschluss: Dieser KI-Assistent dient nur zu Informationszwecken und stellt keine Rechtsberatung dar."
    },
    "zh-tw": {
        "page_title": "LawGPT - 德國法律智能助手",
        "sidebar_title": "⚙️ 設定",
        "lang_select": "介面與回覆語言",
        "new_chat": "➕ 新增對話",
        "history": "對話紀錄",
        "select_chat": "選擇對話",
        "delete_chat": "🗑️ 刪除當前對話",
        "show_graph": "顯示 AI 思考路徑",
        "multimodal_title": "### 多模態功能",
        "multimodal_desc": "您可以上傳契約或法律文件的圖片進行分析。",
        "main_title": "⚖️ LawGPT: 德國法律智能助手",
        "main_caption": "詢問任何關於德國法典 (BGB) 的問題。支援任意語言輸入。",
        "input_placeholder": "請輸入法律問題...",
        "upload_label": "上傳圖片 (選用)",
        "source_preview": "📚 法條原文預覽",
        "graph_expander": "顯示 AI 思考路徑圖",
        "analyzing": "正在分析法律脈絡...",
        "error_prefix": "錯誤：",
        "disclaimer": "免責聲明：本 AI 助手僅供參考，不構成法律建議。如有具體法律問題，請諮詢合格律師。"
    }
}

# Page Config
st.set_page_config(page_title="LawGPT", page_icon="⚖️", layout="wide")

def init_session():
# ... (init_session, create_new_chat, delete_chat implementations remain same) ...

def main():
    settings = Settings()
    init_session()

    # --- Sidebar Configuration ---
    with st.sidebar:
        st.title("⚖️ LawGPT")
        
        # 0. Language Selector (First, because it affects UI text)
        # Check if language is already set in session, otherwise default
        if "user_language" not in st.session_state:
            st.session_state.user_language = "zh-tw"
            
        user_language = st.selectbox(
            "Language / Sprache / 語言", 
            ["zh-tw", "en", "de"],
            index=["zh-tw", "en", "de"].index(st.session_state.user_language),
            key="user_language_select"
        )
        # Update session state immediately
        st.session_state.user_language = user_language
        
        # Get UI Text based on selection
        T = UI_TEXTS[user_language]

        # 1. New Chat Button
        if st.button(T["new_chat"], use_container_width=True):
            create_new_chat()
            st.rerun() 

        st.divider()

        # 2. History
        st.markdown(f"**{T['history']}**")
        
        session_ids = list(st.session_state.sessions.keys())
        session_titles = [st.session_state.sessions[sid]["title"] for sid in session_ids]
        
        current_index = 0
        try:
            current_index = session_ids.index(st.session_state.current_session_id)
        except ValueError:
            current_index = 0
            st.session_state.current_session_id = session_ids[0]

        selected_title = st.radio(
            T["select_chat"], 
            session_titles, 
            index=current_index, 
            label_visibility="collapsed"
        )
        
        selected_index = session_titles.index(selected_title)
        st.session_state.current_session_id = session_ids[selected_index]

        st.divider()
        
        # 3. Settings UI
        st.title(T["sidebar_title"])
        show_graph = st.toggle(T["show_graph"], value=False)
        
        st.divider()
        st.markdown(T["multimodal_title"])
        st.write(T["multimodal_desc"])
        
        st.markdown("---")
        if st.button(T["delete_chat"]):
            delete_chat(st.session_state.current_session_id)
            st.rerun()

    # --- Main Interface ---
    st.title(T["main_title"])
    st.caption(T["main_caption"])
    
    current_session = st.session_state.sessions[st.session_state.current_session_id]
    messages = current_session["messages"]

    if current_session["title"] != "New Chat":
        st.caption(f"Current: {current_session['title']}")

    # Initialize components (Cached)
    if "retriever" not in st.session_state:
        st.session_state.retriever = Retriever()
    if "llm" not in st.session_state:
        st.session_state.llm = GeminiLLMAPI(
            api_key=settings.GOOGLE_API_KEY,
            model="gemini-flash-latest",
            system_instruction=(
                "You are an expert German legal advisor. "
                "Your primary knowledge source is the German Civil Code (BGB). "
                "Regardless of the input language, you MUST respond in the language specified by the user in the prompt."
            )
        )

    # Display Chat History
    for msg in messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "image" in msg:
                st.image(msg["image"], caption="Uploaded Image", use_column_width=True)

    # Input Area
    prompt = st.chat_input(T["input_placeholder"])
    uploaded_file = st.file_uploader(T["upload_label"], type=["png", "jpg", "jpeg"], label_visibility="collapsed")

    if prompt:
        # 1. Update Title
        if current_session["title"] == "New Chat":
            new_title = prompt[:20] + "..." if len(prompt) > 20 else prompt
            current_session["title"] = new_title
            save_sessions(st.session_state.sessions)

        # 2. Handle User Input
        user_image = None
        if uploaded_file:
            user_image = Image.open(uploaded_file)
            messages.append({"role": "user", "content": prompt, "image": user_image})
            save_sessions(st.session_state.sessions)
            with st.chat_message("user"):
                st.markdown(prompt)
                st.image(user_image, caption="Uploaded Image", use_column_width=True)
        else:
            messages.append({"role": "user", "content": prompt})
            save_sessions(st.session_state.sessions)
            with st.chat_message("user"):
                st.markdown(prompt)

        # 3. Run Agent
        with st.chat_message("assistant"):
            with st.spinner(T["analyzing"]):
                try:
                    # History Conversion
                    history_messages = []
                    for msg in messages:
                        if msg["role"] == "user":
                            history_messages.append(HumanMessage(content=msg["content"]))
                        elif msg["role"] == "assistant":
                            history_messages.append(AIMessage(content=msg["content"]))
                    
                    # Prepare Input
                    enhanced_prompt = f"STRICT INSTRUCTION: Respond only in {user_language}.\n\n{prompt}"
                    input_messages = history_messages[:-1] 
                    input_messages.append(HumanMessage(content=enhanced_prompt))
                    
                    initial_state = {
                        "messages": input_messages,
                        "documents": [] 
                    }
                    
                    # Invoke Graph
                    final_state = app.invoke(initial_state)
                    
                    # Extract Response
                    new_messages = final_state['messages'][len(input_messages):] 
                    response_text = "..."
                    for m in reversed(new_messages):
                        if isinstance(m, AIMessage):
                            response_text = m.content
                            break
                    
                    st.markdown(response_text)
                    
                    # Source Preview
                    unique_sources = {}
                    for msg in new_messages:
                        if isinstance(msg, ToolMessage):
                            try:
                                docs = json.loads(msg.content)
                                if isinstance(docs, list):
                                    for doc in docs:
                                        meta = doc.get('metadata', {})
                                        link = meta.get('link', 'Unknown')
                                        if link not in unique_sources:
                                            unique_sources[link] = meta
                            except:
                                pass
                    
                    if unique_sources:
                        with st.expander(T["source_preview"]):
                            for link, meta in unique_sources.items():
                                title = meta.get('section_title', 'Legal Document')
                                content = meta.get('content', 'No content available.')
                                st.markdown(f"**{title}**")
                                st.caption(f"Source: {link}")
                                st.text(content)
                                st.divider()

                    # Disclaimer (From UI Text)
                    st.warning(T["disclaimer"], icon="⚠️")
                    
                    # Graph Visualization
                    if show_graph:
                        with st.expander(T["graph_expander"]):
                            try:
                                graph_image = app.get_graph().draw_mermaid_png()
                                st.image(graph_image, caption="Agent Execution Path")
                            except:
                                st.info("Graph visualization unavailable.")

                    # Save
                    messages.append({"role": "assistant", "content": response_text})
                    save_sessions(st.session_state.sessions)
                    
                except Exception as e:
                    error_msg = f"{T['error_prefix']}{str(e)}"
                    st.error(error_msg)