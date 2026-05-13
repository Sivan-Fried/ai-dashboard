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

    # כותרת
    title = f"ניהול משימות — {project_name}" if project_name else "ניהול משימות"
    st.markdown(f"### {title}", unsafe_allow_html=True)
    st.markdown(
        "<p style='font-size:0.82rem;color:#a1a1aa;margin-top:-4px;"
        "text-align:right;padding-right:18px;'>ניהול ומעקב משימות לפרויקט</p>",
        unsafe_allow_html=True,
    )

    # ── KPIs ──────────────────────────────────────────────
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

    st.markdown("<div style='margin-bottom:1.5rem;'></div>", unsafe_allow_html=True)

    # ── הכנת DataFrame ────────────────────────────────────
    df_display = df[["description", "status", "responsible", "start_date", "due_date", "notes"]].copy()
    df_display["start_date"] = df_display["start_date"].apply(fmt_date)
    df_display["due_date"]   = df_display["due_date"].apply(fmt_date)
    df_display["notes"]      = df_display["notes"].fillna("").astype(str).replace({"nan": ""})

    # ── cellRenderer לבאדג' סטטוס ─────────────────────────
    status_renderer = JsCode("""
    function(params) {
        if (!params.value) return '';
        var colors = {
            'הושלם':  {bg: '#ecfdf5', color: '#10b981'},
            'בביצוע': {bg: '#eff6ff', color: '#3b82f6'},
            'ממתין':  {bg: '#f8fafc', color: '#94a3b8'},
            'באיחור': {bg: '#fef2f2', color: '#ef4444'}
        };
        var c = colors[params.value] || {bg: '#f8fafc', color: '#94a3b8'};
        return '<span style="display:inline-block;padding:3px 10px;border-radius:20px;font-size:11px;font-weight:700;background:' + c.bg + ';color:' + c.color + ';">' + params.value + '</span>';
    }
    """)

    # ── cellStyle לתאריך יעד אם באיחור ───────────────────
    due_style = JsCode("""
    function(params) {
        if (params.data && params.data['\u05e1\u05d8\u05d8\u05d5\u05e1'] === '\u05d1\u05d0\u05d9\u05d7\u05d5\u05e8') {
            return {'color': '#ef4444', 'fontWeight': '600'};
        }
        return {'color': '#71717a'};
    }
    """)

    # ── הגדרת AgGrid ──────────────────────────────────────
    gb = GridOptionsBuilder.from_dataframe(df_display)

    gb.configure_default_column(
        filterable=True,
        sortable=True,
        resizable=True,
        floatingFilter=True,
        filter="agTextColumnFilter",
        wrapText=False,
        suppressMenu=True,
    )

    gb.configure_column("description",  header_name="משימה",        flex=2)
    gb.configure_column("status",       header_name="סטטוס",        flex=1,   cellRenderer=status_renderer, filter="agSetColumnFilter")
    gb.configure_column("responsible",  header_name="אחראי",         flex=1,   filter="agSetColumnFilter")
    gb.configure_column("start_date",   header_name="תאריך התחלה",  flex=1,   filter="agSetColumnFilter")
    gb.configure_column("due_date",     header_name="תאריך יעד",    flex=1,   filter="agSetColumnFilter", cellStyle=due_style)
    gb.configure_column("notes",        header_name="הערות",         flex=1.5, filter="agTextColumnFilter")

    gb.configure_grid_options(
        enableRtl=True,
        rowHeight=44,
        headerHeight=44,
        domLayout="autoHeight",
        suppressRowClickSelection=True,
        suppressCellFocus=True,
    )

    custom_css = {
        ".ag-header":            {"background-color": "#f8fafc !important", "border-bottom": "1px solid #f4f4f5 !important"},
        ".ag-header-cell-label": {"font-size": "12px !important", "font-weight": "700 !important", "color": "#94a3b8 !important", "font-family": "'Plus Jakarta Sans', sans-serif !important", "justify-content": "flex-end !important"},
        ".ag-cell":              {"font-size": "13px !important", "font-family": "'Plus Jakarta Sans', sans-serif !important", "color": "#3f3f46 !important", "border": "none !important", "display": "flex !important", "align-items": "center !important", "justify-content": "flex-end !important"},
        ".ag-row":               {"border-bottom": "1px solid #f4f4f5 !important"},
        ".ag-row:hover":         {"background-color": "#fdf6f9 !important"},
        ".ag-root-wrapper":      {"border": "1px solid #f4f4f5 !important", "border-radius": "16px !important"},
        ".ag-floating-filter-input input": {"border": "1px solid #FADCE6 !important", "border-radius": "8px !important", "font-size": "11px !important", "font-family": "'Plus Jakarta Sans', sans-serif !important"},
        ".ag-header-cell":       {"border-right": "none !important"},
        ".ag-cell-value":        {"direction": "rtl !important"},
    }

    AgGrid(
        df_display,
        gridOptions=gb.build(),
        update_mode=GridUpdateMode.NO_UPDATE,
        allow_unsafe_jscode=True,
        custom_css=custom_css,
        theme="streamlit",
        fit_columns_on_grid_load=True,
        height=None,
    )

    st.markdown("<div style='margin-bottom:1.5rem;'></div>", unsafe_allow_html=True)

    # ── הוספת משימה חדשה ─────────────────────────────────
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
