from client import call_llm, create_client, load_config


def start_chat(client, config, provider_config, model=None, temperature=None, max_tokens=None, top_p=None, presence_penalty=None):
    generation = config["generation"]
    parameters = {
        "model": model or provider_config["model"],
        "temperature": (
            temperature
            if temperature is not None
            else generation["temperature"]
        ),
        "max_tokens": (
            max_tokens
            if max_tokens is not None
            else generation["max_tokens"]
        ),
        "top_p": (
            top_p
            if top_p is not None
            else generation["top_p"]
        ),
        "presence_penalty": (
            presence_penalty
            if presence_penalty is not None
            else generation["presence_penalty"]
        )
    }

    memory = [
        {
            "role": "system",
            "content": config["system_prompt"]
        },
    ]

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

        response = call_llm(client, memory, parameters, provider_config)

        if response:
            print(f"user: {user_input}")
            print(f"assistant: {response}")
            print("=" * 100)
            memory.append({"role": "assistant", "content": response})


def main():
    config, provider_config = load_config()

    with create_client(provider_config) as client:
        start_chat(client, config, provider_config)


if __name__ == "__main__":
    main()
