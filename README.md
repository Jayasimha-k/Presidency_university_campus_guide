# Presidency University Campus Guide

A local Streamlit campus information app using the two supplied route knowledge files, persistent ChromaDB retrieval, Sentence Transformers embeddings, optional Groq answers, and editable image metadata. The files are preserved unmodified under `knowledge_base/`.

## Setup and launch

On Windows, double-click `start.bat`. It creates a local virtual environment, installs the requirements the first time, and starts the app in your browser. Keep the command window open while you use the app; close it to stop the server. Python 3.10 or newer and an internet connection are required for first-time setup.

To start it manually:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

The first index may download `sentence-transformers/all-MiniLM-L6-v2` and may take a few minutes. Use **Index / refresh campus files** in the sidebar after changing knowledge files. ChromaDB persists under `data/chroma_db/`.

## Configuration

Add a valid Groq API key to the ignored local `.env` file as `GROQ_API_KEY=...`. `GROQ_MODEL` defaults to `openai/gpt-oss-120b`; change it in `.env` if needed. The application uses Groq's OpenAI-compatible chat completions endpoint and never displays the key.

## Campus images

The `picture/` folder already contains campus photos. Campus Explorer displays at most one best-matching photo; AI Campus Assistant does not show photos; Campus Navigation displays matching route-stop photos in order and the destination photo last. Photos can be matched against filenames automatically (for example, **gym** finds `gym.jpeg`). To provide a more specific title, location, keywords, or description, add metadata for that exact filename in `data/image_metadata.json`, for example:

```json
{"images":[{"filename":"example.jpg","title":"Verified title","location":"Verified location","keywords":["verified keyword"],"description":"Verified description"}]}
```

The example is a schema illustration, not actual campus image information. User-provided metadata overrides the filename-based title and keywords.

## Routes and limitations

The supplied text files are the route sources. Add future route text files as `.txt` files in `knowledge_base/` and use **Index / refresh campus files** to include them. Their contents can overlap or differ in certainty. Campus Navigation searches for a single document that explicitly includes both the requested origin and destination. It does not combine route records, infer pathways, calculate distances, or run shortest-path routing. Route text marked “Verify” remains caveated and should be confirmed on campus. No distance values, evaluation scores, or route graph are bundled.

## Using the modules

Campus Explorer uses Groq to summarize retrieved location and facility information in natural language; the original matching passages remain available under **Retrieved campus sources**. Campus Navigation asks Groq to explain a route only after finding a source record that explicitly mentions both endpoints, and shows the matching route records for verification. The About page also lets you ask Groq questions about the guide itself. These answers require a working Groq API key and stay grounded in the context shown to the model.

## Modules and architecture

The `modules/module_registry.py` registry powers sidebar navigation and dashboard module cards. To add a module, implement a renderer in `modules/`, import/register it in the registry, and add its renderer to `PAGES` in `app.py`.

Flow: User → Streamlit → Sentence Transformer embeddings → persistent ChromaDB retrieval → relevant source context → optional Groq API → answer and metadata-matched images. Sentence Transformers are used for semantic embeddings, not translation or fine-tuning.

## Evaluation

`data/evaluation_questions.json` is an unscored case template. Retrieval Precision@K and Recall@K can be calculated against reviewed references; correctness, faithfulness, relevance, and image relevance need human review. Route success rate is inapplicable until verified route graph and route tests exist. No evaluation has been performed or claimed.
