# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import datetime
from zoneinfo import ZoneInfo

TASKS_FILE = "tasks.xlsx"

STATUS_COLORS = {
    "הושלם":  {"bg": "#ecfdf5", "color": "#10b981"},
    "בביצוע": {"bg": "#eff6ff", "color": "#3b82f6"},
    "ממתין":  {"bg": "#f8fafc", "color": "#94a3b8"},
    "באיחור": {"bg": "#fef2f2", "color": "#ef4444"},
}

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

    def calc_status(row):
        if row["status"] == "הושלם":
            return "הושלם"
        try:
            if row["due_date"].date() < today:
                return "באיחור"
        except:
            pass
        return row["status"]

    df["status"] = df.apply(calc_status, axis=1)

    # כותרת
    st.markdown(f"### משימות — {project_name}" if project_name else "### משימות", unsafe_allow_html=True)
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
        st.markdown(f'''<div class="kpi-container">
            <div class="kpi-header">
                <div class="kpi-icon-box" style="background:#f8fafc;">
                    <span class="material-symbols-rounded" style="color:#94a3b8;">checklist</span>
                </div>
                <span class="kpi-badge" style="background:#f8fafc;color:#64748b;">סה"כ</span>
            </div>
            <div class="kpi-content"><div class="kpi-value-row">
                <span class="kpi-unit">משימות</span><span class="kpi-number">{total}</span>
            </div></div>
        </div>''', unsafe_allow_html=True)
    with k2:
        st.markdown(f'''<div class="kpi-container">
            <div class="kpi-header">
                <div class="kpi-icon-box" style="background:#ecfdf5;">
                    <span class="material-symbols-rounded" style="color:#10b981;">check_circle</span>
                </div>
                <span class="kpi-badge" style="background:#ecfdf5;color:#10b981;">הושלמו</span>
            </div>
            <div class="kpi-content"><div class="kpi-value-row">
                <span class="kpi-unit">משימות</span><span class="kpi-number">{done}</span>
            </div></div>
        </div>''', unsafe_allow_html=True)
    with k3:
        st.markdown(f'''<div class="kpi-container">
            <div class="kpi-header">
                <div class="kpi-icon-box" style="background:#eff6ff;">
                    <span class="material-symbols-rounded" style="color:#3b82f6;">pending</span>
                </div>
                <span class="kpi-badge" style="background:#eff6ff;color:#3b82f6;">בביצוע</span>
            </div>
            <div class="kpi-content"><div class="kpi-value-row">
                <span class="kpi-unit">משימות</span><span class="kpi-number">{in_prog}</span>
            </div></div>
        </div>''', unsafe_allow_html=True)
    with k4:
        st.markdown(f'''<div class="kpi-container">
            <div class="kpi-header">
                <div class="kpi-icon-box" style="background:#fef2f2;">
                    <span class="material-symbols-rounded" style="color:#ef4444;">warning</span>
                </div>
                <span class="kpi-badge" style="background:#fef2f2;color:#ef4444;">באיחור</span>
            </div>
            <div class="kpi-content"><div class="kpi-value-row">
                <span class="kpi-unit">משימות</span><span class="kpi-number">{late}</span>
            </div></div>
        </div>''', unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom:1rem;'></div>", unsafe_allow_html=True)

    # ── פילטר סטטוס ──────────────────────────────────────
    status_options = ["הכל", "בביצוע", "ממתין", "הושלם", "באיחור"]
    filter_key = f"task_filter_{project_name}"
    if filter_key not in st.session_state:
        st.session_state[filter_key] = "הכל"

    f_cols = st.columns(len(status_options))
    for i, opt in enumerate(status_options):
        with f_cols[i]:
            if st.button(opt, key=f"filter_{project_name}_{opt}", use_container_width=True):
                st.session_state[filter_key] = opt
                st.rerun()

    selected_filter = st.session_state[filter_key]
    df_view = df if selected_filter == "הכל" else df[df["status"] == selected_filter]

    st.markdown("<div style='margin-bottom:0.5rem;'></div>", unsafe_allow_html=True)

    # ── טבלת משימות ──────────────────────────────────────
    with st.container(border=True):
        # כותרת טבלה
        h1, h2, h3, h4, h5 = st.columns([2.5, 1, 1, 0.8, 0.8])
        with h1: st.markdown("<span style='font-size:0.75rem;font-weight:700;color:#94a3b8;'>תיאור</span>", unsafe_allow_html=True)
        with h2: st.markdown("<span style='font-size:0.75rem;font-weight:700;color:#94a3b8;'>סטטוס</span>", unsafe_allow_html=True)
        with h3: st.markdown("<span style='font-size:0.75rem;font-weight:700;color:#94a3b8;'>אחראי</span>", unsafe_allow_html=True)
        with h4: st.markdown("<span style='font-size:0.75rem;font-weight:700;color:#94a3b8;'>התחלה</span>", unsafe_allow_html=True)
        with h5: st.markdown("<span style='font-size:0.75rem;font-weight:700;color:#94a3b8;'>יעד</span>", unsafe_allow_html=True)

        st.markdown("<hr style='margin:4px 0 8px 0;border:none;border-top:1px solid #f4f4f5;'>", unsafe_allow_html=True)

        if df_view.empty:
            st.markdown("<p style='text-align:right;color:#a1a1aa;'>אין משימות להצגה</p>", unsafe_allow_html=True)
        else:
            for _, row in df_view.iterrows():
                s  = row.get("status", "ממתין")
                sc = STATUS_COLORS.get(s, STATUS_COLORS["ממתין"])
                notes = str(row.get("notes", "")).strip()
                show_notes = notes and notes != "nan"
                due_color = "#ef4444" if s == "באיחור" else "#71717a"

                c1, c2, c3, c4, c5 = st.columns([2.5, 1, 1, 0.8, 0.8])
                with c1:
                    st.markdown(
                        f"<div style='font-size:0.82rem;font-weight:600;color:#3f3f46;'>{row['description']}</div>"
                        + (f"<div style='font-size:0.7rem;color:#a1a1aa;'>{notes}</div>" if show_notes else ""),
                        unsafe_allow_html=True
                    )
                with c2:
                    st.markdown(
                        f"<span style='display:inline-block;padding:3px 10px;border-radius:20px;"
                        f"font-size:0.72rem;font-weight:700;"
                        f"background:{sc['bg']};color:{sc['color']};'>{s}</span>",
                        unsafe_allow_html=True
                    )
                with c3:
                    st.markdown(f"<span style='font-size:0.82rem;color:#3f3f46;'>{row.get('responsible','')}</span>", unsafe_allow_html=True)
                with c4:
                    st.markdown(f"<span style='font-size:0.78rem;color:#71717a;'>{fmt_date(row.get('start_date',''))}</span>", unsafe_allow_html=True)
                with c5:
                    st.markdown(f"<span style='font-size:0.78rem;color:{due_color};'>{fmt_date(row.get('due_date',''))}</span>", unsafe_allow_html=True)

                st.markdown("<hr style='margin:4px 0;border:none;border-top:1px solid #f4f4f5;'>", unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom:1rem;'></div>", unsafe_allow_html=True)

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
            st.markdown("<div style='direction:rtl;font-weight:700;color:#3f3f46;margin-bottom:8px;'>משימה חדשה</div>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                new_desc   = st.text_input("תיאור",        key=f"new_task_desc_{project_name}")
                new_resp   = st.text_input("גורם אחראי",   key=f"new_task_resp_{project_name}")
            with c2:
                new_status = st.selectbox("סטטוס", ["ממתין", "בביצוע", "הושלם"], key=f"new_task_status_{project_name}")
                new_notes  = st.text_input("הערות",        key=f"new_task_notes_{project_name}")
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
