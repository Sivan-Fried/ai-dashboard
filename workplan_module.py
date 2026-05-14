import pandas as pd
import datetime
import re


def clean_text(x):
    if not isinstance(x, str):
        x = str(x)
    x = x.strip()
    x = re.sub(r'[\u200f\u202b\u202c\u202d\u202e]', '', x)
    x = re.sub(r'[\x00-\x1F\x7F]', '', x)
    return x


def load_workplan_df():
    df = pd.read_excel("work_plans.xlsx")
    df["date"] = pd.to_datetime(df["date"], dayfirst=False, errors="coerce")
    df["project_name"] = df["project_name"].apply(clean_text)
    return df


def build_timeline_html(project_name):
    df = load_workplan_df()
    project_name = clean_text(project_name)
    project_df = df[df["project_name"] == project_name].copy()
    project_df = project_df.sort_values("date")

    if project_df.empty:
        return "<div style='text-align:right;font-size:16px;padding:10px;'>אין נתונים עבור הפרויקט</div>"

    today     = datetime.date.today()
    today_str = today.strftime("%d.%m")
    today_iso = today.strftime("%Y-%m-%d")

    items = []
    for _, row in project_df.iterrows():
        name = str(row["milestone_name"])
        tag_class = (
            "amit"  if "עמיתים"  in name else
            "measy" if "מעסיקים" in name else
            "soch"  if "סוכנים"  in name else
            "amit"
        )
        status_val   = str(row["status"]).strip()
        status_class = {"LIVE": "live", "WIP": "wip", "HOLD": ""}.get(status_val, "")
        date_str     = row["date"].strftime("%d.%m.%Y")
        date_iso     = row["date"].strftime("%Y-%m-%d")
        contents     = str(row.get("version_contents", "")).strip()
        tooltip      = (
            f"<div class='tip'>{contents.replace(chr(10), '<br>')}</div>"
            if contents and contents != "nan" else ""
        )
        items.append(dict(
            name=name, tag_class=tag_class,
            status_val=status_val, status_class=status_class,
            date_str=date_str, date_iso=date_iso, tooltip=tooltip
        ))

    def card(it):
        return (
            f"<div class='card' data-date='{it['date_iso']}'>"
            f"{it['tooltip']}"
            f"<span class='tag {it['tag_class']}'>{it['name']}</span>"
            f"<div class='dt'>{it['date_str']}</div>"
            f"<span class='st {it['status_class']}'>{it['status_val']}</span>"
            f"</div>"
        )

    rows_html = []
    i = 0
    side = 0

    while i < len(items):
        it = items[i]
        group = [it]
        j = i + 1
        while j < len(items) and items[j]["date_iso"] == it["date_iso"]:
            group.append(items[j])
            j += 1

        if len(group) >= 2:
            rows_html.append(
                f"<div class='row' data-date='{it['date_iso']}'>"
                f"<div class='cl'>{card(group[0])}</div>"
                f"<div class='dot'></div>"
                f"<div class='cr'>{card(group[1])}</div>"
                f"</div>"
            )
        else:
            if side % 2 == 0:
                rows_html.append(
                    f"<div class='row' data-date='{it['date_iso']}'>"
                    f"<div class='cl'>{card(it)}</div>"
                    f"<div class='dot'></div>"
                    f"<div class='cr'></div>"
                    f"</div>"
                )
            else:
                rows_html.append(
                    f"<div class='row' data-date='{it['date_iso']}'>"
                    f"<div class='cl'></div>"
                    f"<div class='dot'></div>"
                    f"<div class='cr'>{card(it)}</div>"
                    f"</div>"
                )
            side += 1
        i = j

    rows_str = "\n".join(rows_html)

    return f"""<!DOCTYPE html>
<html lang="he">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link href="https://fonts.googleapis.com/css2?family=Assistant:wght@400;600;700&display=swap" rel="stylesheet">
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: 'Assistant', sans-serif; background: white; padding-bottom: 40px; }}

.controls {{ display: flex; justify-content: flex-end; padding: 12px 20px 10px; direction: rtl; margin-bottom: 8px; }}
.toggle-group {{ display: flex; background: white; border-radius: 12px; box-shadow: 0 1px 4px rgba(0,0,0,.08); padding: 4px; }}
.toggle-btn {{ padding: 5px 12px; font-size: 12px; font-weight: 600; font-family: 'Assistant', sans-serif; border: none; border-radius: 8px; cursor: pointer; color: #94a3b8; background: transparent; }}
.toggle-btn.active {{ background: #FADCE6; color: #63646c; }}
.toggle-btn:hover:not(.active) {{ color: #475569; }}

.tl {{ position: relative; width: 100%; direction: ltr; }}
.tl::before {{
  content: '';
  position: absolute;
  top: -16px; bottom: -16px;
  left: 50%; width: 2px; margin-left: -1px;
  background: #cbd5e1; z-index: 0;
}}
.tl::after {{
  content: '';
  position: absolute;
  top: -16px; bottom: -16px;
  left: calc(50% - 4px);
  width: 0;
  z-index: 1;
  pointer-events: none;
}}

.row {{
  position: relative;
  width: 100%;
  min-height: 84px;
  display: flex;
  align-items: center;
}}
.row.hidden {{ display: none !important; }}

.cl {{
  width: calc(50% - 6px);
  display: flex;
  justify-content: flex-end;
  padding-right: 80px;
  position: relative; z-index: 1;
}}
.cr {{
  width: calc(50% - 6px);
  display: flex;
  justify-content: flex-start;
  padding-left: 80px;
  margin-left: 12px;
  position: relative; z-index: 1;
}}

.dot {{
  position: absolute;
  left: 50%; top: 50%;
  transform: translate(-50%, -50%);
  width: 12px; height: 12px;
  background: #475569;
  border-radius: 50%;
  border: 2px solid white;
  box-shadow: 0 0 0 2px #475569;
  z-index: 2; flex-shrink: 0;
}}

.card {{
  background: white;
  padding: 7px 10px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,.08);
  border: 1px solid #f1f5f9;
  text-align: center;
  width: 130px;
  flex-shrink: 0;
  position: relative;
  direction: rtl;
}}
.card:hover .tip {{ display: block; }}

.cl .card::after {{
  content: '';
  position: absolute;
  top: 50%; right: -80px;
  width: 80px; height: 2px;
  background: #cbd5e1;
  transform: translateY(-50%);
}}
.cr .card::before {{
  content: '';
  position: absolute;
  top: 50%; left: -80px;
  width: 80px; height: 2px;
  background: #cbd5e1;
  transform: translateY(-50%);
}}

.tag {{ font-size: 10px; font-weight: 700; padding: 1px 5px; border-radius: 3px; display: inline-block; margin-bottom: 2px; line-height: 1.4; }}
.amit  {{ background: #FADCE6; color: #831843; }}
.measy {{ background: #eff6ff; color: #1e40af; }}
.soch  {{ background: #fff7ed; color: #9a3412; }}
.dt {{ font-size: 12px; font-weight: 600; color: #1e293b; margin: 2px 0; }}
.st {{ font-size: 9px; font-weight: 700; display: block; color: #94a3b8; margin-top: 1px; }}
.live {{ color: #10b981; }}
.wip  {{ color: #f59e0b; }}

.tip {{
  display: none; position: absolute; bottom: 110%; right: 50%;
  transform: translateX(50%); background: #1e293b; color: white;
  font-size: 11px; line-height: 1.6; padding: 8px 12px; border-radius: 8px;
  white-space: nowrap; text-align: right; direction: rtl;
  z-index: 100; box-shadow: 0 4px 12px rgba(0,0,0,.2); pointer-events: none;
}}
.tip::after {{
  content: ''; position: absolute; top: 100%; right: 50%;
  transform: translateX(50%); border: 5px solid transparent; border-top-color: #1e293b;
}}

.today {{
  position: relative; display: flex; align-items: center; justify-content: center;
  height: 28px; margin: 4px 0; width: 100%;
}}
.today::before {{
  content: ''; position: absolute; left: 0; right: 0; top: 50%;
  border-top: 2px dashed #f0b8cb;
}}
.today span {{
  background: #FADCE6; color: #63646c; font-size: 11px; font-weight: 700;
  padding: 2px 14px; border-radius: 20px; position: relative; z-index: 2;
  direction: rtl; white-space: nowrap;
}}
</style>
</head>
<body>

<div class="controls">
  <div class="toggle-group">
    <button class="toggle-btn active" onclick="fv('all',this)">הכל</button>
    <button class="toggle-btn" onclick="fv('quarter',this)">רבעון נוכחי</button>
    <button class="toggle-btn" onclick="fv('month',this)">חודש נוכחי</button>
  </div>
</div>

<div class="tl" id="tl">
{rows_str}
</div>

<script>
var todayISO='{today_iso}';
var CM=new Date().getMonth(),CY=new Date().getFullYear(),CQ=Math.floor(CM/3);

(function(){{
  var rows=document.querySelectorAll('.row'),tl=document.getElementById('tl');

  var topDot = document.createElement('div');
  topDot.style.cssText = 'position:absolute;top:-21px;left:50%;transform:translateX(-50%);width:10px;height:10px;border-radius:50%;background:white;border:2px solid #94a3b8;z-index:2;';
  tl.style.position = 'relative';
  tl.appendChild(topDot);
  var botDot = document.createElement('div');
  botDot.style.cssText = 'position:absolute;bottom:-21px;left:50%;transform:translateX(-50%);width:10px;height:10px;border-radius:50%;background:white;border:2px solid #94a3b8;z-index:2;';
  tl.appendChild(botDot);

  var m=document.createElement('div');
  m.className='today';m.id='today-el';
  m.innerHTML='<span>היום {today_str}</span>';
  var placed=false;
  for(var i=0;i<rows.length;i++){{
    if(rows[i].getAttribute('data-date')>todayISO){{tl.insertBefore(m,rows[i]);placed=true;break;}}
  }}
  if(!placed)tl.appendChild(m);
}})();

function fv(mode,btn){{
  document.querySelectorAll('.toggle-btn').forEach(function(b){{b.classList.remove('active');}});
  btn.classList.add('active');
  document.querySelectorAll('.row').forEach(function(row){{
    if(mode==='all'){{row.classList.remove('hidden');row.querySelectorAll('.card').forEach(function(c){{c.style.opacity='1';}});return;}}
    var cards=row.querySelectorAll('.card'),any=false;
    cards.forEach(function(c){{
      var d=new Date(c.getAttribute('data-date'));
      var show=(mode==='month')?(d.getMonth()===CM&&d.getFullYear()===CY):(Math.floor(d.getMonth()/3)===CQ&&d.getFullYear()===CY);
      c.style.opacity=show?'1':'0';if(show)any=true;
    }});
    row.classList.toggle('hidden',!any);
  }});
  var el=document.getElementById('today-el');if(el)el.style.display='flex';
}}
</script>
</body>
</html>"""


def show_workplan_page(project_name=None):
    import streamlit as st
    import streamlit.components.v1 as components
    import datetime

    try:
        df = load_workplan_df()
        p = clean_text(project_name) if project_name else ""
        _pf = df[df["project_name"] == p]
        n = max(len(_pf), 1)
        
        _yr    = datetime.date.today().year
        _live  = len(_pf[_pf["status"].str.strip() == "LIVE"])
        _wip   = len(_pf[_pf["status"].str.strip().isin(["בעבודה", "WIP"])])
        _tbd   = len(_pf[_pf["status"].str.strip() == "TBD"])
        _total = len(_pf[_pf["date"].dt.year == _yr])

        # תצוגת KPIs על הרקע האפור
        k0, k1, k2, k3 = st.columns(4)
        with k0:
            st.markdown(f'''<div class="kpi-container"><div class="kpi-header"><div class="kpi-icon-box" style="background:#ecfdf5;"><span class="material-symbols-rounded" style="color:#10b981;">check_circle</span></div><span class="kpi-badge" style="background:#ecfdf5;color:#10b981;">LIVE</span></div><div class="kpi-content"><div class="kpi-value-row"><span class="kpi-unit">גרסאות</span><span class="kpi-number">{_live}</span></div></div></div>''', unsafe_allow_html=True)
        with k1:
            st.markdown(f'''<div class="kpi-container"><div class="kpi-header"><div class="kpi-icon-box" style="background:#fffbeb;"><span class="material-symbols-rounded" style="color:#f59e0b;">pending</span></div><span class="kpi-badge" style="background:#fffbeb;color:#f59e0b;">בעבודה</span></div><div class="kpi-content"><div class="kpi-value-row"><span class="kpi-unit">גרסאות</span><span class="kpi-number">{_wip}</span></div></div></div>''', unsafe_allow_html=True)
        with k2:
            st.markdown(f'''<div class="kpi-container"><div class="kpi-header"><div class="kpi-icon-box" style="background:#f8fafc;"><span class="material-symbols-rounded" style="color:#94a3b8;">schedule</span></div><span class="kpi-badge" style="background:#f8fafc;color:#94a3b8;">TBD</span></div><div class="kpi-content"><div class="kpi-value-row"><span class="kpi-unit">גרסאות</span><span class="kpi-number">{_tbd}</span></div></div></div>''', unsafe_allow_html=True)
        with k3:
            st.markdown(f'''<div class="kpi-container"><div class="kpi-header"><div class="kpi-icon-box" style="background:#eff6ff;"><span class="material-symbols-rounded" style="color:#3b82f6;">calendar_today</span></div><span class="kpi-badge" style="background:#eff6ff;color:#3b82f6;">סה״כ השנה</span></div><div class="kpi-content"><div class="kpi-value-row"><span class="kpi-unit">גרסאות</span><span class="kpi-number">{_total}</span></div></div></div>''', unsafe_allow_html=True)

        # רווח משמעותי מתחת ל-KPIs
        st.markdown("<div style='margin-bottom:2.5rem;'></div>", unsafe_allow_html=True)

        # המיכל הלבן
        with st.container(border=True):
            # כותרת מעוצבת בתוך המיכל - יישור לימין ופונט Bold
            st.markdown(f"""
                <div style='text-align: right; direction: rtl; padding: 10px 0;'>
                    <span style='font-size: 1.25rem; font-weight: 800; color: #3f3f46;'>
                        תוכנית עבודה — {project_name}
                    </span>
                </div>
            """, unsafe_allow_html=True)
            
            # הצגת הגרף
            height = 60 + n * 95 + 60 + 60
            html = build_timeline_html(project_name)
            components.html(html, height=height, scrolling=False)
            
    except Exception as e:
        st.error(f"שגיאה בטעינת תוכנית העבודה: {e}")
