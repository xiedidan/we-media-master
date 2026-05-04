import streamlit as st
import yaml
import sys
import os
import subprocess

sys.path.insert(0, ".")
from skills.searchng.search import search as search_skill
from agent.prompts import get_system_prompt, build_user_prompt
from services.llm import call_llm, DEFAULT_SYSTEM_PROMPT


def load_config() -> dict:
    config_path = "config/settings.yml"
    try:
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        return {"app": {"title": "自媒体文章创作大师"}}


def load_api_key() -> str:
    config = load_config()
    return config.get("llm", {}).get("api_key", "")


def save_api_key(api_key: str):
    config = load_config()
    if "llm" not in config:
        config["llm"] = {}
    config["llm"]["api_key"] = api_key
    with open("config/settings.yml", "w") as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False)


def main():
    st.set_page_config(
        page_title="自媒体文章创作大师",
        page_icon="✍️",
        layout="wide",
    )
    
    config = load_config()
    app_config = config.get("app", {})
    st.title(app_config.get("title", "自媒体文章创作大师"))
    
    with st.sidebar:
        st.header("⚙️ 配置")
        
        api_key = st.text_input(
            "DeepSeek API Key",
            type="password",
            value=load_api_key(),
            help="在DeepSeek开放平台获取API Key"
        )
        
        if st.button("保存API Key"):
            save_api_key(api_key)
            st.success("已保存！")
            st.rerun()
        
        st.divider()
        
        current_provider = config.get("llm", {}).get("provider", "deepseek")
        current_model = config.get("llm", {}).get("model", "deepseek-v4-pro")
        st.caption(f"当前模型: {current_provider}/{current_model}")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("📝 输入")
        
        topic = st.text_input("主题", placeholder="例如：人工智能")
        
        keywords = st.text_input("关键词", placeholder="用逗号分隔")
        
        length = st.select_slider(
            "文章长度",
            options=["short", "medium", "long"],
            value="medium",
        )
        
        style = st.selectbox(
            "文风",
            options=["professional", "friendly", "popular"],
            index=0,
        )
        
        generate_btn = st.button("生成文章", type="primary")
    
    with col2:
        st.subheader("📄 文章输出")
        
        if generate_btn and topic:
            api_key = load_api_key()
            
            if not api_key:
                st.error("请先在左侧配置DeepSeek API Key")
                return
            
            with st.spinner("正在搜索素材..."):
                kw_list = [k.strip() for k in keywords.split(",")] if keywords else []
                materials = search_skill(" ".join(kw_list) if kw_list else topic, num_results=5)
            
            with st.spinner("正在生成文章（可能需要1-2分钟）..."):
                user_prompt = build_user_prompt(
                    topic=topic,
                    keywords=kw_list,
                    materials=materials,
                    length=length,
                    style=style,
                )
                
                article = call_llm(user_prompt, DEFAULT_SYSTEM_PROMPT, api_key)
            
            st.text_area("文章内容", value=article, height=600)
            
            st.download_button(
                "下载Markdown",
                data=article,
                file_name=f"{topic}.md",
                mime="text/markdown",
            )
        else:
            st.info("请输入主题，点击「生成文章」开始创作")


if __name__ == "__main__":
    main()