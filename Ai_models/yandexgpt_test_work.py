import openai
from keys.ai import YandexGPT_Lite_API, YandexGPT_Lite_Folder_ID


client = openai.OpenAI(
   api_key=YandexGPT_Lite_API,
   base_url="https://llm.api.cloud.yandex.net/v1"
)

response = client.chat.completions.create(
    model=f"gpt://{YandexGPT_Lite_Folder_ID}/yandexgpt-lite/rc",
    messages=[
       {"role": "assistant", "content": "Ты Пушкин."},
       {"role": "user", "content": "Ты Пушкин?"}
    ],
    max_tokens=10000,
    temperature=0.7,
    stream=True
)

for chunk in response:
    if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end="")
