import os
import json
from neo4j import GraphDatabase
from google import genai

# -------------------------
# Gemini
# -------------------------

client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"]
)

# -------------------------
# Neo4j
# -------------------------

driver = GraphDatabase.driver(
    "neo4j://localhost:7687",
    auth=("neo4j", "Patel@123")
)

# -------------------------
# Text
# -------------------------

text = """
Elon Musk founded SpaceX.
SpaceX developed the Falcon 9 rocket.
Falcon 9 launches Starlink satellites.
"""

# -------------------------
# Extract graph
# -------------------------

prompt = f"""
Extract entities and relationships from the following text.

Return ONLY valid JSON in this exact format:

{{
  "entities": [
    {{"name": "Entity Name", "type": "EntityType"}}
  ],
  "relationships": [
    {{
      "source": "Entity Name",
      "relationship": "RELATIONSHIP",
      "target": "Entity Name"
    }}
  ]
}}

Text:
{text}
"""

response = client.models.generate_content(
    model="gemini-3.5-flash",
    contents=prompt
)

graph_data = json.loads(response.text)

# -------------------------
# Insert into Neo4j
# -------------------------

with driver.session() as session:

    # Create entities
    for entity in graph_data["entities"]:

        session.run(
            """
            MERGE (n:Entity {name: $name})
            SET n.type = $type
            """,
            name=entity["name"],
            type=entity["type"]
        )

    # Create relationships
    for relationship in graph_data["relationships"]:

        session.run(
            """
            MATCH (a:Entity {name: $source})
            MATCH (b:Entity {name: $target})
            MERGE (a)-[r:RELATED {type: $relationship}]->(b)
            """,
            source=relationship["source"],
            target=relationship["target"],
            relationship=relationship["relationship"]
        )

driver.close()

print("Graph successfully created in Neo4j!")