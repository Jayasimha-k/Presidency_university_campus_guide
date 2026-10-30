# Presidency University Transport Assistant (RAG Chatbot)

A Retrieval-Augmented Generation (RAG) chatbot that answers Presidency University students' transport questions: which bus serves their area, pickup times, annual fees, how to change a route, how to pay on Linways, and who to contact.

Built for the GenAI course (International Teaching Week).

## Problem
Transport information is scattered across Excel sheets, the Linways portal, circulars and the academic calendar. Students struggle to find the right route, fee, pickup time, or the process to change a route.

## Features
- Route, boarding point, pickup time and annual fee lookup (typo tolerant, e.g. "kodigehali circle")
- Route-level summaries with seats remaining (snapshot)
- Linways login and fee payment steps, and the route change process
- Transport help desk and university contacts
- Academic holidays and the full 2026-27 academic calendar
- Driver details from the June transport sheet (optional, see Data)
- "I don't know" handling: no guessing of drop timings, bus service on holidays, live tracking or an emergency number; it points students to the transport help desk

## Architecture
```
Excel workbook (routes, fees, drivers, policies, contacts, calendar)
        |
   cleaning + chunking
   (one chunk per stop / route / event; recursive chunking for documents)
        |
   embeddings: BAAI/bge-small-en-v1.5  ->  Chroma vector DB
   keyword index: BM25
        |
   hybrid search (reciprocal rank fusion) + exact stop lookup + query routing
        |
   LLM: Qwen (Groq) answers ONLY from the retrieved context, with source and date
        |
   Gradio chat UI
```

| Stage | Technique |
|---|---|
| Chunking | One chunk per stop and route; recursive chunking (LangChain) for documents |
| Embeddings | BAAI/bge-small-en-v1.5 (384-dim, cosine similarity) |
| Vector DB | ChromaDB |
| Search | Hybrid: semantic + BM25 keyword, combined with reciprocal rank fusion |
| Extras | Exact stop lookup with fuzzy matching (RapidFuzz); routing for holiday and emergency/contact questions |
| LLM | Qwen3.8-27B on Groq (fallback: gpt-oss-20b); Qwen2.5-7B-Instruct (4-bit, local) used for experiments |
| UI | Gradio |

## Data
All data is in `data/transport_chatbot_data.xlsx` (one sheet per source):

| Sheet | Content | Source |
|---|---|---|
| Portal_Routes_Fees | 61 routes, 290 boarding points, pickup time, annual fee, seats remaining | Linways Bus Routes Details (copied 29 Oct 2026) |
| Excel_Routes_Drivers | 22 routes, pickup points, times, driver names and mobile numbers (older route numbering) | Transport department Excel (8th-30th June) |
| Operating_Hours_Policies, Fee_Payment_Steps, Route_Change | Hours, fee rules, Linways steps, route change process | Transport knowledge base and route change instructions |
| Contacts | Transport help desk, board lines, grievance, ombudsman, admission desks | University contacts |
| Holidays, Academic_Calendar | 22 holidays and the full 2026-27 calendar | Academic Calendar 2026-27 |
| Info_Not_Confirmed, Data_Notes | What the bot must not guess, and data quality observations | Compiled |

`data/portal_routes.txt` is the raw portal text the route sheet was built from.

**Verification:** [add who in the transport office confirmed the data, and on which date]

**Privacy note:** driver names and phone numbers are included only if the university authorizes sharing them. Set `INCLUDE_DRIVERS = False` in the notebook to exclude them.

### Data quality notes
- Two route numbering systems: the June sheet uses routes 1-22, the portal uses R-1 to R-37 (with A/B/C variants)
- The same stop appears with two fees on R-15 (Kodigehalli Sterling Apts: Rs 39,000 and Rs 40,000)
- Stop-name variants and typos (e.g. SHANTHINAGAR / Shanti Nagar, Hunsemarenahalli)
- Pickup times such as 06:54:59 are rounded to 6:55 AM
- Drop times are missing for all 290 stops
- Seats remaining changes daily; stored as a snapshot with a date

## How to run
1. Open `transport_chatbot_final.ipynb` in Google Colab.
2. Add your Groq key as a Colab Secret named `GROQ_API_KEY` (key icon in the left sidebar). Never paste it into the notebook.
3. Run the cells top to bottom. When asked, upload `data/transport_chatbot_data.xlsx`.
4. The Gradio cell prints a public link to the chat UI.

Install requirements locally with `pip install -r requirements.txt` if you are not using Colab.

## Evaluation
`eval/eval_questions.csv` contains 45 student-style questions (stop fees and times, routes, procedures, policies, contacts, calendar, typos, aggregate questions, and questions the bot must not answer). The last notebook cells compare retrieval and answer accuracy across configurations.

### Results
[Fill in after running the evaluation cells]

| Configuration | Retrieval hit rate | Answer accuracy |
|---|---|---|
| Semantic only | | |
| Keyword only (BM25) | | |
| Hybrid | | |
| Hybrid + stop lookup + routing | | |

### What failed and what we improved
[Fill in: failure cases from the evaluation and the fix for each]

## Limitations and future work
- Drop timings, evening schedule and live bus tracking are not available in the data
- No dedicated emergency number has been provided yet
- Seats remaining is a snapshot, not live
- Route numbers in the June sheet and the portal are not mapped to each other
- Add images (Linways screenshots, route map) with image retrieval
- Kannada language support

## Team
[Add names]

Course: GenAI, Presidency University, Bengaluru
