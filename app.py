# app.py
import streamlit as st
import pandas as pd
import time
from datetime import datetime
from typing import List, Dict, Any
import os

# 导入自定义模块
from prompts import create_prompt
from api_caller import LLMClient
from utils.file_export import export_pdf  # 导出PDF函数

# ============ 页面配置 ============
st.set_page_config(
    page_title="✨ 营销文案生成助手",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============ 初始化 Session State ============
# 历史记录 CSV 文件路径
HISTORY_CSV = "history.csv"


def load_history() -> pd.DataFrame:
    """从 CSV 加载历史记录，返回 DataFrame"""
    if os.path.exists(HISTORY_CSV):
        df = pd.read_csv(HISTORY_CSV, encoding='utf-8-sig')
        # 确保列存在
        required_cols = ["time", "platform", "style", "topics", "results_json"]
        for col in required_cols:
            if col not in df.columns:
                df[col] = ""
        return df
    else:
        return pd.DataFrame(columns=["time", "platform", "style", "topics", "results_json"])


def save_history(df: pd.DataFrame) -> None:
    """将 DataFrame 保存到 CSV"""
    df.to_csv(HISTORY_CSV, index=False, encoding='utf-8-sig')


# 初始化 session_state
if "history_df" not in st.session_state:
    st.session_state.history_df = load_history()

if "generated_data" not in st.session_state:
    st.session_state.generated_data = {}  # {topic: [文案列表]}


# 缓存 LLM 客户端
@st.cache_resource
def get_llm_client():
    return LLMClient(temperature=0.9)


# ============ 辅助函数：追加历史记录 ============
def append_history_record(platform: str, style: str, topics: List[str], results_dict: Dict[str, List[str]]) -> None:
    """
    将本次生成结果按每条文案拆分为单独的行存入历史 DataFrame
    results_dict: {topic: [文案1, 文案2, ...]}
    """
    new_rows = []
    for topic, texts in results_dict.items():
        for text in texts:
            new_rows.append({
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "platform": platform,
                "style": style,
                "topics": topic,
                "results_json": text  # 存储完整文案
            })
    df = st.session_state.history_df
    new_df = pd.DataFrame(new_rows)
    st.session_state.history_df = pd.concat([df, new_df], ignore_index=True)
    save_history(st.session_state.history_df)


# ============ 侧边栏 ============
with st.sidebar:
    st.header("⚙️ 配置参数")
    platform = st.selectbox(
        "选择平台",
        options=["小红书", "公众号", "抖音"],
        index=0,
        help="不同平台有不同的文案结构和字数要求"
    )
    style = st.radio(
        "选择语气风格",
        options=["专业", "幽默", "亲切"],
        index=2,
        horizontal=True
    )
    count = st.slider(
        "每个主题生成条数",
        min_value=1,
        max_value=10,
        value=3,
        help="每条文案都会独立生成，风格角度不同"
    )

    st.markdown("---")
    st.subheader("📂 历史记录")

    # 显示历史记录开关
    show_history = st.checkbox("显示历史记录")
    if show_history:
        if st.session_state.history_df.empty:
            st.info("暂无历史记录")
        else:
            # 使用 data_editor 展示历史，添加删除列
            df_display = st.session_state.history_df.copy()
            # 添加临时删除列
            df_display["删除"] = False
            edited_df = st.data_editor(
                df_display,
                column_config={
                    "删除": st.column_config.CheckboxColumn("删除", help="勾选后点击下方删除按钮"),
                    "time": "生成时间",
                    "platform": "平台",
                    "style": "风格",
                    "topics": "主题",
                    "results_json": "文案内容（预览）",
                },
                disabled=["time", "platform", "style", "topics", "results_json"],
                hide_index=True,
                use_container_width=True,
                key="history_editor"
            )
            # 删除选中行
            if st.button("🗑️ 删除选中行"):
                new_df = edited_df[edited_df["删除"] == False].drop(columns=["删除"])
                st.session_state.history_df = new_df
                save_history(new_df)
                st.rerun()

            # 按平台筛选
            platforms_available = st.session_state.history_df["platform"].unique().tolist()
            if platforms_available:
                selected_platforms = st.multiselect("按平台筛选", options=platforms_available)
                if selected_platforms:
                    filtered = st.session_state.history_df[
                        st.session_state.history_df["platform"].isin(selected_platforms)
                    ]
                    st.dataframe(filtered[["time", "platform", "style", "topics"]], use_container_width=True)
                else:
                    st.dataframe(st.session_state.history_df[["time", "platform", "style", "topics"]],
                                 use_container_width=True)

    # 清空所有历史
    if st.button("🗑️ 清空所有历史"):
        st.session_state.history_df = pd.DataFrame(columns=["time", "platform", "style", "topics", "results_json"])
        save_history(st.session_state.history_df)
        st.rerun()

# ============ 主区域 ============
st.title("✍️ 营销文案生成助手")
st.caption("输入主题或上传CSV，一键生成多平台、多风格的优质文案")

# ---------- 输入模式 ----------
input_mode = st.radio(
    "选择输入方式",
    options=["单主题生成", "多主题批量生成（逐行输入）", "CSV 文件上传"],
    horizontal=True
)

topics = []  # 最终主题列表

if input_mode == "单主题生成":
    topic = st.text_input("输入产品/主题名称", placeholder="例如：换季敏感肌护肤指南")
    if topic:
        topics = [topic]
elif input_mode == "多主题批量生成（逐行输入）":
    text_area = st.text_area(
        "每行输入一个主题",
        placeholder="例如：\n换季敏感肌护肤\n周末宅家食谱\n打工人效率工具"
    )
    if text_area:
        topics = [line.strip() for line in text_area.split("\n") if line.strip()]
elif input_mode == "CSV 文件上传":
    uploaded_file = st.file_uploader("上传 CSV 文件（必须包含 'topic' 列）", type=["csv"])
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        if "topic" in df.columns:
            topics = df["topic"].dropna().astype(str).tolist()
        else:
            st.error("CSV 文件需要包含 'topic' 列，请检查格式")

# ---------- 生成按钮 ----------
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    generate_btn = st.button("🚀 生成文案", type="primary", use_container_width=True)

if generate_btn:
    if not topics:
        st.warning("请至少输入一个主题")
    else:
        total_topics = len(topics)
        progress_bar = st.progress(0, text="开始生成...")
        status_text = st.empty()
        all_results = {}  # {topic: [文案列表]}
        client = get_llm_client()

        for idx, topic in enumerate(topics):
            status_text.info(f"正在生成第 {idx + 1}/{total_topics} 个主题：{topic}")
            # 构建提示词
            prompt = create_prompt(
                platform=platform,
                style=style,
                topic=topic,
                extra_context="",
                short_mode=False
            )
            try:
                results = client.generate_batch(
                    base_prompt=prompt,
                    count=count,
                    separator="---第"
                )
                # 确保结果是列表
                if isinstance(results, list):
                    all_results[topic] = results
                else:
                    all_results[topic] = [results]
            except Exception as e:
                st.error(f"生成主题「{topic}」时出错: {e}")
                all_results[topic] = [f"生成失败: {e}"]
            # 更新进度
            progress_bar.progress((idx + 1) / total_topics, text=f"已完成 {idx + 1}/{total_topics}")

        status_text.success("✅ 全部生成完成！")
        progress_bar.empty()

        # 保存到 session_state（用于展示）
        st.session_state.generated_data = all_results

        # 保存历史记录（每一条文案独立存储）
        append_history_record(platform, style, topics, all_results)

        # 刷新页面显示结果
        st.rerun()

# ---------- 结果展示 ----------
if st.session_state.generated_data:
    st.markdown("---")
    st.subheader("📝 生成结果")
    results = st.session_state.generated_data

    if len(results) == 1:
        # 单个主题
        topic, result_list = list(results.items())[0]
        st.caption(f"主题：{topic} ｜ 共 {len(result_list)} 条文案")
        for i, text in enumerate(result_list):
            with st.expander(f"📌 文案 {i + 1}"):
                st.text_area(f"文案 {i + 1}", text, height=200, key=f"result_{topic}_{i}")
                st.button(f"📋 复制", key=f"copy_{topic}_{i}",
                          on_click=lambda t=text: st.write(f"已复制：{t[:50]}..."))  # 简化复制
    else:
        # 多个主题，使用 tabs
        tab_names = list(results.keys())
        tabs = st.tabs(tab_names)
        for tab, topic in zip(tabs, tab_names):
            with tab:
                st.caption(f"共 {len(results[topic])} 条文案")
                for i, text in enumerate(results[topic]):
                    with st.expander(f"📌 文案 {i + 1}"):
                        st.text_area(f"文案 {i + 1}", text, height=200, key=f"result_{topic}_{i}")
                        st.button(f"📋 复制", key=f"copy_{topic}_{i}")

    # ---------- 导出按钮 ----------
    # 构建导出内容：全部文案拼接为一个列表（每个元素是一行，用于PDF/TXT）
    export_lines = []
    for topic, texts in results.items():
        export_lines.append(f"【{topic}】")
        for i, txt in enumerate(texts, 1):
            export_lines.append(f"--- 第{i}条 ---")
            export_lines.append(txt)
            export_lines.append("")  # 空行分隔
    combined_text = "\n".join(export_lines)

    col_export1, col_export2 = st.columns(2)
    with col_export1:
        st.download_button(
            label="📄 导出 TXT",
            data=combined_text.encode("utf-8"),
            file_name=f"文案_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
            use_container_width=True
        )
    with col_export2:
        try:
            pdf_bytes = export_pdf(export_lines)  # 传入列表
            st.download_button(
                label="📕 导出 PDF",
                data=pdf_bytes,
                file_name=f"文案_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"PDF 导出失败: {e}")

# ============ 页脚 ============
st.markdown("---")
st.caption("Powered by DeepSeek · 文案生成助手 v1.0")