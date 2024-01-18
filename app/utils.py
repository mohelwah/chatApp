


def get_prompt_template(type: str, name: str) -> Optional[str]:
    """
    从prompt_config中加载模板内容
    type: "llm_chat","agent_chat","knowledge_base_chat","search_engine_chat"的其中一种，如果有新功能，应该进行加入。
    """

    from configs import prompt_config
    import importlib

    importlib.reload(prompt_config)  # TODO: 检查configs/prompt_config.py文件有修改再重新加载
    return prompt_config.PROMPT_TEMPLATES[type].get(name)
