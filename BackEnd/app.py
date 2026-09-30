from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import json

from neo4j import GraphDatabase
from google import genai


# -----------------------------
# App
# -----------------------------

app = FastAPI(title="GraphRAG")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------
# Gemini
# -----------------------------

client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"]
)


# -----------------------------
# Neo4j
# -----------------------------

driver = GraphDatabase.driver(
    "neo4j://localhost:7687",
    auth=("neo4j", "Patel@123")
)


# -----------------------------
# Request model
# -----------------------------

class Question(BaseModel):
    question: str


# -----------------------------
# Query endpoint
# -----------------------------

@app.post("/ask")
def ask_question(data: Question):

    question = data.question

    prompt = f"""
You are a Neo4j Cypher expert.

Convert the user's question into a Cypher query.

DATABASE SCHEMA:

Nodes:
(:Entity)
(:Document)

Entity properties:
- name
- type

Document properties:
- name

Entity relationships:
[:RELATED {{type: "founded"}}]
[:RELATED {{type: "developed"}}]
[:RELATED {{type: "launches"}}]

Document relationship:
(:Document)-[:MENTIONS]->(:Entity)

IMPORTANT:
Always use [:RELATED {{type: "..."}}].
Never use [:founded], [:developed], or [:launches].

If the question asks about factual information, also retrieve
the documents that mention the relevant entities.

Example:

MATCH (person:Entity)-[:RELATED {{type: "founded"}}]->(company:Entity)
      -[:RELATED {{type: "developed"}}]->(rocket:Entity)
WHERE rocket.name = "Falcon 9"

OPTIONAL MATCH (doc:Document)-[:MENTIONS]->(person)

RETURN person.name AS founder,
       collect(DISTINCT doc.name) AS sources

Return ONLY the Cypher query.

Question:
{question}
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    cypher = response.text.strip()

    cypher = (
        cypher
        .replace("```cypher", "")
        .replace("```", "")
        .strip()
    )

    # Execute query
    with driver.session() as session:

        result = session.run(cypher)

        records = [
            record.data()
            for record in result
        ]

    # Generate answer
    context = json.dumps(records)

    answer_prompt = f"""
Answer the user's question using ONLY the graph results below.

Question:
{question}

Graph results:
{context}

Return ONLY valid JSON:

{{
    "answer": "concise natural language answer",
    "sources": ["document1.txt", "document2.txt"]
}}

Do not mention Cypher.
Do not mention Neo4j.
"""

    answer_response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=answer_prompt
    )

    answer_text = answer_response.text.strip()

    answer_text = (
        answer_text
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )

    try:
        final_answer = json.loads(answer_text)
    except json.JSONDecodeError:

        final_answer = {
            "answer": answer_text,
            "sources": []
        }

    return {
        "question": question,
        "answer": final_answer.get("answer", ""),
        "sources": final_answer.get("sources", []),
        "cypher": cypher
    }