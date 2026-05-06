# src/generation/llm_client.py
# This file handles all communication with Ollama LLM.
# Every other module uses this to send prompts and get responses.

import requests
from typing import Optional, Generator
from loguru import logger

import config


def check_ollama_running() -> bool:
    """
    Checks if Ollama server is running before making any requests.
    Returns True if running, False if not.
    """
    try:
        response = requests.get(f"{config.OLLAMA_BASE_URL}/api/tags", timeout=5)
        return response.status_code == 200
    except Exception:
        return False


def check_model_available(model_name: str) -> bool:
    """
    Checks if a specific model is pulled and available in Ollama.
    """
    try:
        response = requests.get(f"{config.OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            models = [m["name"] for m in response.json().get("models", [])]
            # Check if model name matches (with or without :latest tag)
            return any(model_name in m for m in models)
    except Exception:
        pass
    return False


def generate(
    prompt: str,
    system_prompt: Optional[str] = None,
    temperature: float = None,
    max_tokens: int = None,
    stream: bool = False
) -> str:
    """
    Send a prompt to Ollama and get a response back.

    prompt:        the user message / query
    system_prompt: optional instructions that shape LLM behavior
    temperature:   0.0 = deterministic, 1.0 = creative (default from config)
    max_tokens:    max length of response (default from config)
    stream:        if True, prints tokens as they arrive (for terminal use)

    Returns the full response as a string.
    """
    if not check_ollama_running():
        error_msg = "Ollama is not running. Please start it with: ollama serve"
        logger.error(error_msg)
        return error_msg

    temperature = temperature or config.LLM_TEMPERATURE
    max_tokens  = max_tokens  or config.LLM_MAX_TOKENS

    # Build messages list
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model":    config.OLLAMA_LLM_MODEL,
        "messages": messages,
        "stream":   stream,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens,
        }
    }

    try:
        logger.info(f"Sending request to Ollama ({config.OLLAMA_LLM_MODEL})...")

        if stream:
            # Stream mode — print tokens as they arrive
            return _stream_response(payload)
        else:
            # Normal mode — wait for full response
            response = requests.post(
                f"{config.OLLAMA_BASE_URL}/api/chat",
                json=payload,
                timeout=300  # 5 min timeout for long generations
            )
            response.raise_for_status()
            result = response.json()
            content = result["message"]["content"]
            logger.info(f"Response received ({len(content)} characters)")
            return content

    except requests.exceptions.Timeout:
        error = "LLM request timed out. Try a shorter prompt or increase timeout."
        logger.error(error)
        return error
    except Exception as e:
        error = f"LLM request failed: {str(e)}"
        logger.error(error)
        return error


def _stream_response(payload: dict) -> str:
    """
    Handles streaming response from Ollama.
    Prints each token as it arrives and returns the full text.
    """
    full_response = ""
    try:
        with requests.post(
            f"{config.OLLAMA_BASE_URL}/api/chat",
            json={**payload, "stream": True},
            stream=True,
            timeout=300
        ) as response:
            import json
            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line)
                    token = chunk.get("message", {}).get("content", "")
                    print(token, end="", flush=True)
                    full_response += token
                    if chunk.get("done"):
                        break
        print()  # newline after streaming ends
    except Exception as e:
        logger.error(f"Streaming failed: {e}")
    return full_response


def get_available_models() -> list:
    """
    Returns list of all models currently available in Ollama.
    Used in Settings page to let user switch models.
    """
    try:
        response = requests.get(f"{config.OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            return [m["name"] for m in response.json().get("models", [])]
    except Exception as e:
        logger.error(f"Could not fetch models: {e}")
    return []


# ── Quick test ───────────────────────────────────────────────
if __name__ == "__main__":
    print("Checking Ollama status...")

    if not check_ollama_running():
        print("Ollama is NOT running! Start it with: ollama serve")
    else:
        print("Ollama is running!")

    models = get_available_models()
    print(f"Available models: {models}")

    print("\nSending test prompt...")
    response = generate(
        prompt="Say 'QA Assistant is ready!' and nothing else.",
        system_prompt="You are a helpful QA assistant.",
        stream=True
    )
    print(f"\nFull response: {response}")