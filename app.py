  # --- אזור Fathom המעודכן ---
        with st.container(border=True):
            col_title, col_refresh = st.columns([0.9, 0.1])
            with col_title:
                st.markdown("### ✨ סיכומי פגישות Fathom")

            with col_refresh:
                if st.button("🔄", key="refresh_fathom"):
                    try:
                        items, status = get_fathom_meetings()
                        if status == 200:
                            st.session_state['fathom_meetings'] = items
                            st.rerun()
                    except: pass

            if 'fathom_meetings' not in st.session_state:
                try:
                    items, status = get_fathom_meetings()
                    if status == 200:
                        st.session_state['fathom_meetings'] = items
                    else:
                        st.session_state['fathom_meetings'] = []
                except:
                    st.session_state['fathom_meetings'] = []

            st.markdown("""
                <style>
                .fathom-row-ui {
                    display: grid;
                    grid-template-columns: auto 1fr auto;
                    align-items: center;
                    background: white;
                    border: 1px solid #edf2f7;
                    border-right: 5px solid #4facfe;
                    border-radius: 8px;
                    padding: 0 16px;
                    height: 45px;
                    direction: rtl;
                    transition: all 0.2s ease;
                }
                div[data-testid="stVerticalBlock"] > div:has(.fathom-row-ui) {
                    gap: 0rem !important;
                }
                div.element-container:has(.fathom-row-ui) + div.element-container {
                    margin-top: -45px !important;
                    margin-bottom: 2px !important;
                }
                div.element-container:has(.fathom-row-ui) + div.element-container div[data-testid="stButton"] button {
                    background: transparent !important;
                    border: 1px solid transparent !important;
                    border-right: 5px solid transparent !important;
                    width: 100% !important;
                    height: 45px !important;
                    color: transparent !important;
                    z-index: 20;
                }
                div.element-container:has(.fathom-row-ui):has(+ div.element-container div[data-testid="stButton"] button:hover) .fathom-row-ui {
                    border-color: #4facfe;
                    background-color: #f8fafc;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
                }
                .fathom-pill-v2 {
                    background-color: #f1f5f9;
                    color: #475569;
                    padding: 1px 8px;
                    border-radius: 10px;
                    font-size: 0.75rem;
                    margin-right: 12px;
                }
                </style>
            """, unsafe_allow_html=True)

            f_meetings = st.session_state.get('fathom_meetings', [])

            if f_meetings:
                for idx, mtg in enumerate(f_meetings):
                    rec_id = mtg.get('recording_id')
                    title = mtg.get('title') or "פגישה"
                    date_str = mtg.get('recording_start_time', '')[:10]

                    open_key = f"open_{rec_id}"
                    is_open = st.session_state.get(open_key, False)
                    arrow = "expand_more" if is_open else "chevron_left"

                    st.markdown(f'''
                        <div class="fathom-row-ui">
                            <div style="display: flex; align-items: center;">
                                <span style="font-size: 1.1rem; margin-left: 10px;">📅</span>
                                <span style="font-weight: 600; color: #1e293b; font-size: 0.85rem;">{title}</span>
                                <span class="fathom-pill-v2">{date_str}</span>
                            </div>
                            <div></div>
                            <span class="material-symbols-rounded" style="color: #94a3b8; font-size: 20px;">{arrow}</span>
                        </div>
                    ''', unsafe_allow_html=True)

                    if st.button("", key=f"f_trig_{rec_id}_{idx}", use_container_width=True):
                        st.session_state[open_key] = not is_open
                        st.rerun()

                    if is_open:
                        with st.container():
                            s_key = f"sum_v4_{rec_id}"
                            if s_key not in st.session_state:
                                if st.button("צור סיכום עם AI 🪄", key=f"gen_{rec_id}"):
                                    with st.spinner("מנתח..."):
                                        raw = get_fathom_summary(rec_id)
                                        if raw:
                                            st.session_state[s_key] = refine_with_ai(raw)
                                            st.rerun()
                            else:
                                st.info(st.session_state[s_key])
            else:
                st.write("אין פגישות זמינות.")
