import openai
from tenacity import retry, wait_random_exponential, stop_after_attempt

@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
def get_chat_completion(
    messages: list[dict], 
    max_tokens: int = 1000, 
    model: str = "gpt-3.5-turbo",
    temperature: float = 0.7
):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature
    )["choices"][0]["message"]["content"]
    return response.strip()
