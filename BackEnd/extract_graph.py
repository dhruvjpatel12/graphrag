import os
import json
from google import genai

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

text = """
Elon Musk founded SpaceX.
SpaceX developed the Falcon 9 rocket.
Falcon 9 launches Starlink satellites.
"""

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

result = json.loads(response.text)

print(json.dumps(result, indent=2))
