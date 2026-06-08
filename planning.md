# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

I plan to collect student reviews of Computer Science professors @ University of Georgia, collected from Rate My Professors. Its hard to find officialy since the UGA course catalog tells you a class exists and who teaches it, but never what the professor requires or what to expect from their course. That experiences only exists in student reviews whom have previously taken it.
---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 |Ratemyprofessor|Barnes' RMP reviews, ratings, & courses taught|rmp_data/barnes_brad.txt|
| 2 |Ratemyprofessor|Cotterell's RMP reviews, ratings, & courses taught|rmp_data/cotterell_michael.txt|
| 3 |Ratemyprofessor|Funk's RMP reviews, ratings, & courses taught|rmp_data/funk_shelby.txt|
| 4 |Ratemyprofessor|Hollingsworth's RMP reviews, ratings, & courses taught|rmp_data/hollingsworth_bill.txt|
| 5 |Ratemyprofessor|Hybinette's RMP reviews, ratings, & courses taught|rmp_data/hybinette_maria.txt|
| 6 |Ratemyprofessor|Keshtgari's RMP reviews, ratings, & courses taught|rmp_data/keshtgari_manijeh.txt|
| 7 |Ratemyprofessor|Lamarca's RMP reviews, ratings, & courses taught|rmp_data/lamarca_salvatore.txt|
| 8 |Ratemyprofessor|Lian's RMP reviews, ratings, & courses taught|rmp_data/lian_yiheng.txt|
| 9 |Ratemyprofessor|Meena's RMP reviews, ratings, & courses taught|rmp_data/meena_sachin.txt|
| 10 |Ratemyprofessor|Menik's RMP reviews, ratings, & courses taught|rmp_data/menik_sami.txt|
| 11 |Ratemyprofessor|Peng's RMP reviews, ratings, & courses taught|rmp_data/peng_hao.txt|
| 12 |Ratemyprofessor|Saleh's RMP reviews, ratings, & courses taught|rmp_data/saleh_eman.txt|

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:** 1 review = 1 chunk (~300-500 character typically; reviews longer than that are split at a sentence boundary)

**Overlap:** Minimal, reviews tend to not continue across boundaries and each one is already complete

**Reasoning:** Fixed-size splitting would slice mid-review and only demonstrate half an opinion; review-level chunks keep each opinion intact and matchable. That's also why I'll keep the professor name attached either to the metadata or prepended header.

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:** all-MiniLM-L6-v2

**Top-k:** Start at 5

**Production tradeoff reflection:** MiniLM is fast & free, which is fine for my case. If I needed multilingual support or better accuracy on domain jargon like course codes, then I'll need to weigh a larger model. I traded those perks against latency/per-query cost.

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 |What do students say about Brad Barnes's use of extra credit in CSCI 1302?|He gives a lot of extra credit — points for submitting projects early (often +10) and for in-class polls/attendance. Multiple reviews say it makes an A very achievable.|
| 2 |Does Salvatore LaMarca test students on the Unix manual in CSCI 1730?|Yes — multiple reviews complain he asks for specific page/section numbers from the Unix manual on the midterm and final. |
| 3 |Why do students give Shelby Funk low ratings?|Flipped classroom with little in-person teaching, excessive "busywork" (worksheets, defense summaries), slow grading, and being hard to reach by email.|
| 4 |Between Barnes and Cotterell for CSCI 1302, do students say the choice matters?|Mixed but leans toward "not much" — several reviews say both are excellent and the assignments/deadlines are shared, though some find Barnes's lectures more engaging and Cotterell's a bit drier.|
| 5 |What are Professor Hao Peng's office hours, and what room is the class in?|"I don't have enough information." Reviews discuss teaching style, not schedules or room numbers — this should be unanswerable.|

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. Professor attribution, if a chunk is a lone review, the professor's name may not be in the review text, so retrieval could surface the right opinion attached to the wrong person unless the metadata is wired correctly.

2. Sparse/noisy reviews, some reviews are vague and carry little weight (like just saying "great professor!") which can pollute retreival. There also may be some troll/conflicting reviews, which makes "the" answer ambiguous.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->
┌─────────────┐   ┌──────────┐   ┌──────────────────┐   ┌───────────┐   ┌────────────┐
│  Document   │   │ Chunking │   │   Embedding +    │   │ Retrieval │   │ Generation │
│  Ingestion  │──▶│         │──▶│   Vector Store   │──▶│          │──▶│            │
│             │   │ 1 review │   │ all-MiniLM-L6-v2 │   │  top-k=5  │   │  Groq      │
│ RMP GraphQL │   │ = 1 chunk│   │   → ChromaDB     │   │  semantic │   │ llama-3.3  │
│ → .txt files│   │          │   │  (+ metadata)    │   │  search   │   │  -70b      │
└─────────────┘   └──────────┘   └──────────────────┘   └───────────┘   └────────────┘
---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:** The tool I'll use is Claude, and I'll give my Chunking strategy/Documents section as the input. I want it to produce the chunk_text() function that creates one chunk per review and I'll print a confirmation to check if the review appears exactly once, and that the professor remains attached to every chunk (also will print out chunk counts).

**Milestone 4 — Embedding and retrieval:** The tool I'll use is Claude, and I'll give my Retrieval Approach section & architecture diagram. I expect it to produce retrieval functions that return the top 5 most relevant chunks for a query, and the retrieval output inclduing similarity scores/chunk metadata. I'll check by confirming that relevant reviews appear in the top results, and that retrieved chunks correspond to the correct professor.

**Milestone 5 — Generation and interface:** I'll also be using Claude, and I'll provide my eval plan & architecture diagram with the requirements. I expect the output to provide a prompt tempalte for RAG, code that combines retrieved chunks into a context window. I'll verify by comparing the generated answers against the expected answers in the Eval plan and confirm if unasnwerable questions doesn't result in hallucinated facts.
