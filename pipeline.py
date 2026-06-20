from agents import (
    build_researcher_agent,
    build_writer_chain,
)
from error_handling import format_step_error, normalize_llm_error


def _content_to_text(content) -> str:
    """Normalize LLM message content into readable plain text."""
    if content is None:
        return ""
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        chunks = []
        for item in content:
            if isinstance(item, dict):
                text = item.get("text") or item.get("content") or ""
                if text:
                    chunks.append(str(text))
            else:
                chunks.append(str(item))
        return "\n".join(chunks).strip()
    if isinstance(content, dict):
        return str(content.get("text") or content.get("content") or "").strip()
    return str(content).strip()


def _extract_last_message_content(step_name: str, result: dict) -> str:
    """Safely extract assistant content from an agent invoke response."""
    try:
        messages = result.get("messages", [])
        if not messages:
            raise ValueError("No messages returned.")
        content = _content_to_text(messages[-1].content)
        if not content:
            raise ValueError("Last message content is empty.")
        return content
    except Exception as exc:
        raise RuntimeError(f"{step_name} returned an invalid response format.") from exc


def run_research_pipeline(topic: str) -> dict:
    topic = (topic or "").strip()
    if not topic:
        raise ValueError("Topic cannot be empty.")

    state = {"errors": {}}

    print("\n" + " ="*50)
    print("step 1 - Researcher Agent is gathering information...")
    print("="*50)

    try:
        researcher_agent = build_researcher_agent()
        research_result = researcher_agent.invoke({
            "messages": [("user", f"Find recent and relevant information about: {topic}")]
        })
        state["research"] = _extract_last_message_content("Researcher step", research_result)
        print("\nresearch result:", state["research"])
    except Exception as exc:
        state["errors"]["researcher"] = format_step_error("Step 1 failed (Researcher Agent)", exc)
        print(f"\n{state['errors']['researcher']}")

    print("\n" + " ="*50)
    print("step 2 - Writer is drafting the report...")
    print("="*50)

    if state.get("research"):
        try:
            writer_chain = build_writer_chain()
            state["report"] = writer_chain.invoke({
                "topic": topic,
                "research": state["research"]
            })
            state["report"] = _content_to_text(state["report"])
            if not state["report"]:
                raise RuntimeError("Writer produced an empty report.")
            print("\nFinal Report\n", state["report"])
        except Exception as exc:
            state["errors"]["writer"] = format_step_error("Step 2 failed (Writer Chain)", exc)
            print(f"\n{state['errors']['writer']}")
    else:
        state["errors"]["writer"] = "Step 2 skipped (Writer Chain): no research context available."
        print(f"\n{state['errors']['writer']}")

    if state["errors"]:
        print("\nPipeline completed with partial results and errors:")
        for step, msg in state["errors"].items():
            print(f"- {step}: {msg}")

    return state


if __name__ == "__main__":
    try:
        topic = input("\nEnter a research topic: ")
        run_research_pipeline(topic)
    except KeyboardInterrupt:
        print("\nProcess interrupted by user.")
    except Exception as exc:
        print(f"\nPipeline failed: {normalize_llm_error(exc)}")
