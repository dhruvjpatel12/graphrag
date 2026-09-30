from neo4j import GraphDatabase

URI = "neo4j://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "Patel@123"

driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)

with driver.session() as session:
    result = session.run("RETURN 'Connected to Neo4j!' AS message")
    print(result.single()["message"])

driver.close()