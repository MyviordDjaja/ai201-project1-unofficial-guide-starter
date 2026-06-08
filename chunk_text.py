import html
import json


def chunk_text(metadata_path="rmp_data/metadata.json"):
    """One chunk per non-empty review. Returns [{"text", "metadata"}]."""
    with open(metadata_path, "r", encoding="utf-8") as f:
        professors = json.load(f)

    chunks = []
    for prof in professors:
        first = (prof.get("first_name") or "").strip()
        last = (prof.get("last_name") or "").strip()
        prof_name = f"{first} {last}".strip()
        department = (prof.get("department") or "").strip()

        position = 0  # index of this review within this professor's reviews
        for review in prof.get("reviews", []):
            comment = html.unescape(review.get("comment") or "").strip()
            if not comment:
                continue  # skip empty / whitespace-only comments

            course = (review.get("class") or "").strip()

            text = f"Professor {prof_name} ({course}): {comment}"

            metadata = {
                "chunk_id": f"{prof_name}__{course}__{position}".replace(" ", "_"),
                "source": prof_name,        # which professor "document" this came from
                "position": position,       # position within that document
                "professor": prof_name,
                "department": department,
                "course": course,
                "grade": review.get("grade"),
                "clarity_rating": review.get("clarityRating"),
                "difficulty_rating": review.get("difficultyRating"),
            }
            # ChromaDB rejects None-valued metadata — drop missing fields
            metadata = {k: v for k, v in metadata.items() if v is not None}

            chunks.append({"text": text, "metadata": metadata})
            position += 1

    return chunks


if __name__ == "__main__":
    chunks = chunk_text()
    print(f"Total chunks: {len(chunks)}\n")
    for i, chunk in enumerate([chunks[0], chunks[200], chunks[500], chunks[800], chunks[1000]], start=1):
        print(f"--- Sample {i} ---")
        print("text:    ", chunk["text"])
        print("metadata:", chunk["metadata"])
        print()