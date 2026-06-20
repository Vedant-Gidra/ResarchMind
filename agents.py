from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from config import RESEARCHER_MODEL, WRITER_MODEL, WRITER_LLM_TEMPERATURE, RESEARCHER_LLM_TEMPERATURE
from dotenv import load_dotenv
import os
from typing import Optional
from mcp_tools import get_mcp_tools_list

load_dotenv()


class ConfigError(RuntimeError):
    """Raised when required runtime configuration is missing or invalid."""
    pass


def _resolve_groq_api_key() -> str:
    """Fetch Groq API key from environment variables."""
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ConfigError(
            "Missing GROQ_API_KEY. Set it in your .env file or Streamlit secrets."
        )

    return api_key


# Separate cached LLM instances
_researcher_llm: Optional[ChatGroq] = None
_writer_llm: Optional[ChatGroq] = None


def get_researcher_llm() -> ChatGroq:
    """Lazily initialize Groq LLM for Researcher Agent."""
    global _researcher_llm

    if _researcher_llm is not None:
        return _researcher_llm

    try:
        _researcher_llm = ChatGroq(
            model=RESEARCHER_MODEL,
            temperature=RESEARCHER_LLM_TEMPERATURE,
            groq_api_key=_resolve_groq_api_key(),
        )
        return _researcher_llm

    except Exception as exc:
        raise RuntimeError(
            "Failed to initialize Groq Researcher model client. Check API key, model access, and network."
        ) from exc


def get_writer_llm() -> ChatGroq:
    """Lazily initialize Groq LLM for Writer Agent."""
    global _writer_llm

    if _writer_llm is not None:
        return _writer_llm

    try:
        _writer_llm = ChatGroq(
            model=WRITER_MODEL,
            temperature=WRITER_LLM_TEMPERATURE,
            groq_api_key=_resolve_groq_api_key(),
        )
        return _writer_llm

    except Exception as exc:
        raise RuntimeError(
            "Failed to initialize Groq Writer model client. Check API key, model access, and network."
        ) from exc


# ────── RESEARCHER AGENT ──────

def build_researcher_agent(tools=None):
    try:
        if tools is None:
            tools = get_mcp_tools_list()
        return create_agent(
            model=get_researcher_llm(),
            tools=tools
        )
    except Exception as exc:
        raise RuntimeError("Failed to build Researcher Agent.") from exc


# ────── WRITER CHAIN ──────

writer_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are an expert research writer. Write clear, structured, and insightful reports based on research summaries."
    ),
    (
        "human",
        """Write a research report on: {topic}

Research Summary:
{research}

Format as: Introduction, Key Findings, Conclusion, Sources.
Be concise and factual."""
    ),
])


def build_writer_chain():
    try:
        return writer_prompt | get_writer_llm() | StrOutputParser()
    except Exception as exc:
        raise RuntimeError("Failed to build Writer Chain.") from exc
