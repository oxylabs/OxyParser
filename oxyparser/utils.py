import tiktoken

enc = tiktoken.get_encoding("p50k_base")


def get_token_count(data: str) -> int:
    tokens = enc.encode(data)
    count = len(tokens)
    return count
