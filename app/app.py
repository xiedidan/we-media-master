import streamlit as st
import yaml
import sys
import os

sys.path.insert(0, ".")
from skills.searchng.search import search as search_skill
from agent.prompts import get_system_prompt, build_user_prompt


def load_config() -> dict:
    config_path = "config/settings.yml"
    try:
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        return {"app": {"title": "自媒体文章创作大师"}}


def main():
    st.set_page_config(
        page_title="自媒体文章创作大师",
        page_icon="✍️",
        layout="wide",
    )
    
    config = load_config()
    app_config = config.get("app", {})
    st.title(app_config.get("title", "自媒体文章创作大师"))
    
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
        length_map = {"short": 1500, "medium": 3000, "long": 5000}
        
        style = st.selectbox(
            "文风",
            options=["professional", "friendly", "popular"],
            index=0,
        )
        
        generate_btn = st.button("生成文章", type="primary")
    
    with col2:
        st.subheader("📄 文章输出")
        
        if generate_btn and topic:
            with st.spinner("正在搜索素材..."):
                kw_list = [k.strip() for k in keywords.split(",")] if keywords else []
                materials = search_skill(" ".join(kw_list) if kw_list else topic, num_results=5)
            
            with st.spinner("正在生成文章..."):
                user_prompt = build_user_prompt(
                    topic=topic,
                    keywords=kw_list,
                    materials=materials,
                    length=length,
                    style=style,
                )
                system_prompt = get_system_prompt()
                
                article = f"# {topic}\n\n"
                article += f"**关键词**: {', '.join(kw_list)}\n\n"
                article += "**素材参考**:\n"
                for m in materials:
                    article += f"- [{m['title']}]({m['url']})\n"
                article += "\n---\n\n"
                article += "（此处为占位符，实际调用LLM生成完整文章）\n"
            
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