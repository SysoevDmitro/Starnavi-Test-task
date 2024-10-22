import time

import requests


def generate_reply(post_content, comment_content):
    api_url = "https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill"
    headers = {
        "Authorization": f"Bearer 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"
    }

    prompt = f"Post: {post_content}\nComment: {comment_content}\nReply:"

    data = {
        "inputs": prompt,
        "parameters": {"truncation": "only_first"}  # Обрезаем длинный ввод
    }

    response = requests.post(api_url, headers=headers, json=data)
    if response.status_code == 200:
        reply = response.json()[0]['generated_text']
        return reply.split("Reply:")[-1].strip()
    else:
        return f"Error: {response.json()}"


# Пример использования
post_content = "greetings in US."
comment_content = "Can you expand this post?"
reply = generate_reply(post_content, comment_content)
print(reply)
