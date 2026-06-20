import re


def _extract_retry_seconds(text: str) -> int | None:
    patterns = [
        r"retry in\s+(\d+(?:\.\d+)?)s",
        r"retrydelay['\"]?\s*:\s*['\"]?(\d+)(?:\.\d+)?s['\"]?",
        r"Please retry in\s+(\d+(?:\.\d+)?)s",
        r"retry-after:\s*(\d+)",
        r"retry after (\d+) seconds",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            try:
                return max(1, int(float(match.group(1))))
            except ValueError:
                return None
    return None


def normalize_llm_error(exc: Exception) -> str:
    raw = str(exc)
    text = raw.lower()
    retry_seconds = _extract_retry_seconds(raw)

    if "rate_limit" in text or "rate limit" in text or "429" in text or \
       "resource_exhausted" in text or "quota exceeded" in text or \
       "too many requests" in text:

        if "free" in text or "trial" in text or "per_day" in text or "perday" in text:
            msg = (
                "Groq API quota exceeded (free-tier limit reached). "
                "Wait for the quota reset or upgrade your plan."
            )
        else:
            msg = "Groq API rate limit reached."

        if retry_seconds is not None:
            msg += f" Retry after about {retry_seconds} seconds."
        return msg

    if "401" in text or "unauthorized" in text or \
       "api key" in text and ("invalid" in text or "expired" in text or "missing" in text):
        return (
            "Groq API key is invalid, expired, or missing. "
            "Set GROQ_API_KEY in your .env file."
        )

    if "model" in text and ("not found" in text or "invalid" in text or "does not exist" in text):
        return (
            "Invalid Groq model name. Check the model ID in agents.py."
        )

    if "context" in text and "length" in text or "token" in text and "limit" in text:
        return (
            "Request exceeds the model's token limit. "
            "Reduce the amount of research text passed to the writer chain."
        )

    return raw


def format_step_error(step_name: str, exc: Exception) -> str:
    return f"{step_name}: {normalize_llm_error(exc)}"
