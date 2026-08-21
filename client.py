import httpx
import yaml


def load_config(config_path="config.yaml"):
    with open(config_path, "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    provider_name = config["provider"]
    provider_config = config["providers"][provider_name]

    return config, provider_config


def create_client(provider_config):
    client = httpx.Client( # 建立 Client 物件
        base_url=provider_config["base_url"],
        timeout=provider_config["timeout"],
        trust_env=False # 要求 HTTPX 不使用作業系統環境變數中的網路設定
    )
    return client


def call_llm(client, messages, parameters, provider_config):
    request_body = {
        "model": parameters["model"],
        "messages": messages,
        "temperature": parameters["temperature"],
        "max_tokens": parameters["max_tokens"],
        "top_p": parameters["top_p"],
        "presence_penalty": parameters["presence_penalty"],
        "stream": False
    }

    try:
        response = client.post("chat/completions", json=request_body)
        response.raise_for_status() # status 檢查, 通過或跳出 error 至 except
        result = response.json() # status 通過後解析成 json

        content = result["choices"][0]["message"]["content"]
        usage = result.get("usage") or {}

        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        total_tokens = usage.get("total_tokens", prompt_tokens + completion_tokens)

        print(
            "token: "
            f"prompt = {prompt_tokens}\n"
            f"completion = {completion_tokens}\n"
            f"total = {total_tokens}\n"
        )

        return content

    except httpx.ConnectError:
        print(
            f"error: 無法連線到 local Qwen API\n"
            f"Please check {provider_config['base_url']}"
        )
        return None

    except httpx.HTTPStatusError as error:
        print(
            f"error: llama-server feedback:\n"
            f"{error.response.status_code}\n"
            f"{error.response.text}"
        )
        return None

    except (httpx.HTTPError, KeyError, ValueError) as error:
        print(f"error: API responde cannot process ({error})")
        return None
