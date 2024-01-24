from .configs import logger, log_verbose
from .configs import MODEL_PRIVIDER, ONLINE_LLM_MODEL
from .configs.server_config import HTTPX_DEFAULT_TIMEOUT,API_SERVER
import asyncio
from typing import (
    Literal,
    Optional,
    Callable,
    Generator,
    Dict,
    Any,
    List,
    Awaitable,
    Union,
    Tuple,
)
import logging
from langchain_community.chat_models import ChatOpenAI
import httpx
import os


def get_prompt_template(type: str = "llm_chat", name: str = "default") -> Optional[str]:
    """
    prompt_config
    type: "llm_chat",
    """

    from .configs import PROMPT_TEMPLATES

    return PROMPT_TEMPLATES[type].get(name)


async def wrap_done(fn: Awaitable, event: asyncio.Event):
    """Wrap an awaitable with a event to signal when it's done or an exception is raised."""
    try:
        await fn
    except Exception as e:
        logging.exception(e)
        # TODO: handle exception
        msg = f"Caught exception: {e}"
        logger.error(
            f"{e.__class__.__name__}: {msg}", exc_info=e if log_verbose else None
        )
    finally:
        # Signal the aiter to stop.
        event.set()


def get_ChatOpenAI(
    model_name: str,
    temperature: float,
    max_tokens: int = None,
    streaming: bool = True,
    callbacks: List[Callable] = [],
    verbose: bool = True,
    **kwargs: Any,
) -> ChatOpenAI:
    config = get_model_worker_config(model_name)

    model = ChatOpenAI(
        streaming=streaming,
        verbose=verbose,
        callbacks=callbacks,
        openai_api_key=config.get("api_key"),
        openai_api_base=config.get("api_base_url"),
        model_name=config.get("model_name"),
        temperature=temperature,
        max_tokens=max_tokens,
        openai_proxy=config.get("openai_proxy"),
        **kwargs,
    )
    return model


def get_model_worker_config(model_name: str = None) -> dict:
    """
    Load the configuration items of the model worker.
    Priority: FSCHAT_MODEL_WORKERS[model_name] > ONLINE_LLM_MODEL[model_name] > FSCHAT_MODEL_WORKERS["default"]
    """

    # from server import model_workers

    config = ONLINE_LLM_MODEL.get(MODEL_PRIVIDER)

    """
    config = FSCHAT_MODEL_WORKERS.get("default", {}).copy()
    config.update(ONLINE_LLM_MODEL.get(model_name, {}).copy())
    config.update(FSCHAT_MODEL_WORKERS.get(model_name, {}).copy())

    if model_name in ONLINE_LLM_MODEL:
        config["online_api"] = True
        if provider := config.get("provider"):
            try:
                config["worker_class"] = getattr(model_workers, provider)
            except Exception as e:
                msg = f"在线模型 ‘{model_name}’ 的provider没有正确配置"
                logger.error(
                    f"{e.__class__.__name__}: {msg}",
                    exc_info=e if log_verbose else None,
                )

    # local model
    if model_name in MODEL_PATH["llm_model"]:
        path = get_model_path(model_name)
        config["model_path"] = path
        if path and os.path.isdir(path):
            config["model_path_exists"] = True
        config["device"] = llm_device(config.get("device"))
    """
    return config


def api_address() -> str:
    from .configs.server_config import API_SERVER

    host = API_SERVER["host"]
    if host == "0.0.0.0":
        host = "127.0.0.1"
    port = API_SERVER["port"]
    return f"http://{host}:{port}"


def webui_address() -> str:
    from configs.server_config import WEBUI_SERVER

    host = WEBUI_SERVER["host"]
    port = WEBUI_SERVER["port"]
    return f"http://{host}:{port}"


def get_httpx_client(
    use_async: bool = False,
    proxies: Union[str, Dict] = None,
    timeout: float = HTTPX_DEFAULT_TIMEOUT,
    **kwargs,
) -> Union[httpx.Client, httpx.AsyncClient]:
    """
    helper to get httpx client with default proxies that bypass local addesses.
    """
    default_proxies = {
        # do not use proxy for locahost
        "all://127.0.0.1": None,
        "all://localhost": None,
    }

    # construct Client
    kwargs.update(timeout=timeout, proxies=default_proxies)

    if log_verbose:
        logger.info(f"{get_httpx_client.__class__.__name__}:kwargs: {kwargs}")

    if use_async:
        return httpx.AsyncClient(**kwargs)
    else:
        return httpx.Client(**kwargs)


if __name__ == "__main__":
    get_model_worker_config()
