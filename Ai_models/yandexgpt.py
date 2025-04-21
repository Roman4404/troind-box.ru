import openai

def test_requst(yandexgpt_api, folder_id):
    client = openai.OpenAI(
       api_key=yandexgpt_api,
       base_url="https://llm.api.cloud.yandex.net/v1"
    )

    response = client.chat.completions.create(
        model=f"gpt://{folder_id}/yandexgpt-lite/rc",
        messages=[
           {"role": "assistant", "content": "Ты Пушкин."},
           {"role": "user", "content": "Ты Пушкин?"}
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