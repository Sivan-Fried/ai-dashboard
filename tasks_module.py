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

# ── חישוב גובה כולל של הגריד ──────────────────────────────────────────────────
# AG-Grid מחשב autoHeight לפי תוכן בפועל — אנחנו רק צריכים לתת לו מספיק
# גובה חלון (height=) כך שלא תופיע גלילה פנימית בתוך הגריד.
# הלוגיקה: כותרת + פילטר + סכום גובה כל שורה לפי כמות שורות טקסט משוערת.
# col_width_chars = הערכת רוחב עמודת התיאור בתווים (flex=4 מתוך סה"כ flex~10.4)
# אם עדיין רואים גלילה — להקטין ל-38; אם יש רווח ריק מיותר — להגדיל ל-48
def _calc_grid_height(df: pd.DataFrame, col_width_chars: int = 42) -> int:
    HEADER_H   = 48  # גובה שורת כותרות
    FILTER_H   = 48  # גובה שורת פילטרים
    ROW_BASE_H = 48  # גובה שורה בסיסי — תואם ל-padding-top/bottom:12px בתא
    LINE_H     = 22  # גובה שורת טקסט נוספת בגלישה (line-height ריאלי)
    PADDING    = 4   # ריפוד תחתון מינימלי

    total = 0
    for val in df["description"].astype(str):
        # ceil division — כמה שורות טקסט ייקח התיאור
        lines = max(1, -(-len(val) // col_width_chars))
        total += ROW_BASE_H + (lines - 1) * LINE_H

    return HEADER_H + FILTER_H + total + PADDING


def show_tasks_page(project_name=None):
    # ── טעינה ראשונית לתוך session_state ──────────────────
    if "tasks_df" not in st.session_state:
        st.session_state.tasks_df = load_tasks()
    df_all = st.session_state.tasks_df
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

    # כותרת כרגע לא מיושמת
    #title = f"ניהול משימות — {project_name}" if project_name else "ניהול משימות"
    #st.markdown(f"### {title}", unsafe_allow_html=True)
    #st.markdown(
        #"<p style='font-size:0.82rem;color:#a1a1aa;margin-top:-4px;"
        #"text-align:right;padding-right:18px;'>ניהול ומעקב משימות לפרויקט</p>",
        #unsafe_allow_html=True,
    #)

    total   = len(df)
    done    = len(df[df["status"] == "הושלם"])
    in_prog = len(df[df["status"] == "בביצוע"])
    late    = len(df[df["status"] == "באיחור"])

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f'''<div class="kpi-container"><div class="kpi-header"><div class="kpi-icon-box" style="background:#ecfdf5;"><span class="material-symbols-rounded" style="color:#10b981;">check_circle</span></div><span class="kpi-badge" style="background:#ecfdf5;color:#10b981;">הושלמו</span></div><div class="kpi-content"><div class="kpi-value-row"><span class="kpi-unit">משימות</span><span class="kpi-number">{done}</span></div></div></div>''', unsafe_allow_html=True)
    with k2:
        st.markdown(f'''<div class="kpi-container"><div class="kpi-header"><div class="kpi-icon-box" style="background:#eff6ff;"><span class="material-symbols-rounded" style="color:#3b82f6;">pending</span></div><span class="kpi-badge" style="background:#eff6ff;color:#3b82f6;">בביצוע</span></div><div class="kpi-content"><div class="kpi-value-row"><span class="kpi-unit">משימות</span><span class="kpi-number">{in_prog}</span></div></div></div>''', unsafe_allow_html=True)
    with k3:
        st.markdown(f'''<div class="kpi-container"><div class="kpi-header"><div class="kpi-icon-box" style="background:#fef2f2;"><span class="material-symbols-rounded" style="color:#ef4444;">warning</span></div><span class="kpi-badge" style="background:#fef2f2;color:#ef4444;">באיחור</span></div><div class="kpi-content"><div class="kpi-value-row"><span class="kpi-unit">משימות</span><span class="kpi-number">{late}</span></div></div></div>''', unsafe_allow_html=True)
    with k4:
        st.markdown(f'''<div class="kpi-container"><div class="kpi-header"><div class="kpi-icon-box" style="background:#f8fafc;"><span class="material-symbols-rounded" style="color:#94a3b8;">checklist</span></div><span class="kpi-badge" style="background:#f8fafc;color:#64748b;">סה"כ</span></div><div class="kpi-content"><div class="kpi-value-row"><span class="kpi-unit">משימות</span><span class="kpi-number">{total}</span></div></div></div>''', unsafe_allow_html=True)

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

    # ── הגדרות ברירת מחדל לכל העמודות ────────────────────────────────────────
    # שימו לב: wrapText ו-autoHeight לא מוגדרים כאן ברירת מחדל —
    # הם מוגדרים רק על עמודת description למטה.
    # הסיבה: rowHeight גלובלי מבטל autoHeight, ו-autoHeight על כולן פוגע בביצועים.
    gb.configure_default_column(
        filterable=True,
        sortable=True,
        resizable=True,
        filter="agTextColumnFilter",
        floatingFilter=True,
        suppressMenu=False,
    )

    # ── עמודת תיאור: wrapText + autoHeight רק עליה ────────────────────────────
    # flex=4 נותן לה את רוב הרוחב; כל העמודות ב-flex כדי למנוע גלילה אופקית
    gb.configure_column("description",  header_name="משימה",        flex=4,   wrapText=True, autoHeight=True, cellStyle={"fontWeight": "600", "color": "#3f3f46"})
    # ── שאר העמודות: flex מינימלי, ללא גלישת טקסט, ללא suppressSizeToFit ──────
    gb.configure_column("status",       header_name="סטטוס",        flex=1,   cellRenderer=cell_style_jscode, filter="agTextColumnFilter")
    gb.configure_column("responsible",  header_name="אחראי",         flex=1.2, filter="agTextColumnFilter")
    gb.configure_column("start_date",   header_name="תאריך התחלה",  flex=1.2)
    gb.configure_column("due_date",     header_name="תאריך יעד",    flex=1.2, cellStyle=due_style_jscode)
    # ── הערות: flex=1 — קטנה יותר מהתיאור אך לא נגעים בה לפי דרישה ──────────
    gb.configure_column("notes",        header_name="הערות",         flex=1.5)

    gb.configure_grid_options(
        enableRtl=True,
        # ── rowHeight הוסר! ────────────────────────────────────────────────────
        # rowHeight גלובלי מבטל את autoHeight שמוגדר על עמודת description.
        # AG-Grid יחשב גובה שורה לפי תוכן — זו ההתנהגות הנכונה.
        headerHeight=48,
        suppressRowClickSelection=True,
        rowStyle={"--ag-row-hover-color": "#fdf6f9"},
    )

    grid_options = gb.build()

    custom_css = {
        ".ag-header":            {"background-color": "#f8fafc !important", "border-bottom": "1px solid #f4f4f5 !important"},
        ".ag-header-cell-label": {"font-size": "12px !important", "font-weight": "700 !important", "color": "#94a3b8 !important", "font-family": "'Plus Jakarta Sans', sans-serif !important"},
        ".ag-cell":              {"font-size": "13px !important", "font-family": "'Plus Jakarta Sans', sans-serif !important", "color": "#3f3f46 !important", "border": "none !important", "padding-top": "12px !important", "padding-bottom": "12px !important"},
        ".ag-row":               {"border-bottom": "1px solid #f4f4f5 !important"},
        ".ag-row-hover":         {"background-color": "#fdf6f9 !important", "background-image": "none !important"},
        ".ag-row-hover .ag-cell": {"background-color": "#fdf6f9 !important"},
        ".ag-root-wrapper":      {"border": "none !important", "border-radius": "0 !important"},
        ".ag-floating-filter-input": {"font-family": "'Plus Jakarta Sans', sans-serif !important", "font-size": "12px !important"},
        ".ag-input-field-input": {"border-radius": "8px !important", "border": "1px solid #FADCE6 !important"},
    }

    st.markdown("### משימות הפרויקט", unsafe_allow_html=True)

    # ── ניהול מצב כפתור הוספה ──────────────────────────────
    add_key = "adding_task"
    if add_key not in st.session_state:
        st.session_state[add_key] = False

    # ── עיצוב כפתורים בkeys קבועים — CSS גלובלי שעובד ──────
    st.markdown("""
    <style>
    .st-key-task_add_btn button {
        background-color: #9ca3af !important;
        border: none !important;
        border-radius: 50% !important;
        width: 44px !important;
        height: 44px !important;
        min-width: 44px !important;
        min-height: 44px !important;
        max-width: 44px !important;
        max-height: 44px !important;
        padding: 0 !important;
        box-shadow: none !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    .st-key-task_add_btn button p {
        color: #ffffff !important;
        font-size: 1.4rem !important;
        font-weight: 700 !important;
        margin: 0 !important;
        padding: 0 !important;
        line-height: 1 !important;
    }
    .st-key-task_add_btn button:hover {
        background-color: #6b7280 !important;
        transform: scale(1.05) !important;
        box-shadow: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── טבלה + שורת הוספה + כפתור פלוס — הכל בקונטיינר אחד ──
    with st.container(border=True):
        AgGrid(
            df_display,
            gridOptions=grid_options,
            update_mode=GridUpdateMode.NO_UPDATE,
            allow_unsafe_jscode=True,
            custom_css=custom_css,
            theme="streamlit",
            fit_columns_on_grid_load=True,
            # ── גובה דינמי: מחושב לפי גלישת טקסט משוערת בעמודת התיאור ──────
            # AG-Grid עצמו מחשב את גובה כל שורה (autoHeight על description),
            # אנחנו רק מספקים חלון מספיק גדול שלא תהיה גלילה פנימית
            height=_calc_grid_height(df_display),
        )

        # שורת הוספה — מוצגת רק כשהכפתור נלחץ
        if st.session_state[add_key]:
            c1, c2, c3, c4, c5, c6, c7, c8 = st.columns([2, 1, 1, 1, 1, 1.5, 0.25, 0.25], vertical_alignment="center")
            with c1:
                new_desc = st.text_input("משימה", placeholder="הכנס משימה...", label_visibility="collapsed", key="task_new_desc")
            with c2:
                new_status = st.selectbox("סטטוס", ["ממתין", "בביצוע", "הושלם"], label_visibility="collapsed", key="task_new_status", index=None, placeholder="בחר סטטוס")
            with c3:
                new_resp = st.text_input("אחראי", placeholder="שם אחראי...", label_visibility="collapsed", key="task_new_resp")
            with c4:
                new_start = st.date_input("תאריך התחלה", label_visibility="collapsed", value=None, key="task_new_start", format="DD/MM/YYYY")
            with c5:
                new_due = st.date_input("תאריך יעד", label_visibility="collapsed", value=None, key="task_new_due", format="DD/MM/YYYY")
            with c6:
                new_notes = st.text_input("הערות", placeholder="הערות...", label_visibility="collapsed", key="task_new_notes")
            with c7:
                # כפתור שמירה — עיגול אפור עם וי לבן
                if st.button("✓", key="task_save_btn"):
                    if new_desc:
                        new_row = {
                            "project_name": project_name,
                            "description":  new_desc,
                            "status":       new_status or "ממתין",
                            "responsible":  new_resp,
                            "start_date":   new_start,
                            "due_date":     new_due,
                            "notes":        new_notes,
                        }
                        updated = pd.concat([df_all, pd.DataFrame([new_row])], ignore_index=True)
                        save_tasks(updated)
                        st.session_state.tasks_df = updated
                        st.session_state[add_key] = False
                        st.rerun()
            with c8:
                # כפתור ביטול — עיגול אפור עם X לבן
                if st.button("✕", key="task_cancel_btn"):
                    st.session_state[add_key] = False
                    st.rerun()

        st.markdown("<div style='margin-bottom:0.5rem;'></div>", unsafe_allow_html=True)

    # כפתור פלוס — מחוץ לטבלה, מוצג רק כשלא במצב עריכה
    if not st.session_state[add_key]:
        if st.button("+", key="task_add_btn"):
            st.session_state[add_key] = True
            st.rerun()

    st.markdown("<div style='margin-bottom:1.5rem;'></div>", unsafe_allow_html=True)
