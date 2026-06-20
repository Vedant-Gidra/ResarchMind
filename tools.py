from langchain.tools import tool
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse


def _is_valid_http_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
    except Exception:
        return False


@tool
def scrape_url(url: str) -> str:
    """Scrape and return relevant text content from a given URL."""
    url = (url or "").strip()
    if not _is_valid_http_url(url):
        return "Could not scrape URL: invalid URL format."

    try:
        resp = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        text = soup.get_text(separator=" ", strip=True)
        if not text:
            return "Could not scrape URL: page contains no readable text."
        return text[:1200]
    except requests.Timeout:
        return "Could not scrape URL: request timed out."
    except requests.HTTPError as exc:
        return f"Could not scrape URL: HTTP error ({exc.response.status_code})."
    except requests.RequestException as exc:
        return f"Could not scrape URL: network error ({exc})."
    except Exception as e:
        return f"Could not scrape URL: unexpected error ({e})."
