import httpx
import yaml


def load_config(config_path="config.yaml"):
    with open(config_path, "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    provider_name = config["provider"]
    provider_config = config["providers"][provider_name]

    return config, provider_config


def create_client(provider_config):
    client = httpx.Client(
        base_url=provider_config["base_url"],
        timeout=provider_config["timeout"],
        trust_env=False,
    )
    return client


def call_llm(client, messages, parameters, provider_config):
    request_body = {
        "model": parameters["model"],
        "messages": messages,
        "stream": False,
        "keep_alive": provider_config["keep_alive"],
        "options": {
            "temperature": parameters["temperature"],
            "num_ctx": parameters["num_ctx"],
            "num_predict": parameters["num_predict"],
            "top_p": parameters["top_p"],
            "repeat_penalty": parameters["repeat_penalty"],
        },
    }

    try:
        response = client.post("/api/chat", json=request_body)
        response.raise_for_status()
        result = response.json()

        content = result["message"]["content"]
        prompt_tokens = result.get("prompt_eval_count", 0)
        completion_tokens = result.get("eval_count", 0)
        total_tokens = prompt_tokens + completion_tokens

        print(
            "token: "
            f"prompt = {prompt_tokens}, "
            f"completion = {completion_tokens}, "
            f"total = {total_tokens}"
        )

        return content

    except httpx.ConnectError:
        print(
            "error: 無法連線到 Ollama，"
            f"請確認 {provider_config['base_url']} 已啟動。"
        )
        return None
    except httpx.HTTPStatusError as error:
        print(
            f"error: Ollama 回傳 {error.response.status_code}，"
            f"{error.response.text}"
        )
        return None
    except (httpx.HTTPError, KeyError, ValueError) as error:
        print(f"error: {error}")
        return None
