# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import datetime
from zoneinfo import ZoneInfo

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

    st.markdown("""
    <style>
    .task-header {
        display:grid;
        grid-template-columns:2.5fr 1fr 1fr 0.8fr 0.8fr;
        gap:8px; padding:10px 16px;
        background:#f8fafc; border-radius:10px;
        margin-bottom:4px; direction:rtl; text-align:right;
    }
    .task-row {
        display:grid;
        grid-template-columns:2.5fr 1fr 1fr 0.8fr 0.8fr;
        gap:8px; padding:12px 16px;
        border-bottom:1px solid #f4f4f5;
        direction:rtl; text-align:right; align-items:center;
    }
    .task-row:hover { background:#fdf6f9; border-radius:8px; }
    </style>
    """, unsafe_allow_html=True)

    title = f"ניהול משימות — {project_name}" if project_name else "ניהול משימות"
    st.markdown(f"### {title}", unsafe_allow_html=True)
    st.markdown("<p style='font-size:0.82rem;color:#a1a1aa;margin-top:-4px;text-align:right;padding-right:18px;'>ניהול ומעקב משימות לפרויקט</p>", unsafe_allow_html=True)

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

    with st.container(border=True):
        st.markdown("""
        <div class="task-header">
            <div style="font-size:0.75rem;font-weight:700;color:#94a3b8;">משימה</div>
            <div style="font-size:0.75rem;font-weight:700;color:#94a3b8;">סטטוס</div>
            <div style="font-size:0.75rem;font-weight:700;color:#94a3b8;">אחראי</div>
            <div style="font-size:0.75rem;font-weight:700;color:#94a3b8;">התחלה</div>
            <div style="font-size:0.75rem;font-weight:700;color:#94a3b8;">יעד</div>
        </div>
        """, unsafe_allow_html=True)

        if df_view.empty:
            st.markdown("<p style='text-align:right;color:#a1a1aa;padding:12px 16px;'>אין משימות להצגה</p>", unsafe_allow_html=True)
        else:
            badge_styles = {
                "הושלם":  "background:#ecfdf5;color:#10b981;",
                "בביצוע": "background:#eff6ff;color:#3b82f6;",
                "ממתין":  "background:#f8fafc;color:#94a3b8;",
                "באיחור": "background:#fef2f2;color:#ef4444;",
            }
            for _, row in df_view.iterrows():
                s         = str(row.get("status", "ממתין"))
                desc      = str(row.get("description", ""))
                resp      = str(row.get("responsible", ""))
                start_str = fmt_date(row.get("start_date", ""))
                due_str   = fmt_date(row.get("due_date", ""))
                notes     = str(row.get("notes", "")).strip()
                notes_html = f"<div style='font-size:0.7rem;color:#a1a1aa;margin-top:2px;'>{notes}</div>" if notes and notes.lower() != "nan" else ""
                due_color  = "#ef4444" if s == "באיחור" else "#71717a"
                badge_style = badge_styles.get(s, badge_styles["ממתין"])

                st.markdown(f"""<div class="task-row">
<div><div style="font-size:0.82rem;font-weight:600;color:#3f3f46;">{desc}</div>{notes_html}</div>
<div><div style="display:inline-block;padding:3px 10px;border-radius:20px;font-size:0.72rem;font-weight:700;{badge_style}">{s}</div></div>
<div style="font-size:0.82rem;color:#3f3f46;">{resp}</div>
<div style="font-size:0.78rem;color:#71717a;">{start_str}</div>
<div style="font-size:0.78rem;color:{due_color};">{due_str}</div>
</div>""", unsafe_allow_html=True)

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
            st.markdown("<div style='direction:rtl;font-weight:700;color:#3f3f46;margin-bottom:8px;'>משימה חדשה</div>", unsafe_allow_html=True)
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
