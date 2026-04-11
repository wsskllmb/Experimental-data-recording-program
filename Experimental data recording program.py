import streamlit as st
import pandas as pd
from datetime import datetime
import os
import uuid

# ====================== 科技感CSS ======================
st.set_page_config(page_title="实验记录系统", layout="wide")

st.markdown("""
<style>
.stApp { background: #0b1020; color: #e0e0e0; }
.main-title { font-size: 28px; font-weight: bold; color: #0cf; text-shadow: 0 0 10px #0cf; }
.card { background: #121a33; border:1px solid #253466; border-radius:12px; padding:22px; margin-bottom:18px; }
.stTextInput>div>div, .stTextArea>div>div { background:#162040 !important; border-color:#354980 !important; color:#e0e0e0 !important; }
.stButton>button { background:linear-gradient(90deg,#0088ff,#00ccff); color:#fff; font-weight:bold; border:none; border-radius:8px; }
</style>
""", unsafe_allow_html=True)

# ====================== 永久存储路径 ======================
BASE_DIR = os.path.abspath(os.getcwd())
USER_FILE = os.path.join(BASE_DIR, "users.csv")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "upload_files")

# 确保文件夹永远存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 确保用户文件永远存在
if not os.path.exists(USER_FILE):
    pd.DataFrame(columns=["username", "password"]).to_csv(
        USER_FILE, index=False, encoding="utf-8-sig"
    )

# ====================== 登录状态 ======================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None

# ====================== 注册（永久保存） ======================
def register(username, password):
    users = pd.read_csv(USER_FILE, encoding="utf-8-sig")
    if username in users["username"].values:
        return False
    new_row = pd.DataFrame({"username": [username], "password": [password]})
    users = pd.concat([users, new_row], ignore_index=True)
    users.to_csv(USER_FILE, index=False, encoding="utf-8-sig")
    return True

# ====================== 登录验证 ======================
def login(username, password):
    users = pd.read_csv(USER_FILE, encoding="utf-8-sig")
    return not users[(users.username == username) & (users.password == password)].empty

# ====================== 登录/注册界面 ======================
if not st.session_state.logged_in:
    st.markdown('<div class="main-title">🔬 实验记录系统</div>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["登录", "注册"])

    with tab1:
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            u = st.text_input("用户名")
            p = st.text_input("密码", type="password")
            if st.button("登录", use_container_width=True):
                if login(u, p):
                    st.session_state.logged_in = True
                    st.session_state.current_user = u
                    st.rerun()
                else:
                    st.error("用户名或密码错误")
            st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            new_u = st.text_input("设置用户名")
            new_p = st.text_input("设置密码", type="password")
            if st.button("注册", use_container_width=True):
                if not new_u or not new_p:
                    st.error("不能为空")
                elif register(new_u, new_p):
                    st.success("注册成功！请登录")
                else:
                    st.error("用户名已存在")
            st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ====================== 已登录 ======================
user = st.session_state.current_user
st.markdown(f'<div class="main-title">🧪 控制台 | 欢迎 {user}</div>', unsafe_allow_html=True)

# 退出
if st.button("退出登录"):
    st.session_state.logged_in = False
    st.rerun()

# ====================== 用户独立数据文件 ======================
RECORD_FILE = os.path.join(BASE_DIR, f"records_{user}.csv")

# ====================== 读取/保存 实验记录 ======================
def load_records():
    if os.path.exists(RECORD_FILE):
        df = pd.read_csv(RECORD_FILE, encoding="utf-8-sig")
    else:
        df = pd.DataFrame(columns=[
            "唯一ID", "记录时间", "实验名称", "实验人员", "实验数据", "备注", "保存文件名", "原始文件名"
        ])
    for col in df.columns:
        df[col] = df[col].astype(str).fillna("")
    return df

def save_records(df):
    df.to_csv(RECORD_FILE, index=False, encoding="utf-8-sig")

# ====================== 新增记录 ======================
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown("### 📝 新增实验记录")
with st.form("add_form", clear_on_submit=True):
    c1, c2 = st.columns(2)
    with c1:
        exp_name = st.text_input("实验名称")
        exp_person = st.text_input("实验人员")
    with c2:
        exp_data = st.text_input("实验数据")
        exp_note = st.text_area("备注", height=80)
    files = st.file_uploader("上传附件", accept_multiple_files=True)
    submit = st.form_submit_button("✅ 保存", use_container_width=True)

if submit:
    if not exp_name or not exp_person:
        st.error("必填")
    else:
        df = load_records()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_f, orig_f = [], []
        for f in files:
            ext = f.name.split(".")[-1]
            fn = f"{uuid.uuid4()}.{ext}"
            path = os.path.join(UPLOAD_FOLDER, fn)
            with open(path, "wb") as fo:
                fo.write(f.getbuffer())
            save_f.append(fn)
            orig_f.append(f.name)
        new_row = {
            "唯一ID": str(uuid.uuid4()),
            "记录时间": now,
            "实验名称": exp_name,
            "实验人员": exp_person,
            "实验数据": exp_data,
            "备注": exp_note,
            "保存文件名": ",".join(save_f),
            "原始文件名": ",".join(orig_f)
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        save_records(df)
        st.success("保存成功！")
st.markdown('</div>', unsafe_allow_html=True)

# ====================== 搜索 ======================
st.divider()
search = st.text_input("🔍 搜索")
df = load_records()
if search:
    df_show = df[
        df["实验名称"].str.contains(search, na=False) |
        df["实验人员"].str.contains(search, na=False) |
        df["实验数据"].str.contains(search, na=False) |
        df["备注"].str.contains(search, na=False)
    ]
else:
    df_show = df.copy()

# ====================== 展示记录：修改+删除+附件 ======================
st.markdown("### 📋 我的记录")
if not df_show.empty:
    for _, row in df_show.iterrows():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        col_btn, col_info = st.columns([0.6, 3])
        with col_btn:
            if st.button("✏️ 修改", key=f"e{row['唯一ID']}", use_container_width=True):
                st.session_state["edit_id"] = row["唯一ID"]
            if st.button("🗑️ 删除", key=f"d{row['唯一ID']}", use_container_width=True):
                df = load_records()
                save_records(df[df["唯一ID"] != row["唯一ID"]])
                st.rerun()
        with col_info:
            st.markdown(f"**{row['记录时间']}** | **{row['实验名称']}**")
            st.markdown(f"人员：{row['实验人员']} | 数据：{row['实验数据']}")
            st.markdown(f"备注：{row['备注']}")
            sfs = row["保存文件名"].split(",") if row["保存文件名"] else []
            ofs = row["原始文件名"].split(",") if row["原始文件名"] else []
            for sf, of in zip(sfs, ofs):
                sf = sf.strip()
                of = of.strip()
                fp = os.path.join(UPLOAD_FOLDER, sf)
                if os.path.exists(fp):
                    if fp.lower().endswith(("png", "jpg", "jpeg")):
                        st.image(fp, width=260)
                    with open(fp, "rb") as f:
                        st.download_button(f"下载 {of}", f, file_name=of, key=f"dl{row['唯一ID']}{sf}")
        st.markdown('</div>', unsafe_allow_html=True)
else:
    st.info("暂无记录")

# ====================== 修改记录 ======================
if "edit_id" in st.session_state and st.session_state["edit_id"]:
    eid = st.session_state["edit_id"]
    df = load_records()
    target = df[df["唯一ID"] == eid].iloc[0]
    st.divider()
    st.markdown("### ✏️ 修改记录")
    st.markdown('<div class="card">', unsafe_allow_html=True)
    with st.form("edit_form"):
        c1, c2 = st.columns(2)
        with c1:
            en = st.text_input("实验名称", value=target["实验名称"])
            ep = st.text_input("实验人员", value=target["实验人员"])
        with c2:
            ed = st.text_input("实验数据", value=target["实验数据"])
            eno = st.text_area("备注", value=target["备注"])
        st.caption(f"原附件：{target['原始文件名']}")
        new_files = st.file_uploader("新附件（留空不修改）", accept_multiple_files=True)
        save_btn = st.form_submit_button("💾 保存修改", use_container_width=True)
    if save_btn:
        if new_files:
            ns, no = [], []
            for f in new_files:
                ext = f.name.split(".")[-1]
                fn = f"{uuid.uuid4()}.{ext}"
                pp = os.path.join(UPLOAD_FOLDER, fn)
                with open(pp, "wb") as fo:
                    fo.write(f.getbuffer())
                ns.append(fn)
                no.append(f.name)
            df.loc[df["唯一ID"] == eid, "保存文件名"] = ",".join(ns)
            df.loc[df["唯一ID"] == eid, "原始文件名"] = ",".join(no)
        df.loc[df["唯一ID"] == eid, "实验名称"] = en
        df.loc[df["唯一ID"] == eid, "实验人员"] = ep
        df.loc[df["唯一ID"] == eid, "实验数据"] = ed
        df.loc[df["唯一ID"] == eid, "备注"] = eno
        save_records(df)
        st.success("修改成功！")
        del st.session_state["edit_id"]
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ====================== 导出 ======================
st.divider()
csv_bytes = df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
st.download_button(
    "📥 导出我的记录",
    data=csv_bytes,
    file_name=f"实验记录_{user}_{datetime.now():%Y%m%d}.csv"
)
