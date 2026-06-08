import os

import gradio as gr
from dotenv import load_dotenv
from groq import Groq

from retrieve import retrieve  # wherever your retrieve() lives

load_dotenv()

client = Groq(api_key=os.environ["GROQ_API_KEY"])
MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are a question-answering assistant for student reviews of UGA professors.

Answer the question using ONLY the information in the provided review context below. \
Follow these rules strictly:
- Base your answer solely on the provided reviews. Do not use any outside or general knowledge.
- Do not infer, guess, or fill in details that are not present in the context.
- If the context does not contain enough information to answer the question, respond with \
exactly this sentence and nothing else: "I don't have enough information on that."
- When the context does support an answer, be specific and cite what students actually said."""

NO_INFO = "I don't have enough information on that."


def format_context(hits):
    """Turn retrieved chunks into a numbered context block for the prompt."""
    blocks = []
    for i, hit in enumerate(hits, start=1):
        meta = hit["metadata"]
        prof = meta.get("professor", "Unknown")
        course = meta.get("course", "")
        header = f"[Review {i}] {prof}" + (f" ({course})" if course else "")
        blocks.append(f"{header}\n{hit['text']}")
    return "\n\n".join(blocks)


def ask(question, k=5):
    """Retrieve context, generate a grounded answer, return answer + sources."""
    hits = retrieve(question, k=k)

    # No retrieved context at all → don't even call the LLM.
    if not hits:
        return {"answer": NO_INFO, "sources": []}

    # Deduplicate professor names, preserving retrieval order. Built from
    # metadata, NOT from the model's output, so sources can't be hallucinated.
    sources = []
    for hit in hits:
        prof = hit["metadata"].get("professor")
        if prof and prof not in sources:
            sources.append(prof)

    context = format_context(hits)
    user_message = (
        f"Review context:\n\n{context}\n\n"
        f"Question: {question}\n\n"
        f"Answer using only the reviews above."
    )

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0,  # deterministic, keeps it close to the source text
    )
    answer = response.choices[0].message.content.strip()

    return {"answer": answer, "sources": sources}


def handle_query(question):
    if not question or not question.strip():
        return "Please enter a question.", ""
    result = ask(question)
    sources = "\n".join(f"• {s}" for s in result["sources"])
    return result["answer"], sources


if __name__ == "__main__":
    with gr.Blocks() as demo:
        gr.Markdown("## UGA Professor Reviews — Ask a Question")
        inp = gr.Textbox(label="Your question", placeholder="e.g. How are Professor Funk's exams?")
        btn = gr.Button("Ask")
        answer = gr.Textbox(label="Answer", lines=8)
        sources = gr.Textbox(label="Retrieved from (professors)", lines=4)

        btn.click(handle_query, inputs=inp, outputs=[answer, sources])
        inp.submit(handle_query, inputs=inp, outputs=[answer, sources])

    demo.launch()