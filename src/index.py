# Lana v0.0.1
# A simple terminal-based client for the Gemini API
# xorydev, licensed under WTFPL (technically OSS). See LICENSE.

from google import genai
from google.genai import types
from dotenv import load_dotenv
from consts import SYSTEM_PROMPT
from tools import searxng, open_url
import os

# env init
load_dotenv()
gem_client = genai.Client(api_key=os.getenv("GEM_API_KEY"))

def main():
  print(f"""Lana v0.0.1
-----------""")
  
  # chat = gem_client.chats.create(model="gemini-3-flash-preview", config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT, tools=[searxng, open_url]))
  # while True:
  #   response = chat.send_message_stream(input("[user] > "))
  #   for chunk in response:
  #     print(chunk.text, end="")
  response = gem_client.models.generate_content(model="gemini-3-flash-preview", config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT, tools=[searxng, open_url]), contents=input("[user] > "))
  print(response.text)

if __name__ == "__main__":
  main()