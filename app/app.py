import streamlit as st
import yaml
import sys
import os
import subprocess
from urllib.request import urlopen
from bs4 import BeautifulSoup

sys.path.insert(0, ".")
from skills.searchng.search import search as search_skill
from agent.prompts import get_system_prompt, build_user_prompt
from services.llm import call_llm, DEFAULT_SYSTEM_PROMPT, validate_api_key
from utils.logger import save_execution_log, list_logs


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


def get_model_config() -> dict:
    config = load_config()
    return config.get("llm", {})


def save_api_key(api_key: str, provider: str = "deepseek", model: str = "deepseek-v4-flash", thinking: bool = False):
    config = load_config()
    if "llm" not in config:
        config["llm"] = {}
    config["llm"]["api_key"] = api_key
    config["llm"]["provider"] = provider
    config["llm"]["model"] = model
    config["llm"]["thinking"] = thinking
    
    if provider == "deepseek":
        config["llm"]["base_url"] = "https://api.deepseek.com"
    elif provider == "openai":
        config["llm"]["base_url"] = "https://api.openai.com/v1"
    
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
    
    llm_config = get_model_config()
    current_api_key = llm_config.get("api_key", "")
    current_provider = llm_config.get("provider", "deepseek")
    current_model = llm_config.get("model", "deepseek-v4-flash")
    current_thinking = llm_config.get("thinking", False)
    
    with st.sidebar:
        st.header("⚙️ 配置")
        
        # Step 1: Select provider
        model_config = get_model_config()
        available_models = model_config.get("models", [
            {"name": "deepseek-v4-flash", "provider": "deepseek", "label": "DeepSeek V4 Flash"},
            {"name": "deepseek-v4-pro", "provider": "deepseek", "label": "DeepSeek V4 Pro"},
        ])
        
        # Group models by provider
        providers = list(set(m["provider"] for m in available_models))
        
        current_provider = model_config.get("provider", "deepseek")
        provider_idx = providers.index(current_provider) if current_provider in providers else 0
        
        selected_provider = st.selectbox(
            "选择供应商",
            options=providers,
            index=provider_idx,
        )
        
# Step 2: Select model for the chosen provider
        provider_models = [m for m in available_models if m["provider"] == selected_provider]
        
        if not provider_models:
            st.warning("该供应商暂无可用模型")
            return
        
        model_options = [m["name"] for m in provider_models]
        model_labels = [m["label"] for m in provider_models]
        
        current_model = model_config.get("model", "deepseek-v4-flash")
        model_idx = model_options.index(current_model) if current_model in model_options else 0
        
        selected_model = st.selectbox(
            "选择模型版本",
            options=model_options,
            format_func=lambda m: model_labels[model_options.index(m)] if m in model_options else m,
            index=model_idx,
        )
        
        # Step 3: Thinking mode (DeepSeek only)
        if selected_provider == "deepseek":
            current_thinking = model_config.get("thinking", False)
            thinking_enabled = st.checkbox("启用深度思考(Thinking)", value=current_thinking)
        else:
            thinking_enabled = False
        
        # Step 4: API Key
        api_key = st.text_input(
            "API Key",
            type="password",
            value=load_api_key(),
            help=f"在{selected_provider}开放平台获取API Key"
        )
        
        if st.button("保存配置"):
            if api_key:
                with st.spinner("验证API Key..."):
                    result = validate_api_key(api_key, selected_provider, selected_model)
                    if result.get("valid"):
                        save_api_key(api_key, selected_provider, selected_model, thinking_enabled)
                        st.success(f"API Key验证成功！")
                    else:
                        st.error(f"API Key无效: {result.get('error', '未知错误')}")
            st.rerun()
        
        st.divider()
        
        thinking_status = model_config.get("thinking", False)
        st.caption(f"当前: {selected_provider}/{selected_model} {'(深度思考)' if thinking_status else ''}")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("📝 输入")
        
        topic = st.text_input("主题", placeholder="例如：人工智能")
        
        central_idea = st.text_area("中心思想", placeholder="文章想要表达的核心观点是什么？例如：真正的成长来自于走出舒适区的勇气", height=80)
        
        keywords = st.text_input("关键词", placeholder="用逗号分隔")
        
        st.markdown("---")
        st.markdown("**🔍 搜索设置**")
        
        search_num = st.slider("搜索篇数", min_value=3, max_value=10, value=5, help="选择搜索多少条素材")
        search_keywords = st.text_input("自定义搜索关键词", placeholder="可选，覆写默认搜索词", help="留空则使用上面的关键词")
        
        st.markdown("---")
        st.markdown("**📎 参考材料（可选）**")
        
        uploaded_files = st.file_uploader("上传参考文件", type=["txt", "md"], accept_multiple_files=True, help="支持.txt和.md文件")
        
        ref_url = st.text_input("参考链接", placeholder="https://example.com/article", help="输入URL，Agent会自动获取内容")
        
        st.markdown("---")
        st.markdown("**📚 范文参考（可选）**")
        
        example_article = st.text_area("范文内容", placeholder="粘贴一篇你喜欢的文章，Agent会学习其风格", height=100)
        
        length_options = ["短文(1500字)", "中篇(3000字)", "长篇(5000字)"]
        length_map = {
            "短文(1500字)": "short",
            "中篇(3000字)": "medium",
            "长篇(5000字)": "long",
        }
        
        style_options = ["专业严谨", "亲切友好", "通俗易懂"]
        style_map = {
            "专业严谨": "professional",
            "亲切友好": "friendly",
            "通俗易懂": "popular",
        }
        
        current_style = model_config.get("style", "professional")
        style_idx = 0
        for i, (k, v) in enumerate(style_map.items()):
            if v == current_style:
                style_idx = i
                break
        
        length = st.select_slider(
            "文章长度",
            options=length_options,
            value="中篇(3000字)",
        )
        
        style = st.selectbox(
            "文风",
            options=style_options,
            index=style_idx,
        )
        style = style_map[style]
        
        article_type = st.selectbox(
            "文章类型",
            options=["知识普及", "经验分享", "感悟体会", "想法迸发"],
            index=0,
        )
        
        generate_btn = st.button("生成文章", type="primary")
    
    with col2:
        st.subheader("📄 文章输出")
        
        if generate_btn and topic:
            api_key = current_api_key
            provider = current_provider
            model = current_model
            
            if not api_key:
                st.error("请先在左侧配置API Key")
                return
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("🔍 步骤1/3: 搜索素材中...")
            progress_bar.progress(5)
            
            search_kw = search_keywords.strip() if search_keywords else (", ".join([k.strip() for k in keywords.split(",")]) if keywords else topic)
            materials = search_skill(search_kw, num_results=search_num)
            progress_bar.progress(20)
            
            status_text.text("📄 步骤2/3: 处理参考材料...")
            progress_bar.progress(30)
            
            if uploaded_files:
                for uploaded_file in uploaded_files:
                    content = uploaded_file.getvalue().decode("utf-8")
                    materials.append({
                        "title": f"[上传] {uploaded_file.name}",
                        "content": content[:500] if len(content) > 500 else content,
                        "url": "",
                    })
            
            if ref_url:
                try:
                    with urlopen(ref_url, timeout=10) as response:
                        html = response.read().decode("utf-8")
                        soup = BeautifulSoup(html, "html.parser")
                        text = soup.get_text()[:1000]
                        materials.append({
                            "title": f"[链接] {ref_url[:50]}...",
                            "content": text,
                            "url": ref_url,
                        })
                except Exception as e:
                    st.warning(f"获取链接失败: {e}")
            
            example_text = ""
            if example_article:
                example_text = f"\n\n参考范文风格：\n{example_article}"
                materials.append({
                    "title": "[范文] 用户提供",
                    "content": example_article[:500],
                    "url": "",
                })
            
            progress_bar.progress(50)
            
            st.info(f"共 {len(materials)} 条素材")
            
            selected_indices = list(range(len(materials)))
            if len(materials) > 1:
                st.markdown("**选择要使用的素材：**")
                selected_indices = []
                for i, m in enumerate(materials):
                    selected = st.checkbox(
                        f"{i+1}. {m.get('title', '素材')[:60]}",
                        value=True,
                        key=f"material_{i}",
                    )
                    if selected:
                        selected_indices.append(i)
            
            selected_materials = [materials[i] for i in selected_indices]
            
            if not selected_materials:
                st.error("请至少选择一条素材")
                return
            
            status_text.text("✍️ 步骤3/3: 生成文章中...")
            progress_bar.progress(60)
            
            user_prompt = build_user_prompt(
                topic=topic,
                keywords=[k.strip() for k in keywords.split(",")] if keywords else [],
                materials=selected_materials,
                length=length_map.get(length, "medium"),
                style=style,
                article_type=article_type,
                central_idea=central_idea,
            )
            
            if example_text:
                user_prompt += example_text
            
            article = call_llm(user_prompt, DEFAULT_SYSTEM_PROMPT, api_key)
            progress_bar.progress(100)
            status_text.text("✅ 生成完成!")
            
            save_execution_log(
                topic=topic,
                keywords=kw_list,
                article=article,
                article_type=article_type,
                style=style,
                length=length_map.get(length, "medium"),
                material_count=len(materials),
                provider=current_provider,
                model=current_model,
                thinking=current_thinking,
                materials=materials,
            )
            
            st.text_area("文章内容", value=article, height=600)
            
            st.download_button(
                "下载Markdown",
                data=article,
                file_name=f"{topic}.md",
                mime="text/markdown",
            )
        else:
            st.info("请输入主题，点击「生成文章」开始创作")
        
        st.divider()
        st.subheader("📋 执行历史")
        logs = list_logs(5)
        if logs:
            for log in logs:
                with st.expander(f"{log.get('topic', 'unknown')} - {log.get('timestamp', '')}"):
                    st.caption(f"类型: {log.get('article_type')} | 文风: {log.get('style')} | 字数: {log.get('article_length', 0)}")
                    if log.get('score'):
                        st.caption(f"评分: {log['score'].get('总分', 'N/A')}分")
        else:
            st.caption("暂无执行记录")


if __name__ == "__main__":
    main()