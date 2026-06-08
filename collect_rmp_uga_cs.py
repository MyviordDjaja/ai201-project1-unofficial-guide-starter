"""
collect_rmp_uga_cs.py
---------------------
Pulls Computer Science professor reviews at the University of Georgia (RMP school id 1101)
through Rate My Professors' public GraphQL backend -- no browser / JS rendering needed.

Output (written to ./rmp_data/):
  - one <lastname>_<firstname>.txt per professor: all review comments concatenated
  - metadata.json: structured record per professor (ratings, dept, per-review fields)

This hits a public data endpoint at low volume for a personal/educational project.
Be polite: the REQUEST_DELAY below keeps it slow. Don't crank it up or redistribute the raw data.

Usage:
    pip install requests
    python collect_rmp_uga_cs.py
"""

import base64
import json
import re
import time
from pathlib import Path

import requests

# ---- config -----------------------------------------------------------------
SCHOOL_LEGACY_ID = 1101            # University of Georgia
DEPARTMENT_FILTER = "Computer Science"   # client-side match on teacher.department
OUTPUT_DIR = Path("rmp_data")
REQUEST_DELAY = 1.5                # seconds between requests -- be a good citizen
MAX_REVIEWS_PER_PROF = 100         # plenty for this project

# RMP's GraphQL endpoint + the public auth token its own frontend uses.
GRAPHQL_URL = "https://www.ratemyprofessors.com/graphql"
HEADERS = {
    "Authorization": "Basic dGVzdDp0ZXN0",   # base64("test:test") -- public, same for everyone
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (educational RAG project; low-volume)",
}

# RMP node IDs are base64 of "School-<id>" / "Teacher-<id>"
SCHOOL_NODE_ID = base64.b64encode(f"School-{SCHOOL_LEGACY_ID}".encode()).decode()

# ---- GraphQL queries --------------------------------------------------------
TEACHER_SEARCH_QUERY = """
query TeacherSearch($query: TeacherSearchQuery!, $count: Int!, $cursor: String) {
  newSearch {
    teachers(query: $query, first: $count, after: $cursor) {
      edges {
        node {
          id
          legacyId
          firstName
          lastName
          department
          avgRating
          avgDifficulty
          numRatings
          wouldTakeAgainPercent
        }
      }
      pageInfo { hasNextPage endCursor }
    }
  }
}
"""

RATINGS_QUERY = """
query Ratings($id: ID!, $count: Int!) {
  node(id: $id) {
    ... on Teacher {
      firstName
      lastName
      department
      ratings(first: $count) {
        edges {
          node {
            comment
            class
            date
            clarityRating
            difficultyRating
            helpfulRating
            grade
            wouldTakeAgain
            attendanceMandatory
            ratingTags
          }
        }
      }
    }
  }
}
"""


def gql(query, variables):
    """Single GraphQL POST with basic error surfacing."""
    resp = requests.post(
        GRAPHQL_URL,
        headers=HEADERS,
        json={"query": query, "variables": variables},
        timeout=30,
    )
    resp.raise_for_status()
    payload = resp.json()
    if "errors" in payload:
        raise RuntimeError(f"GraphQL errors: {payload['errors']}")
    return payload["data"]


def get_cs_teachers():
    """Paginate all teachers at the school, keep the ones in the target department."""
    teachers, cursor = [], None
    while True:
        variables = {
            "query": {"text": "", "schoolID": SCHOOL_NODE_ID, "fallback": True},
            "count": 1000,
            "cursor": cursor,
        }
        data = gql(TEACHER_SEARCH_QUERY, variables)
        block = data["newSearch"]["teachers"]
        for edge in block["edges"]:
            node = edge["node"]
            dept = (node.get("department") or "").strip()
            if DEPARTMENT_FILTER.lower() in dept.lower():
                teachers.append(node)
        page = block["pageInfo"]
        if not page["hasNextPage"]:
            break
        cursor = page["endCursor"]
        time.sleep(REQUEST_DELAY)
    return teachers


def get_reviews(teacher_node_id):
    data = gql(RATINGS_QUERY, {"id": teacher_node_id, "count": MAX_REVIEWS_PER_PROF})
    node = data["node"]
    if not node:
        return []
    return [e["node"] for e in node["ratings"]["edges"]]


def safe_filename(first, last):
    raw = f"{last}_{first}".lower()
    return re.sub(r"[^a-z0-9_]+", "_", raw).strip("_")


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    print(f"School node id: {SCHOOL_NODE_ID}  (legacy {SCHOOL_LEGACY_ID})")
    print(f"Finding '{DEPARTMENT_FILTER}' professors...")

    teachers = get_cs_teachers()
    print(f"Found {len(teachers)} matching professors total.")

    # keep only well-reviewed professors, capped at a manageable number
    MIN_RATINGS = 15
    KEEP_TOP_N = 12
    teachers = [t for t in teachers if (t.get("numRatings") or 0) >= MIN_RATINGS]
    teachers.sort(key=lambda t: t.get("numRatings") or 0, reverse=True)
    teachers = teachers[:KEEP_TOP_N]
    print(f"Keeping top {len(teachers)} by review count.\n")

    metadata = []
    for i, t in enumerate(teachers, 1):
        first, last = t["firstName"], t["lastName"]
        print(f"[{i}/{len(teachers)}] {first} {last}  ({t['numRatings']} ratings)")
        reviews = get_reviews(t["id"])
        time.sleep(REQUEST_DELAY)

        # write the human-readable .txt (this is what you'll chunk in Milestone 3)
        fname = safe_filename(first, last)
        txt_path = OUTPUT_DIR / f"{fname}.txt"
        lines = [f"Professor: {first} {last}",
                 f"Department: {t.get('department')}",
                 f"Overall rating: {t.get('avgRating')}  Difficulty: {t.get('avgDifficulty')}  "
                 f"Would take again: {t.get('wouldTakeAgainPercent')}%",
                 "=" * 60, ""]
        for r in reviews:
            comment = (r.get("comment") or "").strip()
            if not comment:
                continue
            course = r.get("class") or "N/A"
            lines.append(f"[Course: {course} | Quality: {r.get('clarityRating')} | "
                         f"Difficulty: {r.get('difficultyRating')} | Grade: {r.get('grade')}]")
            lines.append(comment)
            lines.append("")
        txt_path.write_text("\n".join(lines), encoding="utf-8")

        metadata.append({
            "first_name": first, "last_name": last,
            "department": t.get("department"),
            "legacy_id": t.get("legacyId"),
            "avg_rating": t.get("avgRating"),
            "avg_difficulty": t.get("avgDifficulty"),
            "num_ratings": t.get("numRatings"),
            "would_take_again_percent": t.get("wouldTakeAgainPercent"),
            "source_file": txt_path.name,
            "reviews": reviews,
        })

    (OUTPUT_DIR / "metadata.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )
    print(f"\nDone. {len(metadata)} professors written to {OUTPUT_DIR}/")
    print("Each .txt = one document for your RAG corpus; metadata.json has the structured fields.")


if __name__ == "__main__":
    main()