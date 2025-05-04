import openai
from Ai_models.keys.ai import YandexGPT_Lite_API, YandexGPT_Lite_Folder_ID

def yandexgptlite_requst(requst_for_ai):
    client = openai.OpenAI(
       api_key=YandexGPT_Lite_API,
       base_url="https://llm.api.cloud.yandex.net/v1"
    )

    response = client.chat.completions.create(
        model=f"gpt://{YandexGPT_Lite_Folder_ID}/yandexgpt-lite/rc",
        messages=[
           {"role": "assistant", "content": "Ты умный ассистент."},
           {"role": "user", "content": f"{requst_for_ai}"}
        ],
        max_tokens=10000,
        temperature=0.7,
        stream=True
    )

    s = ''
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            s += chunk.choices[0].delta.content

    return s
