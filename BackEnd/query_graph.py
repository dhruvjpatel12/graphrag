import os
import json
from neo4j import GraphDatabase
from google import genai


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
# User question
# -----------------------------

question = input("Ask a question: ")


# -----------------------------
# Generate Cypher
# -----------------------------

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

Question:
Who founded the company that developed Falcon 9?

Correct Cypher:

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


# -----------------------------
# Clean generated Cypher
# -----------------------------

cypher = response.text.strip()

cypher = (
    cypher
    .replace("```cypher", "")
    .replace("```", "")
    .strip()
)


print("\nGenerated Cypher:")
print(cypher)


# -----------------------------
# Execute Cypher
# -----------------------------

with driver.session() as session:

    result = session.run(cypher)

    records = [
        record.data()
        for record in result
    ]


print("\nGraph Results:")
print(records)


# -----------------------------
# Generate final answer
# -----------------------------

context = json.dumps(records)


answer_prompt = f"""
Answer the user's question using ONLY the graph results below.

User question:
{question}

Graph results:
{context}

Return the answer in exactly this format:

Answer:
<concise natural-language answer>

Sources:
- <source document>

Do not mention Cypher.
Do not mention Neo4j.
Do not mention the graph database.
"""


answer_response = client.models.generate_content(
    model="gemini-3.5-flash-lite",
    contents=answer_prompt
)


print("\n" + answer_response.text)


# -----------------------------
# Close Neo4j
# -----------------------------

driver.close()