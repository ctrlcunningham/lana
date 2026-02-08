# lana v0.0.1 /// src/main.py
# a simple terminal-based client for the gemini api
# xorydev, licensed under wtfpl (technically OSS). See LICENSE.

from google import genai
from google.genai import types
from dotenv import load_dotenv
from consts import SYSTEM_PROMPT
from tools import searxng, open_url
import os

# env init
load_dotenv()
gem_client = genai.Client(api_key=os.getenv("GEM_API_KEY"))
chat = gem_client.chats.create(model="gemini-3-flash-preview", config=types.GenerateContentConfig(tools=[searxng, open_url], system_instruction=SYSTEM_PROMPT))

# abstracted generate function for expandability's sake
def generate(prompt: str) -> str:
  model_response = chat.send_message(prompt)
  response = model_response.text

  if not response:
    response = "(model returned no response)"
  return response

def main():
  print(f"""lana v0.0.1
-----------""")
  while True:
    print(generate(input("[user] > ")))

if __name__ == "__main__":
  main()