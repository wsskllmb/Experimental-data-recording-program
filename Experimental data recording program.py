import streamlit as st
import pandas as pd
from datetime import datetime
import os
import uuid

# 初始化文件夹
if not os.path.exists("upload_files"):
    os.makedirs("upload_files")

# 页面设置
st.set_page_config(page_title="实验记录系统", layout="wide")
st.title("🧪 实验数据记录系统")

# 数据读取
def load_data():
    try:
        df = pd.read_csv("experiment_records.csv", encoding="utf-8-sig")
    except FileNotFoundError:
        df = pd.DataFrame(columns=[
            "唯一ID", "记录时间", "实验名称", "实验人员", "实验数据", "备注", "保存文件名", "原始文件名"
        ])
    required = ["唯一ID", "记录时间", "实验名称", "实验人员", "实验数据", "备注", "保存文件名", "原始文件名"]
    for col in required:
        if col not in df.columns:
            df[col] = ""
    return df

# 保存数据
def save_data(df):
    df.to_csv("experiment_records.csv", index=False, encoding="utf-8-sig")

# 新增记录
with st.expander("📝 新增实验记录", expanded=True):
    with st.form("experiment_form"):
        col1, col2 = st.columns(2)
        with col1:
            experiment_name = st.text_input("实验名称")
            experimenter = st.text_input("实验人员")
        with col2:
            data_value = st.text_input("实验数据")
            notes = st.text_area("备注")
        uploaded_files = st.file_uploader(
            "上传多个文件/图片",
            type=["png", "jpg", "jpeg", "pdf", "docx", "xlsx", "txt"],
            accept_multiple_files=True
        )
        submit = st.form_submit_button("✅ 保存记录")

if submit:
    if not experiment_name or not experimenter:
        st.error("请填写实验名称和实验人员！")
    else:
        df = load_data()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_names = []
        orig_names = []
        for file in uploaded_files:
            if file:
                ext = file.name.split(".")[-1]
                save_name = str(uuid.uuid4()) + "." + ext
                save_path = os.path.join("upload_files", save_name)
                with open(save_path, "wb") as f:
                    f.write(file.getbuffer())
                save_names.append(save_name)
                orig_names.append(file.name)
        new_row = {
            "唯一ID": str(uuid.uuid4()),
            "记录时间": current_time,
            "实验名称": experiment_name,
            "实验人员": experimenter,
            "实验数据": data_value,
            "备注": notes,
            "保存文件名": ",".join(save_names),
            "原始文件名": ",".join(orig_names)
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        save_data(df)
        st.success("保存成功！")

# 筛选
st.divider()
st.subheader("🔍 筛选记录")
df = load_data()
search = st.text_input("搜索关键词")
if search:
    df_show = df[
        df["实验名称"].str.contains(search, na=False) |
        df["实验人员"].str.contains(search, na=False) |
        df["实验数据"].str.contains(search, na=False) |
        df["备注"].str.contains(search, na=False)
    ]
else:
    df_show = df.copy()

# 展示记录
st.subheader("📋 全部记录")
if not df_show.empty:
    for idx, row in df_show.iterrows():
        with st.container():
            col_del, col_info = st.columns([0.1, 2.9])
            with col_del:
                if st.button("🗑️", key=row["唯一ID"]):
                    df = load_data()
                    df = df[df["唯一ID"] != row["唯一ID"]]
                    save_data(df)
                    st.rerun()
            with col_info:
                # 🔥 修复空值报错
                time_str = str(row.get("记录时间", ""))
                name_str = str(row.get("实验名称", ""))
                st.write(f"**{time_str}** | **{name_str}**")

                experimenter_str = str(row.get("实验人员", ""))
                data_str = str(row.get("实验数据", ""))
                st.write(f"人员: {experimenter_str} | 数据: {data_str}")

                note_str = str(row.get("备注", ""))
                st.write(f"备注: {note_str}")

                save_files = str(row["保存文件名"]).split(",") if pd.notna(row["保存文件名"]) else []
                orig_files = str(row["原始文件名"]).split(",") if pd.notna(row["原始文件名"]) else []
                if save_files and save_files[0]:
                    st.write("📎 附件：")
                    for save_fn, orig_fn in zip(save_files, orig_files):
                        save_fn = save_fn.strip()
                        orig_fn = orig_fn.strip()
                        fp = os.path.join("upload_files", save_fn)
                        if os.path.exists(fp):
                            if fp.endswith(("png", "jpg", "jpeg")):
                                st.image(fp, width=300)
                            with open(fp, "rb") as f:
                                st.download_button(
                                    label="📂 下载 " + orig_fn,
                                    data=f,
                                    file_name=orig_fn,
                                    key="dl_" + row['唯一ID'] + "_" + save_fn
                                )
            st.divider()
else:
    st.info("暂无记录")

# 导出CSV
csv_data = df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
st.download_button(
    "📥 导出全部记录",
    data=csv_data,
    file_name="实验记录_" + datetime.now().strftime("%Y%m%d") + ".csv",
    mime="text/csv"
)
