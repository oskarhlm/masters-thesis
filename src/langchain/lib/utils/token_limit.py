import tiktoken
model_token_mapping = {
    'gpt-3.5-turbo-0125': 16.385,
    'gpt-4-0125-preview': 128.000,
    "gpt-4": 128.000,  # Watch out
    "gpt-4-0314": 8192,
    "gpt-4-0613": 8192,
    "gpt-4-32k": 32768,
    "gpt-4-32k-0314": 32768,
    "gpt-4-32k-0613": 32768,
    "gpt-3.5-turbo": 16.385,  # Watch out
    "gpt-3.5-turbo-0301": 4096,
    "gpt-3.5-turbo-0613": 4096,
    "gpt-3.5-turbo-16k": 16385,
    "gpt-3.5-turbo-16k-0613": 16385,
    "gpt-3.5-turbo-instruct": 4096,
    "text-ada-001": 2049,
    "ada": 2049,
    "text-babbage-001": 2040,
    "babbage": 2049,
    "text-curie-001": 2049,
    "curie": 2049,
    "davinci": 2049,
    "text-davinci-003": 4097,
    "text-davinci-002": 4097,
    "code-davinci-002": 8001,
    "code-davinci-001": 8001,
    "code-cushman-002": 2048,
    "code-cushman-001": 2048,
}


def get_context_window_percentage(text: str, model_name: str) -> float:
    enc = tiktoken.encoding_for_model(model_name)
    print(text, len(enc.encode(text)), model_token_mapping[model_name])
    return len(enc.encode(text)) / model_token_mapping[model_name]
