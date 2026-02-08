# lana v0.0.1 /// src/main.py
# a simple terminal-based client for the gemini api
# xorydev, licensed under wtfpl (technically OSS). See LICENSE.

from google import genai
from google.genai import types
from dotenv import load_dotenv
from consts import SYSTEM_PROMPT
from tools import searxng, open_url, python_eval, shell_eval, file_find_and_replace
import os

# env init
load_dotenv()
gem_client = genai.Client(api_key=os.getenv("GEM_API_KEY"))
chat = gem_client.aio.chats.create(
  model="gemini-3-flash-preview", 
  config=types.GenerateContentConfig(
    tools=[searxng, open_url, python_eval, shell_eval, file_find_and_replace], 
    system_instruction=SYSTEM_PROMPT,
    thinking_config=types.ThinkingConfig(thinking_level=types.ThinkingLevel.MEDIUM) # TODO user thinking level parameter + give _her_ the ability to control thinking level
  ),
)

# abstracted generate function for expandability's sake
async def generate(prompt: str) -> str:
  model_response = await chat.send_message(prompt)
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