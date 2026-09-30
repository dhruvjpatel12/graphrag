````markdown
 GraphRAG — Knowledge Graph-Powered RAG

GraphRAG is a knowledge graph-based Retrieval-Augmented Generation system that I built to explore how LLMs can reason across connected information rather than simply retrieve similar text.

The system takes multiple documents, extracts entities and relationships using Google Gemini, stores them in Neo4j, and then converts natural-language questions into Cypher queries to retrieve the relevant graph context.

The final answer is generated from the retrieved graph data and includes the source documents used for the response.

## What it can do

- Extract entities and relationships from multiple documents
- Build and maintain a knowledge graph using Neo4j
- Convert natural-language questions into Cypher queries
- Perform multi-hop reasoning across connected entities
- Retrieve information across multiple documents
- Track source documents associated with retrieved entities
- Generate concise answers using Google Gemini
- Provide an interactive chat-based web interface

## How it works

```text
Documents
    ↓
Gemini Entity & Relationship Extraction
    ↓
Neo4j Knowledge Graph
    ↓
User Question
    ↓
Gemini → Cypher Generation
    ↓
Neo4j Graph Retrieval
    ↓
Graph Context + Sources
    ↓
Gemini Answer Generation
    ↓
Answer + Sources
````

For example, given:

```text
Elon Musk founded SpaceX.
SpaceX developed Falcon 9.
Falcon 9 is a reusable orbital launch vehicle.
```

The system can answer:

> Who founded the company that developed Falcon 9?

by traversing:

```text
Elon Musk
     │
   founded
     ↓
  SpaceX
     │
  developed
     ↓
 Falcon 9
```

and returning:

```text
Elon Musk founded SpaceX.
Source: spacex.txt
```

## Tech Stack

* **Python** — Core application and data processing
* **Google Gemini** — Entity extraction, Cypher generation and answer generation
* **Neo4j** — Knowledge graph storage and traversal
* **FastAPI** — Backend API
* **HTML, CSS, JavaScript** — Frontend
* **Cypher** — Graph query language
* **Git & GitHub** — Version control

## Project Structure

```text
graphrag/
│
├── BackEnd/
│   ├── app.py
│   ├── build_graph.py
│   ├── extract_graph.py
│   ├── graph.py
│   ├── ingest.py
│   └── query_graph.py
│
├── FrontEnd/
│   ├── index.htm
│   ├── Script.js
│   └── Style.css
│
├── documents/
│   ├── company.txt
│   ├── nasa.txt
│   ├── spacex.txt
│   └── starship.txt
│
├── .gitignore
└── README.md
```

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/dhruvjpatel12/graphrag.git
cd graphrag
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install neo4j google-genai fastapi uvicorn
```

### 4. Configure environment variables

Set your Gemini API key:

```bash
export GEMINI_API_KEY="your_gemini_api_key"
```

Set your Neo4j password:

```bash
export NEO4J_PASSWORD="your_neo4j_password"
```

Make sure Neo4j is running locally.

```bash
brew services start neo4j
```

Neo4j Browser:

`http://localhost:7474`

### 5. Build the knowledge graph

From the project root:

```bash
python BackEnd/ingest.py
```

This processes the documents in `documents/`, extracts entities and relationships, and stores them in Neo4j.

### 6. Start the backend

```bash
python -m uvicorn BackEnd.app:app --reload --port 8001
```

### 7. Start the frontend

Open another terminal:

```bash
python -m http.server 5500 --directory FrontEnd
```

Then open:

`http://localhost:5500`

## Example Questions

Try asking:

```text
Which company developed Falcon 9?
```

```text
Who founded the company that developed Falcon 9?
```

```text
What spacecraft did SpaceX develop for future Moon and Mars missions?
```

```text
What is NASA's relationship with Falcon 9?
```

The interesting part is that the system can answer questions that require following multiple relationships in the graph rather than relying on a single text match.

## Knowledge Graph Model

The current graph uses two main node types:

```text
(:Entity)
(:Document)
```

Entities are connected through relationships such as:

```text
(:Entity)-[:RELATED {type: "founded"}]->(:Entity)

(:Entity)-[:RELATED {type: "developed"}]->(:Entity)

(:Entity)-[:RELATED {type: "launches"}]->(:Entity)
```

Documents are connected to the entities they contain:

```text
(:Document)-[:MENTIONS]->(:Entity)
```

## Why GraphRAG?

Traditional RAG is very effective when the answer exists directly inside a relevant text chunk. However, some questions require connecting several pieces of information.

For example:

```text
Who founded the company
that developed the rocket
used to launch a particular project?
```

A knowledge graph makes those relationships explicit and allows the system to traverse them before generating the final response.

This project was built as a practical exploration of that idea — combining LLMs with structured graph reasoning and document retrieval.

## What's Next

Some of the areas I plan to explore next include:

* Hybrid Graph + Vector retrieval
* Chunk-level provenance
* Interactive knowledge graph visualization
* Better entity and relationship extraction
* Cypher query validation
* Graph-based context ranking
* Streaming responses
* GraphRAG evaluation and benchmarking

## Author

**Dhruv Patel**

Data Science Engineering | AI & Data Engineering

GitHub: [https://github.com/dhruvjpatel12](https://github.com/dhruvjpatel12)

```
```
