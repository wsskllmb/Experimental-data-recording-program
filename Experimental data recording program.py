import streamlit as st
import pandas as pd
from datetime import datetime
import os
import uuid

# ====================== 页面配置 + 科技感CSS ======================
st.set_page_config(page_title="实验记录系统", layout="wide")

st.markdown("""
<style>
.stApp {
    background: #0b1020;
    color: #e0e0e0;
}
.main-title {
    font-size: 28px;
    font-weight: bold;
    color: #0cf;
    text-shadow: 0 0 10px #0cf, 0 0 20px #0cf;
    margin-bottom: 20px;
}
.card {
    background: #121a33;
    border: 1px solid #253466;
    border-radius: 12px;
    padding: 22px;
    margin-bottom: 18px;
    box-shadow: 0 0 15px rgba(0,200,255,0.1);
}
.stTextInput>div>div, .stTextArea>div>div, .stFileUploader>div {
    background: #162040 !important;
    border-color: #354980 !important;
    color: #e0e0e0 !important;
    border-radius: 8px;
}
.stButton>button {
    border-radius: 8px;
    background: linear-gradient(90deg, #0088ff, #00ccff);
    color: #fff;
    font-weight: bold;
    border: none;
    box-shadow: 0 0 10px rgba(0,150,255,0.3);
}
.stButton>button:hover {
    box-shadow: 0 0 16px rgba(0,180,255,0.6);
}
hr {
    border-color: #253466;
}
</style>
""", unsafe_allow_html=True)

# ====================== 初始化 ======================
if not os.path.exists("upload_files"):
    os.makedirs("upload_files")

if not os.path.exists("users.csv"):
    pd.DataFrame(columns=["username","password"]).to_csv("users.csv", index=False, encoding="utf-8-sig")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None

# ====================== 注册 ======================
def register_user(username, password):
    users = pd.read_csv("users.csv", encoding="utf-8-sig")
    if username in users["username"].values:
        return False
    users = pd.concat([users, pd.DataFrame({"username":[username],"password":[password]})], ignore_index=True)
    users.to_csv("users.csv", index=False, encoding="utf-8-sig")
    return True

# ====================== 登录 ======================
def check_login(username, password):
    users = pd.read_csv("users.csv", encoding="utf-8-sig")
    return not users[(users["username"]==username) & (users["password"]==password)].empty

# ====================== 未登录 ======================
if not st.session_state.logged_in:
    st.markdown('<div class="main-title">🔬 实验记录管理系统</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🔑 登录", "📝 注册"])
    with tab1:
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            username = st.text_input("用户名")
            pwd = st.text_input("密码", type="password")
            if st.button("登录", use_container_width=True):
                if check_login(username, pwd):
                    st.session_state.logged_in = True
                    st.session_state.current_user = username
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
                    st.error("用户名和密码不能为空")
                elif register_user(new_u, new_p):
                    st.success("注册成功！请登录")
                else:
                    st.error("用户名已存在")
            st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ====================== 已登录 ======================
user = st.session_state.current_user
csv_file = f"experiment_records_{user}.csv"

c1, c2 = st.columns([10,1])
with c1:
    st.markdown(f'<div class="main-title">🧪 实验记录控制台 | 欢迎 {user}</div>', unsafe_allow_html=True)
with c2:
    if st.button("退出"):
        st.session_state.logged_in = False
        st.rerun()

# ====================== 数据 ======================
def load_data():
    try:
        df = pd.read_csv(csv_file, encoding="utf-8-sig")
    except FileNotFoundError:
        df = pd.DataFrame(columns=["唯一ID","记录时间","实验名称","实验人员","实验数据","备注","保存文件名","原始文件名"])
    for c in df.columns:
        df[c] = df[c].astype(str).fillna("")
    return df

def save_data(df):
    df.to_csv(csv_file, index=False, encoding="utf-8-sig")

# ====================== 新增记录 ======================
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown("### 📝 新增实验记录")
with st.form("add", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("实验名称")
        person = st.text_input("实验人员")
    with col2:
        data = st.text_input("实验数据")
        note = st.text_area("备注", height=80)
    files = st.file_uploader("上传附件", accept_multiple_files=True, type=["png","jpg","jpeg","pdf","docx","xlsx","txt"])
    sub = st.form_submit_button("✅ 保存记录", use_container_width=True)

if sub:
    if not name or not person:
        st.error("实验名称和人员不能为空")
    else:
        df = load_data()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sf, of = [], []
        for f in files:
            ext = f.name.split(".")[-1]
            fn = f"{uuid.uuid4()}.{ext}"
            pp = os.path.join("upload_files", fn)
            with open(pp, "wb") as fo:
                fo.write(f.getbuffer())
            sf.append(fn)
            of.append(f.name)
        row = {
            "唯一ID": str(uuid.uuid4()),
            "记录时间": now,
            "实验名称": name,
            "实验人员": person,
            "实验数据": data,
            "备注": note,
            "保存文件名": ",".join(sf),
            "原始文件名": ",".join(of)
        }
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
        save_data(df)
        st.success("保存成功！")
st.markdown('</div>', unsafe_allow_html=True)

# ====================== 筛选 ======================
st.divider()
st.markdown("### 🔍 搜索记录")
search = st.text_input("搜索关键词")
df = load_data()
if search:
    df_show = df[
        df["实验名称"].str.contains(search, na=False) |
        df["实验人员"].str.contains(search, na=False) |
        df["实验数据"].str.contains(search, na=False) |
        df["备注"].str.contains(search, na=False)
    ]
else:
    df_show = df.copy()

# ====================== 展示 ======================
st.markdown("### 📋 实验记录列表")
if not df_show.empty:
    for _, row in df_show.iterrows():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        cb, ci = st.columns([0.6, 3])
        with cb:
            if st.button("✏️ 修改", key=f"e{row['唯一ID']}", use_container_width=True):
                st.session_state["edit_id"] = row["唯一ID"]
            if st.button("🗑️ 删除", key=f"d{row['唯一ID']}", use_container_width=True):
                d = load_data()
                save_data(d[d["唯一ID"]!=row["唯一ID"]])
                st.rerun()
        with ci:
            st.markdown(f"**{row['记录时间']}** | **{row['实验名称']}**")
            st.markdown(f"人员：{row['实验人员']} | 数据：{row['实验数据']}")
            st.markdown(f"备注：{row['备注']}")
            
            sfs = row["保存文件名"].split(",") if row["保存文件名"] else []
            ofs = row["原始文件名"].split(",") if row["原始文件名"] else []
            for sf, of in zip(sfs, ofs):
                sf = sf.strip()
                of = of.strip()
                fp = os.path.join("upload_files", sf)
                if os.path.exists(fp):
                    if fp.lower().endswith(("png","jpg","jpeg")):
                        st.image(fp, width=260)
                    with open(fp, "rb") as f:
                        st.download_button(f"下载 {of}", f, file_name=of, key=f"dl{row['唯一ID']}{sf}")
        st.markdown('</div>', unsafe_allow_html=True)
else:
    st.info("暂无记录")

# ====================== 修改 ======================
if "edit_id" in st.session_state and st.session_state["edit_id"]:
    eid = st.session_state["edit_id"]
    df = load_data()
    tg = df[df["唯一ID"]==eid].iloc[0]
    st.divider()
    st.markdown("### ✏️ 修改记录")
    st.markdown('<div class="card">', unsafe_allow_html=True)
    with st.form("edit"):
        c1, c2 = st.columns(2)
        with c1:
            en = st.text_input("实验名称", value=tg["实验名称"])
            ep = st.text_input("实验人员", value=tg["实验人员"])
        with c2:
            ed = st.text_input("实验数据", value=tg["实验数据"])
            eno = st.text_area("备注", value=tg["备注"])
        st.caption(f"原附件：{tg['原始文件名']}")
        nfs = st.file_uploader("上传新附件（留空不修改）", accept_multiple_files=True)
        sav = st.form_submit_button("💾 保存修改", use_container_width=True)

    if sav:
        if nfs:
            ns, no = [], []
            for f in nfs:
                ext = f.name.split(".")[-1]
                fn = f"{uuid.uuid4()}.{ext}"
                pp = os.path.join("upload_files", fn)
                with open(pp, "wb") as fo:
                    fo.write(f.getbuffer())
                ns.append(fn)
                no.append(f.name)
            df.loc[df["唯一ID"]==eid, "保存文件名"] = ",".join(ns)
            df.loc[df["唯一ID"]==eid, "原始文件名"] = ",".join(no)

        df.loc[df["唯一ID"]==eid, "实验名称"] = en
        df.loc[df["唯一ID"]==eid, "实验人员"] = ep
        df.loc[df["唯一ID"]==eid, "实验数据"] = ed
        df.loc[df["唯一ID"]==eid, "备注"] = eno
        save_data(df)
        st.success("修改成功！")
        del st.session_state["edit_id"]
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ====================== 导出 ======================
st.divider()
csv_bytes = df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
st.download_button(
    "📥 导出我的实验记录",
    data=csv_bytes,
    file_name=f"实验记录_{user}_{datetime.now():%Y%m%d}.csv",
    mime="text/csv"
)
