import openai
from Ai_models.keys.ai import YandexGPT_Lite_API, YandexGPT_Lite_Folder_ID

def yandexgptpro_requst(system_context, user_context, max_tokens, temperature):
    client = openai.OpenAI(
       api_key=YandexGPT_Lite_API,
       base_url="https://llm.api.cloud.yandex.net/v1"
    )

    response = client.chat.completions.create(
        model=f"gpt://{YandexGPT_Lite_Folder_ID}/yandexgpt/rc",
        messages=[
           {"role": "assistant", "content": f"{system_context}"},
           {"role": "user", "content": f"{user_context}"}
        ],
        max_tokens=max_tokens,
        temperature=temperature,
        stream=True
    )

    s = ''
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            s += chunk.choices[0].delta.content

    return s