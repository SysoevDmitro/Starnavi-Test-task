import time

import requests
from celery import shared_task


@shared_task
def generate_reply(post_content, comment_content, initial_delay=60, retries=5, delay=60):
    time.sleep(initial_delay)
    api_url = "https://api-inference.huggingface.co/models/meta-llama/Llama-3.2-3B"
    headers = {
        "Authorization": f"Bearer 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 "
    }

    prompt = f"Post: {post_content}\nComment: {comment_content}\nReply:"

    data = {
        "inputs": prompt,
        "parameters": {
            "max_length": 150,  # Максимальная длина генерируемого текста
            "return_full_text": False  # Возврат только сгенерированного ответа
        }
    }

    for attempt in range(retries):
        response = requests.post(api_url, headers=headers, json=data)
        if response.status_code == 200:
            reply = response.json()[0]['generated_text']
            return reply.split("Reply:")[-1].strip()
        elif response.status_code == 503:  # Model loading error
            print(f"Model is loading. Attempt {attempt + 1} of {retries}. Waiting for {delay} seconds.")
            time.sleep(delay)  # Подождите перед повторной попыткой
        else:
            return f"Error: {response.json()}"

    return "Error: Model could not be loaded in time."
