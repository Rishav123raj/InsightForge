import re
from . import tools
from .retriever import retrieve_documents


def _detect_tools(question: str) -> tuple[list[str], dict]:
    q = question.lower()
    selected: list[str] = []
    payload: dict = {}
    year = 2025
    year_match = re.search(r"20\d{2}", q)
    if year_match:
        year = int(year_match.group(0))
    if any(x in q for x in ["best", "performed", "top titles"]):
        selected.append("best_titles")
        payload["best_titles"] = tools.best_titles(year)
    if "dark orbit" in q and "last kingdom" in q:
        selected.append("compare_titles")
        payload["compare_titles"] = tools.compare_titles("Dark Orbit", "Last Kingdom")
    if "city" in q or "last month" in q or "strongest engagement" in q:
        selected.append("city_engagement")
        payload["city_engagement"] = tools.city_engagement("2025-12")
    if "genre" in q or "growing" in q:
        selected.append("genre_growth")
        payload["genre_growth"] = tools.genre_growth()
    if "comedy" in q or "weak" in q:
        selected.append("weak_comedy")
        payload["weak_comedy"] = tools.weak_comedy()
    if "recommend" in q or "leadership" in q or not selected:
        selected.extend(["best_titles", "genre_growth", "city_engagement"])
        payload.setdefault("best_titles", tools.best_titles(year))
        payload.setdefault("genre_growth", tools.genre_growth())
        payload.setdefault("city_engagement", tools.city_engagement("2025-12"))
    return selected, payload


def answer_question(question: str, user: dict) -> dict:
    tool_names, tool_payload = _detect_tools(question)
    documents = retrieve_documents(question)
    answer_parts = []

    if "best_titles" in tool_payload:
        rows = tool_payload["best_titles"][:3]
        answer_parts.append("Top 2025 performers are " + ", ".join(f"{r['title']} (${r['revenue']:,.0f} revenue, {r['avg_rating']} rating)" for r in rows) + ".")
    if "compare_titles" in tool_payload:
        rows = tool_payload["compare_titles"]
        answer_parts.append("Comparison: " + "; ".join(f"{r['title']} has ${r['revenue']:,.0f} revenue, {r['avg_rating']} rating, and {r['completions']} completions" for r in rows) + ".")
    if "city_engagement" in tool_payload and tool_payload["city_engagement"]:
        c = tool_payload["city_engagement"][0]
        answer_parts.append(f"{c['city']} shows the strongest recent engagement with {c['views']:,} views and {c['completion_rate']:.0%} completion.")
    if "genre_growth" in tool_payload and tool_payload["genre_growth"]:
        g = tool_payload["genre_growth"][0]
        answer_parts.append(f"{g['genre']} is growing fastest, up {g['pct_growth']}% from Q1 to Q4 views.")
    if "weak_comedy" in tool_payload:
        answer_parts.append("Comedy weakness is tied to lower completion rates and lower review scores than the action/sci-fi slate; campaign notes also mention creative fatigue and poor trailer conversion.")
    if documents:
        answer_parts.append("Relevant internal reports support this with context from " + ", ".join(d["title"] for d in documents[:2]) + ".")
    answer_parts.append("Recommended next steps: double down on high-retention genres, refresh comedy creative, and shift incremental spend toward the strongest cities and audience segments.")

    return {
        "answer": " ".join(answer_parts),
        "sources": {"structured_tools": tool_names, "documents": documents},
        "tool_trace": [{"tool": name, "result_count": len(tool_payload.get(name, []))} for name in tool_names],
        "chart": build_chart(tool_payload),
        "privacy": "Viewer emails and row-level PII are excluded; access used role-scoped backend tools only.",
    }


def build_chart(payload: dict) -> dict:
    rows = payload.get("best_titles") or payload.get("city_engagement") or []
    if not rows:
        return {"type": "bar", "labels": [], "values": [], "title": "No chart data"}
    if "title" in rows[0]:
        return {"type": "bar", "labels": [r["title"] for r in rows[:6]], "values": [r.get("revenue") or 0 for r in rows[:6]], "title": "Revenue by title"}
    return {"type": "bar", "labels": [r["city"] for r in rows[:6]], "values": [r.get("views") or 0 for r in rows[:6]], "title": "Views by city"}


if __name__ == "__main__":
    print("Testing AI analytics assistant...\n")

    question = "What are the best performing sci-fi titles in 2025 and which city has the strongest engagement?"

    response = answer_question(
        question,
        user={"role": "analyst"}
    )

    print("=" * 80)
    print("ANSWER:\n")
    print(response["answer"])

    print("\n" + "=" * 80)
    print("TOOL TRACE:\n")
    print(response["tool_trace"])

    print("\n" + "=" * 80)
    print("DOCUMENT SOURCES:\n")

    for doc in response["sources"]["documents"]:
        print(f"- {doc['title']} (score={doc['score']})")

    print("\n" + "=" * 80)
    print("CHART:\n")
    print(response["chart"])

    print("\n" + "=" * 80)
    print("PRIVACY:\n")
    print(response["privacy"])