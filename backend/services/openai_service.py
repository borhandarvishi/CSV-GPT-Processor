from openai import OpenAI

def get_openai_client(api_key: str):
    return OpenAI(api_key=api_key)


def generate_response(client, prompt: str, model: str, temperature: float, top_p: float, system_prompt: str = "") -> str:
    messages = []
    if system_prompt.strip():
        messages.append({"role": "system", "content": system_prompt.strip()})
    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        top_p=top_p
    )
    return response.choices[0].message.content.strip()
