import os
import sys
import uuid

import yaml
from dotenv import load_dotenv
from openai import OpenAI
from opentelemetry.trace import Status, StatusCode


def load_config(config_path = "config.yaml"):
    load_dotenv() # 讀取根目錄檔名僅為.env 的檔案, 並將檔案內容 (變數代號(key)=變數內容(value)) 轉換為系統變數

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    provider_name = config["provider"]
    provider_config = config["providers"][provider_name]
    api_key = provider_config.get("api_key") or os.getenv(provider_config.get("api_key_env", ""))
    if not api_key:
        print("Cannot find API key")
        sys.exit(1) # 終止程式, 狀態碼 = 1 為異常結束狀態, 系統紀錄或開發者紀錄

    return config, provider_config, api_key


def create_client(provider_config, api_key):
    client = OpenAI( # groq 相容 OpenAI 格式
        base_url=provider_config["base_url"], # OpenAI 格式預設連到 open ai 所以要自訂 url 指向 groq
        api_key=api_key
    )
    return client


def call_llm(client, tracer, messages, parameters, config, provider_config):
    with tracer.start_as_current_span("llm_generation") as span: # span 計篹 with: 區間時間
        provider_name = config["provider"]
        nim_config = provider_config.get("nim", {})
        request_id = str(uuid.uuid4())

        span.set_attribute("model", parameters['model'])
        span.set_attribute("temperature", parameters['temperature'])
        span.set_attribute("max_tokens", parameters['max_tokens'])
        span.set_attribute("presence_penalty", parameters['presence_penalty'])
        span.set_attribute("provider", provider_name)
        span.set_attribute("base_url", provider_config["base_url"])
        span.set_attribute("nim_profile", nim_config.get("profile", ""))
        span.set_attribute("nim_model_path", nim_config.get("model_path", ""))
        span.set_attribute("NIM_MAX_MODEL_LEN", os.getenv("NIM_MAX_MODEL_LEN", ""))
        span.set_attribute("NIM_MAX_NUM_SEQS", os.getenv("NIM_MAX_NUM_SEQS", ""))
        span.set_attribute("NIM_MAX_NUM_BATCHED_TOKENS", os.getenv("NIM_MAX_NUM_BATCHED_TOKENS", ""))
        span.set_attribute("NIM_GPU_MEMORY_UTILIZATION", os.getenv("NIM_GPU_MEMORY_UTILIZATION", ""))
        span.set_attribute("NIM_ENABLE_PREFIX_CACHING", os.getenv("NIM_ENABLE_PREFIX_CACHING", ""))
        span.set_attribute("request_id", request_id)
        span.set_attribute("message_count", len(messages))
        span.set_attribute("error_type", "")
        span.set_attribute("error_message", "")
        span.set_attribute("test_concurrency", os.getenv("TEST_CONCURRENCY", ""))
        user_input = [m['content'] for m in messages if m ['role'] == 'user'][-1]
        span.set_attribute("user_prompt", user_input)

        span.add_event("call_LLM_by_API")

        try:
            response = client.chat.completions.create(
                model=parameters['model'],
                messages=messages,
                temperature=parameters['temperature'],
                max_tokens=parameters['max_tokens'],
                presence_penalty=parameters['presence_penalty'],
                stream=False # stream=False 全部生成完再一次回傳
            )

            content = response.choices[0].message.content # 根據 "response 回傳 JSON 物件內容結構範例" 取得回復
            print(f"token: prompt = {response.usage.prompt_tokens}, completion = {response.usage.completion_tokens}, total = {response.usage.total_tokens}")

            span.set_attribute("assistant_response", content)
            span.set_attribute("prompt_token", response.usage.prompt_tokens)
            span.set_attribute("completion_token", response.usage.completion_tokens)
            span.set_attribute("total_tokens", response.usage.total_tokens)
            span.set_status(Status(StatusCode.OK))

            return content

        except Exception as e:
            span.set_attribute("error_type", type(e).__name__)
            span.set_attribute("error_message", str(e))
            span.set_status(Status(StatusCode.ERROR, str(e)))
            print(f"error: {str(e)}")
            return None
