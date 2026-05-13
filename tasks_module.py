# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import datetime
from zoneinfo import ZoneInfo
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode

TASKS_FILE = "tasks.xlsx"

def load_tasks():
    try:
        df = pd.read_excel(TASKS_FILE)
        df["start_date"] = pd.to_datetime(df["start_date"], errors="coerce")
        df["due_date"]   = pd.to_datetime(df["due_date"],   errors="coerce")
        return df
    except Exception as e:
        st.error(f"שגיאה בטעינת קובץ משימות: {e}")
        return pd.DataFrame()

def save_tasks(df):
    df.to_excel(TASKS_FILE, index=False)

def fmt_date(d):
    try:
        return d.strftime("%d/%m/%Y")
    except:
        return ""

def show_tasks_page(project_name=None):
    df_all = load_tasks()
    if df_all.empty:
        st.error("לא נמצא קובץ tasks.xlsx")
        return

    df = df_all[df_all["project_name"] == project_name].copy() if project_name else df_all.copy()
    today = datetime.datetime.now(ZoneInfo("Asia/Jerusalem")).date()

    for i, row in df.iterrows():
        if row["status"] != "הושלם":
            try:
                if row["due_date"].date() < today:
                    df.at[i, "status"] = "באיחור"
            except:
                pass

    title = f"ניהול משימות — {project_name}" if project_name else "ניהול משימות"
    st.markdown(f"### {title}", unsafe_allow_html=True)
    st.markdown(
        "<p style='font-size:0.82rem;color:#a1a1aa;margin-top:-4px;"
        "text-align:right;padding-right:18px;'>ניהול ומעקב משימות לפרויקט</p>",
        unsafe_allow_html=True,
    )

    total   = len(df)
    done    = len(df[df["status"] == "הושלם"])
    in_prog = len(df[df["status"] == "בביצוע"])
    late    = len(df[df["status"] == "באיחור"])

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f'''<div class="kpi-container"><div class="kpi-header"><div class="kpi-icon-box" style="background:#f8fafc;"><span class="material-symbols-rounded" style="color:#94a3b8;">checklist</span></div><span class="kpi-badge" style="background:#f8fafc;color:#64748b;">סה"כ</span></div><div class="kpi-content"><div class="kpi-value-row"><span class="kpi-unit">משימות</span><span class="kpi-number">{total}</span></div></div></div>''', unsafe_allow_html=True)
    with k2:
        st.markdown(f'''<div class="kpi-container"><div class="kpi-header"><div class="kpi-icon-box" style="background:#ecfdf5;"><span class="material-symbols-rounded" style="color:#10b981;">check_circle</span></div><span class="kpi-badge" style="background:#ecfdf5;color:#10b981;">הושלמו</span></div><div class="kpi-content"><div class="kpi-value-row"><span class="kpi-unit">משימות</span><span class="kpi-number">{done}</span></div></div></div>''', unsafe_allow_html=True)
    with k3:
        st.markdown(f'''<div class="kpi-container"><div class="kpi-header"><div class="kpi-icon-box" style="background:#eff6ff;"><span class="material-symbols-rounded" style="color:#3b82f6;">pending</span></div><span class="kpi-badge" style="background:#eff6ff;color:#3b82f6;">בביצוע</span></div><div class="kpi-content"><div class="kpi-value-row"><span class="kpi-unit">משימות</span><span class="kpi-number">{in_prog}</span></div></div></div>''', unsafe_allow_html=True)
    with k4:
        st.markdown(f'''<div class="kpi-container"><div class="kpi-header"><div class="kpi-icon-box" style="background:#fef2f2;"><span class="material-symbols-rounded" style="color:#ef4444;">warning</span></div><span class="kpi-badge" style="background:#fef2f2;color:#ef4444;">באיחור</span></div><div class="kpi-content"><div class="kpi-value-row"><span class="kpi-unit">משימות</span><span class="kpi-number">{late}</span></div></div></div>''', unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom:2rem;'></div>", unsafe_allow_html=True)

    df_display = df[["description", "status", "responsible", "start_date", "due_date", "notes"]].copy()
    df_display["start_date"] = df_display["start_date"].apply(fmt_date)
    df_display["due_date"]   = df_display["due_date"].apply(fmt_date)
    df_display["notes"]      = df_display["notes"].fillna("").astype(str).replace("nan", "")

    cell_style_jscode = JsCode("""
    class StatusRenderer {
        init(params) {
            var map = {
                '\u05d4\u05d5\u05e9\u05dc\u05dd':  ['\u0023ecfdf5','\u002310b981'],
                '\u05d1\u05d1\u05d9\u05e6\u05d5\u05e2': ['\u0023eff6ff','\u00233b82f6'],
                '\u05de\u05de\u05ea\u05d9\u05df':  ['\u0023f8fafc','\u002394a3b8'],
                '\u05d1\u05d0\u05d9\u05d7\u05d5\u05e8': ['\u0023fef2f2','\u0023ef4444']
            };
            var c = map[params.value] || ['\u0023f8fafc','\u002394a3b8'];
            this.eGui = document.createElement('span');
            this.eGui.style.cssText = 'display:inline-block;padding:3px 10px;border-radius:20px;font-size:11px;font-weight:700;background:' + c[0] + ';color:' + c[1];
            this.eGui.textContent = params.value || '';
        }
        getGui() { return this.eGui; }
        refresh() { return false; }
    }
    """)

    due_style_jscode = JsCode("""
    function(params) {
        var row = params.data;
        if (row && row['\u05e1\u05d8\u05d8\u05d5\u05e1'] === '\u05d1\u05d0\u05d9\u05d7\u05d5\u05e8') return {'color': '#ef4444', 'fontWeight': '600'};
        return {};
    }
    """)

    gb = GridOptionsBuilder.from_dataframe(df_display)

    gb.configure_default_column(
        filterable=True,
        sortable=True,
        resizable=True,
        filter="agTextColumnFilter",
        floatingFilter=True,
        suppressMenu=False,
        wrapText=True,
        autoHeight=True,
    )

    gb.configure_column("description",  header_name="משימה",        flex=2)
    gb.configure_column("status",       header_name="סטטוס",        flex=1,   cellRenderer=cell_style_jscode, filter="agSetColumnFilter")
    gb.configure_column("responsible",  header_name="אחראי",         flex=1,   filter="agSetColumnFilter")
    gb.configure_column("start_date",   header_name="תאריך התחלה",  flex=1)
    gb.configure_column("due_date",     header_name="תאריך יעד",    flex=1,   cellStyle=due_style_jscode)
    gb.configure_column("notes",        header_name="הערות",         flex=1.5)

    gb.configure_grid_options(
        enableRtl=True,
        rowHeight=44,
        headerHeight=48,
        suppressRowClickSelection=True,
    )

    grid_options = gb.build()

    custom_css = {
        ".ag-header":            {"background-color": "#f8fafc !important", "border-bottom": "1px solid #f4f4f5 !important"},
        ".ag-header-cell-label": {"font-size": "12px !important", "font-weight": "700 !important", "color": "#94a3b8 !important", "font-family": "'Plus Jakarta Sans', sans-serif !important"},
        ".ag-cell":              {"font-size": "13px !important", "font-family": "'Plus Jakarta Sans', sans-serif !important", "color": "#3f3f46 !important", "border": "none !important"},
        ".ag-row":               {"border-bottom": "1px solid #f4f4f5 !important"},
        ".ag-row:hover":         {"background-color": "#fdf6f9 !important"},
        ".ag-root-wrapper":      {"border": "none !important", "border-radius": "0 !important"},
        ".ag-floating-filter-input": {"font-family": "'Plus Jakarta Sans', sans-serif !important", "font-size": "12px !important"},
        ".ag-input-field-input": {"border-radius": "8px !important", "border": "1px solid #FADCE6 !important"},
    }

    st.markdown("### משימות הפרויקט", unsafe_allow_html=True)

    with st.container(border=True):
        AgGrid(
            df_display,
            gridOptions=grid_options,
            update_mode=GridUpdateMode.NO_UPDATE,
            allow_unsafe_jscode=True,
            custom_css=custom_css,
            theme="streamlit",
            fit_columns_on_grid_load=True,
            height=48 + 48 + (len(df_display) * 44) + 10,
        )

    st.markdown("<div style='margin-bottom:1.5rem;'></div>", unsafe_allow_html=True)

    add_key = f"adding_task_{project_name}"
    if add_key not in st.session_state:
        st.session_state[add_key] = False

    if not st.session_state[add_key]:
        if st.button("+ הוסף משימה", key=f"add_task_btn_{project_name}", use_container_width=True, type="secondary"):
            st.session_state[add_key] = True
            st.rerun()
    else:
        with st.container(border=True):
            st.markdown(
                "<div style='direction:rtl;font-weight:700;color:#3f3f46;margin-bottom:8px;'>משימה חדשה</div>",
                unsafe_allow_html=True
            )
            c1, c2 = st.columns(2)
            with c1:
                new_desc   = st.text_input("תיאור",       key=f"new_task_desc_{project_name}")
                new_resp   = st.text_input("גורם אחראי",  key=f"new_task_resp_{project_name}")
            with c2:
                new_status = st.selectbox("סטטוס", ["ממתין", "בביצוע", "הושלם"], key=f"new_task_status_{project_name}")
                new_notes  = st.text_input("הערות",       key=f"new_task_notes_{project_name}")
            d1, d2 = st.columns(2)
            with d1:
                new_start = st.date_input("תאריך התחלה", key=f"new_task_start_{project_name}")
            with d2:
                new_due   = st.date_input("תאריך יעד",   key=f"new_task_due_{project_name}")

            btn1, btn2, _ = st.columns([0.15, 0.15, 0.7])
            with btn1:
                if st.button("✓ שמור", key=f"save_task_{project_name}"):
                    if new_desc:
                        new_row = {
                            "project_name": project_name,
                            "description":  new_desc,
                            "status":       new_status,
                            "responsible":  new_resp,
                            "start_date":   new_start,
                            "due_date":     new_due,
                            "notes":        new_notes,
                        }
                        updated = pd.concat([df_all, pd.DataFrame([new_row])], ignore_index=True)
                        save_tasks(updated)
                        st.session_state[add_key] = False
                        st.rerun()
            with btn2:
                if st.button("✕ בטל", key=f"cancel_task_{project_name}"):
                    st.session_state[add_key] = False
                    st.rerun()
