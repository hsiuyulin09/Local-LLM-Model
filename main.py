from client import call_llm, create_client, load_config


def start_chat(
    client,
    config,
    provider_config,
    model=None,
    temperature=None,
    num_ctx=None,
    num_predict=None,
    top_p=None,
    repeat_penalty=None,
):
    generation = config["generation"]
    parameters = {
        "model": model or provider_config["model"],
        "temperature": (
            temperature
            if temperature is not None
            else generation["temperature"]
        ),
        "num_ctx": num_ctx if num_ctx is not None else generation["num_ctx"],
        "num_predict": (
            num_predict
            if num_predict is not None
            else generation["num_predict"]
        ),
        "top_p": top_p if top_p is not None else generation["top_p"],
        "repeat_penalty": (
            repeat_penalty
            if repeat_penalty is not None
            else generation["repeat_penalty"]
        ),
    }

    memory = []

    print(
        f"{parameters['model']}：輸入 q 或 quit 結束對話。"
    )
    print("=" * 100)

    while True:
        user_input = input("\nuser: ")

        if user_input.lower() in ["quit", "q"]:
            print("system off")
            break

        if not user_input.strip():
            continue

        memory.append({"role": "user", "content": user_input})
        response = call_llm(
            client,
            memory,
            parameters,
            provider_config,
        )

        if response:
            print(f"user: {user_input}")
            print(f"assistant: {response}")
            print("=" * 100)
            memory.append({"role": "assistant", "content": response})


def main():
    config, provider_config = load_config()
    client = create_client(provider_config)
    start_chat(client, config, provider_config)


if __name__ == "__main__":
    main()
