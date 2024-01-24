from typing import *
from pathlib import Path

# The configuration imported here is the configuration on the machine that initiates the request (such as WEBUI), and is mainly used to set default values ​​for the front end. Distributed deployment can be different from that on the server

from app.configs.server_config import (
    HTTPX_DEFAULT_TIMEOUT,
)
from app.configs import logger, log_verbose, LLM_MODELS, TEMPERATURE
import httpx
import contextlib
import json
import os
from io import BytesIO
from app.utils import api_address, get_httpx_client

from pprint import pprint


class ApiRequest:
    def __init__(
        self,
        base_url: str = api_address(),
        timeout: float = HTTPX_DEFAULT_TIMEOUT,
    ):
        self.base_url = base_url
        self.timeout = timeout
        self._use_async = False
        self._client = None

    @property
    def client(self):
        if self._client is None or self._client.is_closed:
            self._client = get_httpx_client(
                base_url=self.base_url, use_async=self._use_async, timeout=self.timeout
            )
        return self._client

    def get(
        self,
        url: str,
        params: Union[Dict, List[Tuple], bytes] = None,
        retry: int = 3,
        stream: bool = False,
        **kwargs: Any,
    ) -> Union[httpx.Response, Iterator[httpx.Response], None]:
        while retry > 0:
            try:
                if stream:
                    return self.client.stream("GET", url, params=params, **kwargs)
                else:
                    return self.client.get(url, params=params, **kwargs)
            except Exception as e:
                msg = f"error when get {url}: {e}"
                logger.error(
                    f"{e.__class__.__name__}: {msg}",
                    exc_info=e if log_verbose else None,
                )
                retry -= 1

    def post(
        self,
        url: str,
        data: Dict = None,
        json: Dict = None,
        retry: int = 3,
        stream: bool = False,
        **kwargs: Any,
    ) -> Union[httpx.Response, Iterator[httpx.Response], None]:
        while retry > 0:
            try:
                # print(kwargs)
                if stream:
                    return self.client.stream(
                        "POST", url, data=data, json=json, **kwargs
                    )
                else:
                    return self.client.post(url, data=data, json=json, **kwargs)
            except Exception as e:
                msg = f"error when post {url}: {e}"
                logger.error(
                    f"{e.__class__.__name__}: {msg}",
                    exc_info=e if log_verbose else None,
                )
                retry -= 1

    def delete(
        self,
        url: str,
        data: Dict = None,
        json: Dict = None,
        retry: int = 3,
        stream: bool = False,
        **kwargs: Any,
    ) -> Union[httpx.Response, Iterator[httpx.Response], None]:
        while retry > 0:
            try:
                if stream:
                    return self.client.stream(
                        "DELETE", url, data=data, json=json, **kwargs
                    )
                else:
                    return self.client.delete(url, data=data, json=json, **kwargs)
            except Exception as e:
                msg = f"error when delete {url}: {e}"
                logger.error(
                    f"{e.__class__.__name__}: {msg}",
                    exc_info=e if log_verbose else None,
                )
                retry -= 1

    def _httpx_stream2generator(
        self,
        response: contextlib._GeneratorContextManager,
        as_json: bool = False,
    ):
        """
        Convert the GeneratorContextManager returned by httpx.stream into a normal generator
        """

        async def ret_async(response, as_json):
            try:
                async with response as r:
                    async for chunk in r.aiter_text(None):
                        if not chunk:  # fastchat api yield empty bytes on start and end
                            continue
                        if as_json:
                            try:
                                data = json.loads(chunk)
                                # pprint(data, depth=1)
                                yield data
                            except Exception as e:
                                msg = f"The interface returns json error: ‘{chunk}’. The error message is:{e}。"
                                logger.error(
                                    f"{e.__class__.__name__}: {msg}",
                                    exc_info=e if log_verbose else None,
                                )
                        else:
                            # print(chunk, end="", flush=True)
                            yield chunk
            except httpx.ConnectError as e:
                msg = f"Unable to connect to the API server, please confirm that 'api.py' has been started normally.({e})"
                logger.error(msg)
                yield {"code": 500, "msg": msg}
            except httpx.ReadTimeout as e:
                msg = f"API communication timed out, please confirm that FastChat and API services have been started (see Wiki '5. Start API service or Web UI for details)'）。（{e}）"
                logger.error(msg)
                yield {"code": 500, "msg": msg}
            except Exception as e:
                msg = f"API communication encountered error: {e}"
                logger.error(
                    f"{e.__class__.__name__}: {msg}",
                    exc_info=e if log_verbose else None,
                )
                yield {"code": 500, "msg": msg}

        def ret_sync(response, as_json):
            try:
                with response as r:
                    for chunk in r.iter_text(None):
                        if not chunk:  # fastchat api yield empty bytes on start and end
                            continue
                        if as_json:
                            try:
                                data = json.loads(chunk)
                                # pprint(data, depth=1)
                                yield data
                            except Exception as e:
                                msg = f"The interface returns json error: '{chunk}'. The error message is:{e}。"
                                logger.error(
                                    f"{e.__class__.__name__}: {msg}",
                                    exc_info=e if log_verbose else None,
                                )
                        else:
                            # print(chunk, end="", flush=True)
                            yield chunk
            except httpx.ConnectError as e:
                msg = f"Unable to connect to the API server, please confirm that 'api.py' has been started normally.({e})"
                logger.error(msg)
                yield {"code": 500, "msg": msg}
            except httpx.ReadTimeout as e:
                msg = f"API communication timed out, please confirm that FastChat and API services have been started (see Wiki '5. Start API service or Web UI for details)'）。（{e}）"
                logger.error(msg)
                yield {"code": 500, "msg": msg}
            except Exception as e:
                msg = f"API communication encountered error:{e}"
                logger.error(
                    f"{e.__class__.__name__}: {msg}",
                    exc_info=e if log_verbose else None,
                )
                yield {"code": 500, "msg": msg}

        if self._use_async:
            return ret_async(response, as_json)
        else:
            return ret_sync(response, as_json)

    def _get_response_value(
        self,
        response: httpx.Response,
        as_json: bool = False,
        value_func: Callable = None,
    ):
        """
        Convert the response returned by a synchronous or asynchronous request
        `as_json`: return json
        `value_func`: Users can customize the return value. This function accepts response or json
        """

        def to_json(r):
            try:
                return r.json()
            except Exception as e:
                msg = "API failed to return correct JSON." + str(e)
                if log_verbose:
                    logger.error(
                        f"{e.__class__.__name__}: {msg}",
                        exc_info=e if log_verbose else None,
                    )
                return {"code": 500, "msg": msg, "data": None}

        if value_func is None:
            value_func = lambda r: r

        async def ret_async(response):
            if as_json:
                return value_func(to_json(await response))
            else:
                return value_func(await response)

        if self._use_async:
            return ret_async(response)
        else:
            if as_json:
                return value_func(to_json(response))
            else:
                return value_func(response)

    def chat(
        self,
        query: str,
        conversation_id: str = None,
        history_len: int = -1,
        history: List[Dict] = [],
        stream: bool = True,
        model: str = LLM_MODELS,
        temperature: float = TEMPERATURE,
        max_tokens: int = None,
        prompt_name: str = "default",
        **kwargs,
    ):
        """

        Corresponds to main.py/chat interface
        """
        test_data = {
            "query": query,
            "conversation_id": conversation_id,
            "history_len": history_len,
            "history": history,
            "stream": stream,
            "model_name": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "prompt_name": prompt_name,
        }
        data = {
            "query": query,
            "conversation_id": conversation_id,
            "history_len": history_len,
            "history": history,
            "stream": stream,
            "model_name": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "prompt_name": prompt_name,
        }

        # print(f"received input message:")
        # pprint(data)

        response = self.post("/chat", json=test_data, stream=True, **kwargs)
        return self._httpx_stream2generator(response, as_json=True)


class AsyncApiRequest(ApiRequest):
    def __init__(
        self, base_url: str = api_address(), timeout: float = HTTPX_DEFAULT_TIMEOUT
    ):
        super().__init__(base_url, timeout)
        self._use_async = True


if __name__ == "__main__":
    request = ApiRequest()

    print(f"api request is done")
