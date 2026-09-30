import os
import json
from pathlib import Path
from neo4j import GraphDatabase
from google import genai

client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"]
)

driver = GraphDatabase.driver(
    "neo4j://localhost:7687",
    auth=("neo4j", "Patel@123")
)

documents_path = Path(__file__).resolve().parent.parent / "documents"
files = list(documents_path.glob("*.txt"))

print(f"Found {len(files)} documents")

for file_path in files:

    print(f"\nProcessing: {file_path.name}")

    text = file_path.read_text()

    prompt = f"""
Extract entities and relationships from this document.

Return ONLY valid JSON:

{{
  "entities": [
    {{"name": "Entity Name", "type": "EntityType"}}
  ],
  "relationships": [
    {{
      "source": "Entity Name",
      "relationship": "relationship_name",
      "target": "Entity Name"
    }}
  ]
}}

Document:
{text}
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    graph_data = json.loads(response.text)

    with driver.session() as session:

        # Create document node
        session.run(
            """
            MERGE (d:Document {name: $document})
            """,
            document=file_path.name
        )

        # Create entities
        for entity in graph_data["entities"]:
            session.run(
                """
                MERGE (n:Entity {name: $name})
                SET n.type = $type

                WITH n
                MATCH (d:Document {name: $document})

                MERGE (d)-[:MENTIONS]->(n)
                """,
                name=entity["name"],
                type=entity["type"],
                document=file_path.name
            )

        # Create relationships
        for rel in graph_data["relationships"]:
            session.run(
                """
                MATCH (a:Entity {name: $source})
                MATCH (b:Entity {name: $target})

                MERGE (a)-[r:RELATED {type: $relationship}]->(b)
                """,
                source=rel["source"],
                target=rel["target"],
                relationship=rel["relationship"]
            )

    print(f"Completed: {file_path.name}")

driver.close()

print("\nAll documents processed successfully!")