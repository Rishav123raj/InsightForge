import json
import re

from . import tools
from .llm import generate_answer
from .retriever import retrieve_documents


def _detect_tools(question: str) -> tuple[list[str], dict]:

    q = question.lower()

    selected: list[str] = []
    payload: dict = {}

    year = 2025

    year_match = re.search(r"20\\d{2}", q)

    if year_match:
        year = int(year_match.group(0))

    if any(x in q for x in ["best", "performed", "top titles", "top movies"]):
        selected.append("best_titles")
        payload["best_titles"] = tools.best_titles(year)

    if "dark orbit" in q and "last kingdom" in q:
        selected.append("compare_titles")
        payload["compare_titles"] = tools.compare_titles(
            "Dark Orbit",
            "Last Kingdom"
        )

    if any(x in q for x in [
        "city",
        "engagement",
        "audience",
        "regional",
        "last month"
    ]):
        selected.append("city_engagement")
        payload["city_engagement"] = tools.city_engagement("2025-12")

    if any(x in q for x in [
        "genre",
        "growth",
        "growing",
        "trending"
    ]):
        selected.append("genre_growth")
        payload["genre_growth"] = tools.genre_growth()

    if any(x in q for x in [
        "comedy",
        "weak",
        "poor performance"
    ]):
        selected.append("weak_comedy")
        payload["weak_comedy"] = tools.weak_comedy()

    if not selected:
        selected.extend([
            "best_titles",
            "genre_growth",
            "city_engagement"
        ])

        payload.setdefault(
            "best_titles",
            tools.best_titles(year)
        )

        payload.setdefault(
            "genre_growth",
            tools.genre_growth()
        )

        payload.setdefault(
            "city_engagement",
            tools.city_engagement("2025-12")
        )

    return selected, payload


def _build_prompt(
    question: str,
    tool_payload: dict,
    documents: list[dict],
    user: dict
) -> str:

    document_context = []

    for doc in documents[:4]:

        document_context.append(
            f'''
DOCUMENT TITLE:
{doc["title"]}

DOCUMENT SNIPPET:
{doc["snippet"]}
'''
        )

    prompt = f"""
USER ROLE:
{user.get("role")}

USER QUESTION:
{question}

STRUCTURED ANALYTICS DATA:
{json.dumps(tool_payload, indent=2)}

RETRIEVED INTERNAL REPORTS:
{"".join(document_context)}

INSTRUCTIONS:
- Answer the user's question directly
- Use analytics data carefully
- Explain WHY trends are happening
- Mention supporting evidence from reports
- Include quantitative insights when available
- Generate concise executive-style analysis
- Do NOT hallucinate unavailable facts
- Do NOT expose PII
- Keep answer under 250 words
"""

    return prompt


def answer_question(question: str, user: dict) -> dict:

    tool_names, tool_payload = _detect_tools(question)

    documents = retrieve_documents(question)

    prompt = _build_prompt(
        question=question,
        tool_payload=tool_payload,
        documents=documents,
        user=user
    )

    llm_answer = generate_answer(prompt)

    return {
        "answer": llm_answer,

        "sources": {
            "structured_tools": tool_names,
            "documents": documents,
        },

        "tool_trace": [
            {
                "tool": name,
                "result_count": len(tool_payload.get(name, []))
            }
            for name in tool_names
        ],

        "chart": build_chart(tool_payload),

        "privacy":
            "Viewer emails and row-level PII are excluded; "
            "access used role-scoped backend tools only.",
    }


def build_chart(payload: dict) -> dict:

    rows = (
        payload.get("best_titles")
        or payload.get("city_engagement")
        or []
    )

    if not rows:
        return {
            "type": "bar",
            "labels": [],
            "values": [],
            "title": "No chart data"
        }

    if "title" in rows[0]:

        return {
            "type": "bar",
            "labels": [
                r["title"]
                for r in rows[:6]
            ],
            "values": [
                r.get("revenue") or 0
                for r in rows[:6]
            ],
            "title": "Revenue by title"
        }

    return {
        "type": "bar",
        "labels": [
            r["city"]
            for r in rows[:6]
        ],
        "values": [
            r.get("views") or 0
            for r in rows[:6]
        ],
        "title": "Views by city"
    }


if __name__ == "__main__":

    print("Testing Ollama-powered analytics assistant...\\n")

    question = (
        "Why is Stellar Run trending recently?"
    )

    response = answer_question(
        question,
        user={"role": "analyst"}
    )

    print("=" * 80)
    print("ANSWER:\\n")
    print(response["answer"])

    print("\\n" + "=" * 80)
    print("TOOL TRACE:\\n")
    print(response["tool_trace"])

    print("\\n" + "=" * 80)
    print("DOCUMENT SOURCES:\\n")

    for doc in response["sources"]["documents"]:
        print(f"- {doc['title']} (score={doc['score']})")

    print("\\n" + "=" * 80)
    print("CHART:\\n")
    print(response["chart"])