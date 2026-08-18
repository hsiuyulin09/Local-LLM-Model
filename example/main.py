from llm_client import call_llm, create_client, load_config
from trace_utils import setup_tracer


def start_chat(client, tracer, config, provider_config, model = None, temperature = None, max_tokens = None, presence_penalty = None):
    generation = config["generation"]
    parameters = {
        "model": model or provider_config["model"],
        "temperature": temperature if temperature is not None else generation["temperature"],
        "max_tokens": max_tokens if max_tokens is not None else generation["max_tokens"],
        "presence_penalty": presence_penalty if presence_penalty is not None else generation["presence_penalty"],
    }

    memory = [{"role": "system", "content": "You are a professional and helpful assistant, please respond in the user's language."}]

    print(f"{parameters['model']} : Key in 'q' or 'quit' while you want to end the chat.")
    print("=" * 100)

    while True:
        user_input = input("\n user:")

        if user_input.lower() in ['quit', 'q']:
            print("system off")
            break

        if not user_input.strip():
            continue

        memory.append({"role": "user", "content": user_input})
        response = call_llm(client, tracer, memory, parameters, config, provider_config)

        if response:
            print(f"user: {user_input}")
            print(f"assistant: {response}")
            print("=" * 100)
            memory.append({"role": "assistant", "content": response})


def main():
    config, provider_config, api_key = load_config()
    client = create_client(provider_config, api_key)
    tracer = setup_tracer()
    start_chat(client, tracer, config, provider_config)


if __name__ == "__main__":
    main()
