import streamlit as st
from app.webui_pages.utils import *
from streamlit_option_menu import option_menu
from app.webui_pages.dialogue.dialogue import dialogue_page, chat_box
import os
import sys
from app.configs import VERSION
from app.utils import api_address


api = ApiRequest(base_url=api_address())

if __name__ == "__main__":
    is_lite = "lite" in sys.argv

    st.set_page_config(
        "Langchain-Chatchat WebUI",
        os.path.join("img", "chatchat_icon_blue_square_v2.png"),
        initial_sidebar_state="expanded",
        menu_items={
            "Get Help": "https://github.com/chatchat-space/Langchain-Chatchat",
            "Report a bug": "https://github.com/chatchat-space/Langchain-Chatchat/issues",
            "About": f"""欢迎使用 Langchain-Chatchat WebUI {VERSION}！""",
        },
    )

    pages = {
        "Dialogue": {
            "icon": "chat",
            "func": dialogue_page,
        }
    }

    with st.sidebar:
        st.caption(
            f"""<p align="right">Current Version: {VERSION}</p>""",
            unsafe_allow_html=True,
        )
        options = list(pages)
        icons = [x["icon"] for x in pages.values()]

        default_index = 0
        selected_page = option_menu(
            "",
            options=options,
            icons=icons,
            # menu_icon="chat-quote",
            default_index=default_index,
        )

    if selected_page in pages:
        pages[selected_page]["func"](api=api, is_lite=is_lite)
