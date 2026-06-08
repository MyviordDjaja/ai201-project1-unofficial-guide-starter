# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

<!-- What topic or category of knowledge does your system cover?
     Why is this knowledge valuable, and why is it hard to find through official channels?
     Example: "Student reviews of CS professors at [university] — useful because official
     course descriptions don't reflect teaching style, exam difficulty, or workload." -->
I plan to collect student reviews of Computer Science professors @ University of Georgia, collected from Rate My Professors. Its hard to find officially since the UGA course catalog tells you a class exists and who teaches it, but never what the professor requires or what to expect from their course. That experience only exists in student reviews whom have previously taken it.
---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

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

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:** One review per chunk (Typically ~300-500 characters, longer ones split at sentence boundaries)

**Overlap:** None, each review is already a complete, self-contained opinion so there's nothing to bridge across boundaries

**Why these choices fit your documents:** Fixed-size splitting would slice mid-review and only demonstrate half an opinion; review-level chunks keep each opinion intact and matchable.

**Final chunk count:** 1120 chunks

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:** all-MiniLM-L6-v2 via sentence-transformers, run locally through ChromaDB's embedding function, cosine distance.

**Production tradeoff reflection:** MiniLM was fast, free, and gave me on-topic retrieval with distances mostly 0.2-0.4; A real deployment would weight a larger model for better handling of domain jargon & multilingual reviews, traded against latency and per-query API cost.

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:** The system prompt commands answers from provided context ONLY, forbids outside knowledge, and mandates the exact refusal string when context is thin.

**How source attribution is surfaced in the response:** The sources list is built programmatically by deduplicating professor names from retrieved chunk metadata, which isn't generated by LLM. This means it can't be hallucinated

**Note:** There is temperature=0 keeps the model from drifting creatively toward training data; There is also an if not hits short-circuit returns the refusal without calling the LLM when retrieval is empty.

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 |What do students say about Brad Barnes's use of extra credit in CSCI 1302?|Lots of extra credit — early-project submissions (often +10) and in-class polls; makes an A achievable|Summarized that Barnes gives heavy extra credit via early submissions and polls; cited Barnes|Relevant|Accurate|
| 2 |Does Salvatore LaMarca test students on the Unix manual in CSCI 1730?|Yes — reviews cite exam questions asking for specific manual page/section numbers|Confirmed yes, citing the page-number exam complaints; cited LaMarca|Relevant|Accurate|
| 3 |Why do students give Shelby Funk low ratings?|Flipped classroom with little teaching, heavy busywork, slow grading, hard to reach|Listed busywork, harsh/slow grading, poor communication; cited Funk|Relevant|Accurate|
| 4 |Between Barnes and Cotterell for CSCI 1302, do students say the choice matters?|Mixed, leans "not much" — both well-regarded, shared assignments|Balanced answer: most say either is fine, noted one dissent; cited both|Relevant|Accurate|
| 5 |What are Hao Peng's office hours and what room is the class in?|Should refuse — reviews don't cover schedules|Returned exact refusal string; no fabrication|Partially Relevant|Accurate|

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:** Which professor gives the most extra credit?

**What the system returned:** The system noted Barnes and Cotterell both give extra credit, then refused to pick a "most."

**Root cause (tied to a specific pipeline stage):** A superlative query needs corpus-wide comparison, but top-k=5 plus review-level chunking and uneven document sizes means the most-reviewed professors monopolize the five retrieved chunks — professors with fewer reviews never entered the context, so the model reasoned correctly over a biased sample.

**What you would change to fix it:** Higher k for aggregate queries, or metadata-aware retrieval that samples across professors rather than by raw similarity.

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:** The chunking decision of having one review = one chunk w/ name attached helped me get the code for my chunk_text() that fit the first time, and my #1 anticipated risk (attribution) was solved structurally. Because I already decided the chunking rule in advance, my prompt to the AI was specific enough that my file matched my intent on the first try without needed any rewrite.

**One way your implementation diverged from the spec, and why:** My spec said that name would go in metadata or a prepended header, but I did both (metadata for clean attribution & prepend so the embedding matches professor-specific queries).

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:* I'm building a RAG pipeline. Write me a chunk_text() function (Python) that reads from metadata.json — a list of professor objects, each with first_name, last_name, department, avg_rating, and a reviews list where each review has comment, class, grade, clarityRating, difficultyRating.
Chunking rule: one chunk per review. For each review: run html.unescape() on the comment, skip empty/whitespace-only comments, and prepend the professor name and course into the chunk text like "Professor Brad Barnes (CSCI1302): <comment>". Also store professor name, course, and grade as separate metadata on each chunk. Return a list of dicts with text and metadata keys.
At the end, print the total chunk count and 5 sample chunks so I can inspect them.
- *What it produced:* Check chunk_text.py (it had a few things which I overwritten, described down below)
- *What I changed or overrode:* The first version defaulted to the wrong file path (had metadata.json instead of rmp_data/metadata.json), which I corrected. I also added the None-metadata filter and chunk-id/position myself.

**Instance 2**

- *What I gave the AI:* Alright, I'm moving to milestone 4. Heres the next prompt for you to do.

I'm building the retrieval stage of a RAG pipeline. I already have a chunk_text() function that returns a list of {"text": str, "metadata": dict} dicts (metadata has keys: chunk_id, source, position, professor, department, course, and sometimes grade/clarity_rating/difficulty_rating).
Write Python that:

    Sets up a persistent ChromaDB client (so embeddings survive between runs, not in-memory).
    Configures Chroma's embedding function to use all-MiniLM-L6-v2 via sentence-transformers (SentenceTransformerEmbeddingFunction).
    Creates/gets a collection and adds all chunks — passing documents= (the text), metadatas= (the metadata dict), and ids= (use the chunk_id from metadata). Handle the case where the collection already exists so re-running doesn't duplicate or crash.

    Provides a retrieve(query, k=5) function that returns the top-k chunks with their text, metadata, and distance scores.
    At the bottom, run retrieve() on these three test queries and print each returned chunk's text, professor, and distance score:
    "Does Salvatore LaMarca test students on the Unix manual?"
    "Which professor gives a lot of extra credit?"
    "Why do students dislike Shelby Funk?"
- *What it produced:* It wrote up retrieve.py (with some few modifications that I made.)
- *What I changed or overrode:* Similar to the previous instance, however I didn't really overrode much this time. I only changed the packages "from chunk_text import chunk_text", since they had a different name for it "from chunker". This would have resulted in an error.

---

## Sample Chunks

--- Sample 1 ---
text:     Professor Salvatore Lamarca (CSCI1730): The exams will test both your knowledge and your mental fortitude. However! The projects and weekly assignments are easy so long as you follow all instructions. Attend class or else. Still, he gives the answers to each in-class activity.
metadata: {'chunk_id': 'Salvatore_Lamarca__CSCI1730__0', 'source': 'Salvatore Lamarca', 'position': 0, 'professor': 'Salvatore Lamarca', 'department': 'Computer Science', 'course': 'CSCI1730', 'grade': 'B', 'clarity_rating': 3, 'difficulty_rating': 3}

--- Sample 2 ---
text:     Professor Brad Barnes (CSCI1302): Great professor! Chill, knowledgeable, and respectful. Make sure you do the readings from the (free, online) textbook!
metadata: {'chunk_id': 'Brad_Barnes__CSCI1302__0', 'source': 'Brad Barnes', 'position': 0, 'professor': 'Brad Barnes', 'department': 'Computer Science', 'course': 'CSCI1302', 'grade': 'A', 'clarity_rating': 5, 'difficulty_rating': 4}

--- Sample 3 ---
text:     Professor Sami Menik (4370): he's on a similar level to cotterell imo, but he types so fast that it can be hard to keep up with class activities even when paying attention. lectures could be slow and boring. exams are fine if you pay enough attention and attend class reviews. projects felt like they were testing your knowledge of java not databases. pick your group carefully
metadata: {'chunk_id': 'Sami_Menik__4370__0', 'source': 'Sami Menik', 'position': 0, 'professor': 'Sami Menik', 'department': 'Computer Science', 'course': '4370', 'grade': 'Not sure yet', 'clarity_rating': 3, 'difficulty_rating': 4}

--- Sample 4 ---
text:     Professor Shelby Funk (CSCI4470): Bismillah, do not take. Thank allah she is retiring.
metadata: {'chunk_id': 'Shelby_Funk__CSCI4470__0', 'source': 'Shelby Funk', 'position': 0, 'professor': 'Shelby Funk', 'department': 'Computer Science', 'course': 'CSCI4470', 'grade': 'Drop/Withdrawal', 'clarity_rating': 1, 'difficulty_rating': 5}

--- Sample 5 ---
text:     Professor Maria Hybinette (CS1730): Labs every week, HW every few weeks. Our HW kept getting pushed back so we had way less than what we were originally supposed to. This can either be a good or bad thing depending on how well you did on the HW because HW is worth 50%. Overall not a bad prof. I bombed the midterm but am still doing fine since I'm good at the labs and HW.
metadata: {'chunk_id': 'Maria_Hybinette__CS1730__35', 'source': 'Maria Hybinette', 'position': 35, 'professor': 'Maria Hybinette', 'department': 'Computer Science', 'course': 'CS1730', 'grade': 'Not sure yet', 'clarity_rating': 3, 'difficulty_rating': 3}

---

## Retrieval test Results

=== Query: Does Salvatore LaMarca test students on the Unix manual? ===

[1] Salvatore Lamarca  (distance: 0.315)
    Professor Salvatore Lamarca (CSCI1730): Occasionally tests for irrelevant knowledge - always tests for intimate knowledge. One MCQ read, "What command was page X of the manual?". Wants his students to come to class, but instead of taking attendance, just doesn't upload material. One of his favorite pastimes is drinking students' tears on RMP and writing/coaxing fake reviews.

[2] Salvatore Lamarca  (distance: 0.320)
    Professor Salvatore Lamarca (CSCI1730): Dr. LaMarca lacks in sympathy. Never met a professor that went so out of his own way to be as difficult as possible on the students. Very questionable grading criteria and tests. Asked random memorization questions such as "which page a command could be found in the C manual."

[3] Salvatore Lamarca  (distance: 0.328)
    Professor Salvatore Lamarca (CSCI1730): I've never had a professor who wants to see his students fail as much as this dude. To give you an idea of what I mean, his midterm and final had questions asking for us to recall specific section / page numbers in the Unix User manual. And he was a crashout.

All three top results are LaMarca reviews independently describing the Unix-manual page-number exam questions, with distances 0.31-0.33, tightly on topic & correctly attributed.
---

## Query Interface

This will also be shown in the video, which is much visually better. 

The Gradio UI consists of a question textbox, where you can ask your question. It has an "Ask button", which when pressed, gives an Answer output alongside a "Retrieved from (professors)" sources output in the last two text boxes. An example is this:

Does Salvatore LaMarca test students on the Unix manual?

Yes, according to the reviews, Salvatore LaMarca tests students on the Unix manual. Review 3 mentions that the midterm and final had questions asking for students to recall specific section/page numbers in the Unix User manual. Additionally, Review 5 mentions that he brings up the Unix manual once every class, implying that it is a topic of focus. Review 2 also mentions a question about the page a command could be found in the C manual, but Review 3 and Review 1 (which mentions "page X of the manual") specifically reference the Unix manual or a manual in general.

• Salvatore Lamarca