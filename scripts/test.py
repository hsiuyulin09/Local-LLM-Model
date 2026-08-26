from pathlib import Path
import httpx
import yaml


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / "config.yaml"


def fail(message):
    print(f"[fail] {message}")
    raise SystemExit(1)


def main():
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    provider_name = config["provider"]
    provider_config = config["providers"][provider_name]
    generation = config["generation"]

    try:
        with httpx.Client( # 建立 Client 物件
            base_url=provider_config["base_url"],
            timeout=provider_config["timeout"],
            trust_env=False # 要求 HTTPX 不使用作業系統環境變數中的網路設定
        ) as client:
            models_response = client.get("models")
            models_response.raise_for_status() # status 檢查, 通過或跳出 error 至 except

            models = models_response.json().get("data", [])
            model_ids = { # 為什麼不直接取得 id 就好，還要先判定是不是 dict? 而且是用 for loop? 用 for loop 是不是代表 id 有可能不只一個?
                item.get("id")
                for item in models
                if isinstance(item, dict)
            }

            if provider_config["model"] not in model_ids:
                fail(f"cannot find model: {provider_config['model']}")

            print(f"[OK] provider: {provider_config['model']}")

            messages = [
                {
                    "role": "system",
                    "content": config["system_prompt"]
                },
                {
                    "role": "user",
                    "content": "Only response: API test successful"
                }
            ]

            request_body = {
                "model": provider_config["model"],
                "messages": messages,
                "temperature": 0,
                "max_tokens": generation["max_tokens"],
                "top_p": 0.1,
                "presence_penalty": generation["presence_penalty"],
                "stream": False
            }

            response = client.post("chat/completions", json=request_body)
            response.raise_for_status() # status 檢查, 通過或跳出 error 至 except

            result = response.json()
            content = result["choices"][0]["message"]["content"]

            if not isinstance(content, str) or not content.strip():
                fail("model response is empty")

            print("[OK] POST v1/chat/completions")
            print(f"assistant: {content}")

    except httpx.ConnectError:
        fail(f"cannot connect to {provider_config['base_url']}")

    except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError) as e:
        fail(f"API fail: {e}")

if __name__ == "__main__":
    main()
        