import streamlit as st
from app.webui_pages.utils import *
from streamlit_chatbox import *
from streamlit_modal import Modal
from datetime import datetime
import os
import re
import time
from app.configs import LLM_MODELS, PROMPT_TEMPLATES

from app.configs.model_config import HISTORY_LEN

# from server.knowledge_base.utils import LOADER_DICT
import uuid
from typing import List, Dict

chat_box = ChatBox()


def check_error_msg(data: Union[str, dict, list], key: str = "errorMsg") -> str:
    """
    return error message if error occured when requests API
    """
    if isinstance(data, dict):
        if key in data:
            return data[key]
        if "code" in data and data["code"] != 200:
            return data["msg"]
    return ""


def get_messages_history(
    history_len: int, content_in_expander: bool = False
) -> List[Dict]:
    """
    Return message history.
    content_in_expander controls whether to return the content in the expander element. Generally, it can be selected when exporting. It is not required for the history passed into LLM.
    """

    def filter(msg):
        content = [
            x for x in msg["elements"] if x._output_method in ["markdown", "text"]
        ]
        if not content_in_expander:
            content = [x for x in content if not x._in_expander]
        content = [x.content for x in content]

        return {
            "role": msg["role"],
            "content": "\n\n".join(content),
        }


def parse_command(text: str, modal: Modal) -> bool:
    """
    Check whether the user has entered a custom command. Currently supported:
    /new {session_name}. If no name is provided, defaults to "Session X"
    /del {session_name}. If no name is provided, delete the current session if the number of sessions > 1.
    /clear {session_name}. If no name is provided, defaults to clearing the current session
    /help. View command help
    Return value: If the command is entered, it returns True, otherwise it returns False.
    """
    if m := re.match(r"/([^\s]+)\s*(.*)", text):
        cmd, name = m.groups()
        name = name.strip()
        conv_names = chat_box.get_chat_names()
        if cmd == "help":
            modal.open()
        elif cmd == "new":
            if not name:
                i = 1
                while True:
                    name = f"session{i}"
                    if name not in conv_names:
                        break
                    i += 1
            if name in st.session_state["conversation_ids"]:
                st.error(f"The session name '{name}' already exists")
                time.sleep(1)
            else:
                st.session_state["conversation_ids"][name] = uuid.uuid4().hex
                st.session_state["cur_conv_name"] = name
        elif cmd == "del":
            name = name or st.session_state.get("cur_conv_name")
            if len(conv_names) == 1:
                st.error("This is the last session and cannot be deleted")
                time.sleep(1)
            elif not name or name not in st.session_state["conversation_ids"]:
                st.error(f"Invalid session name: “{name}”")
                time.sleep(1)
            else:
                st.session_state["conversation_ids"].pop(name, None)
                chat_box.del_chat_name(name)
                st.session_state["cur_conv_name"] = ""
        elif cmd == "clear":
            chat_box.reset_history(name=name or None)
        return True
    return False


def dialogue_page(api: ApiRequest, is_lite: bool = False):
    st.session_state.setdefault("conversation_ids", {})
    st.session_state["conversation_ids"].setdefault(
        chat_box.cur_chat_name, uuid.uuid4().hex
    )
    st.session_state.setdefault("file_chat_id", None)
    default_model = LLM_MODELS[0]

    if not chat_box.chat_inited:
        st.toast(
            f"Welcome to  [`Chatapp`](https://github.com/chatchat-space/Chatapp) ! \n\n"
            f"The currently running model `{default_model}`, You can start asking questions."
        )
        chat_box.init_session()

    modal = Modal(" Custom command", key="cmd_help", max_width="500")
    if modal.is_open():
        with modal.container():
            cmds = [
                x
                for x in parse_command.__doc__.split("\n")
                if x.strip().startswith("/")
            ]
            st.write("\n\n".join(cmds))

    with st.sidebar:
        conv_names = list(st.session_state["conversation_ids"].keys())
        index = 0
        if st.session_state.get("cur_conv_name") in conv_names:
            index = conv_names.index(st.session_state.get("cur_conv_name"))
        conversation_name = st.selectbox("Current session:", conv_names, index=index)
        chat_box.use_chat_name(conversation_name)
        conversation_id = st.session_state["conversation_ids"][conversation_name]

        # TODO: Dialogue model and session binding
        def on_mode_change():
            mode = st.session_state.dialogue_mode
            text = f"Switched to {mode}."
            if mode == "Knowledge Base Q&A":
                cur_kb = st.session_state.get("selected_kb")
                if cur_kb:
                    text = f"{text} Current knowledge base: `{cur_kb}`。"
            st.toast(text)

        dialogue_modes = [
            "LLM Conversation",
        ]
        dialogue_mode = st.selectbox(
            "Please select conversation mode:",
            dialogue_modes,
            index=0,
            on_change=on_mode_change,
            key="dialogue_mode",
        )

        running_models = LLM_MODELS

        def on_llm_change():
            if llm_model:
                st.session_state["cur_llm_model"] = st.session_state.llm_model

        def llm_model_format_func(x):
            if x in running_models:
                return f"{x} (Running)"
            return x

        llm_models = LLM_MODELS

   
        llm_model = st.selectbox(
            "Select LLM model:",
            llm_models,
            index,
            format_func=llm_model_format_func,
            on_change=on_llm_change,
            key="llm_model",
        )
        """
        index_prompt = {
            "llm_chat": "LLM chat",
        }
        prompt_templates_kb_list = list(
            PROMPT_TEMPLATES[index_prompt[dialogue_mode]].keys()
        )
        prompt_template_name = prompt_templates_kb_list[0]
        if "prompt_template_select" not in st.session_state:
            st.session_state.prompt_template_select = prompt_templates_kb_list[0]

        def prompt_change():
            text = f"Switched to {prompt_template_name} template."
            st.toast(text)

        prompt_template_select = st.selectbox(
            "Please select a prompt template:",
            prompt_templates_kb_list,
            index=0,
            on_change=prompt_change,
            key="prompt_template_select",
        )

        prompt_template_name = st.session_state.prompt_template_select
        """
        prompt_template_name = PROMPT_TEMPLATES["llm_chat"]["default"]
        #prompt_template_name = st.session_state.prompt_template_select

        temperature = st.slider("Temperature：", 0.0, 1.0, TEMPERATURE, 0.05)
        history_len = st.number_input(
            "Number of historical dialogue rounds:", 0, 20, HISTORY_LEN
        )

    # Display chat messages from history on app rerun
    chat_box.output_messages()

    chat_input_placeholder = "Please enter the conversation content and use Shift+Enter for line breaks. Enter /help to view custom commands "

    if prompt := st.chat_input(chat_input_placeholder, key="prompt"):
        if parse_command(text=prompt, modal=modal):
            st.rerun()
        else:
            history = get_messages_history(history_len)
            chat_box.user_say(prompt)
            if dialogue_mode == "LLM Conversation":
                chat_box.ai_say("Thinking...")
                text = ""
                message_id = ""
                r = api.chat(
                    prompt,
                    history=history,
                    conversation_id=conversation_id,
                    model=llm_model,
                    prompt_name=prompt_template_name,
                    temperature=0,
                )

                for t in r:
                    if error_msg := check_error_msg(t):  # check whether error occured
                        st.error(error_msg)
                        break
                    text += t.get("text", "")
                    chat_box.update_msg(text)
                    message_id = t.get("message_id", "")

                metadata = {
                    "message_id": message_id,
                }
                chat_box.update_msg(
                    text, streaming=False, metadata=metadata
                )  # Update the final string and remove the cursor

    if st.session_state.get("need_rerun"):
        st.session_state["need_rerun"] = False
        st.rerun()

    now = datetime.now()
    with st.sidebar:
        cols = st.columns(2)
        export_btn = cols[0]
        if cols[1].button(
            "Clear conversation",
            use_container_width=True,
        ):
            chat_box.reset_history()
            st.rerun()

    export_btn.download_button(
        "Export records",
        "".join(chat_box.export2md()),
        file_name=f"{now:%Y-%m-%d %H.%M}_Conversation record.md",
        mime="text/markdown",
        use_container_width=True,
    )
    #st.write("Welcome in my world is now development")
