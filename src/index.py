# lana v0.0.1 /// src/main.py
# a simple terminal-based client for the gemini api
# xorydev, licensed under wtfpl (technically OSS). See LICENSE.

from google import genai
from google.genai import types
from dotenv import load_dotenv
from consts import SYSTEM_PROMPT
from tools import *
import os
import asyncio
import json
import base64

# env init
load_dotenv()
history = []
gem_client = genai.Client(api_key=os.getenv("GEM_API_KEY"))

text_tool_map = {
  "searxng": searxng,
  "shell_eval": shell_eval,
  "sel_navigate": sel_navigate,
  "sel_read_current_page_as_markdown": sel_read_current_page_as_markdown,
  "sel_read_current_page_as_raw_html": sel_read_current_page_as_raw_html,
  "shell_eval": shell_eval,
  "python_eval": python_eval,
  "file_find_and_replace": file_find_and_replace,
  "open_image": open_image,
}

# abstracted generate function for expandability's sake
async def generate(prompt: str | None) -> str:
  if prompt:
    history.append(types.Content(role="user", parts=[types.Part(text=prompt)]))

  model_response = await gem_client.aio.models.generate_content(
    contents=history,
    model="gemini-3-flash-preview",
    config=types.GenerateContentConfig(
      tools=tools, 
      system_instruction=SYSTEM_PROMPT,
      thinking_config=types.ThinkingConfig(thinking_level=types.ThinkingLevel.HIGH) # TODO user thinking level parameter + give _her_ the ability to control thinking level
    )
  )
  if not model_response:
    return "(model returned no response)"
  
  # we now use manual function calling because automatic doesn't support image returns.
  tool_response_parts = []
  if model_response.function_calls:
    function_call = model_response.function_calls[0]
    if function_call.args is not None:
      requested_tool = function_call.name
      print(f"[tool called] {requested_tool} {function_call.args}")
      if requested_tool == "open_image":
        bytes = await open_image(**function_call.args)
        image_path = function_call.args["file_path"]
        image_name = os.path.basename(image_path)
        _, image_extension = os.path.splitext(image_name)
        image_type = ""
        match image_extension:
          case ".png":
            image_type = "image/png"
          case ".jpg":
            image_type = "image/jpeg"
          case ".webp":
            image_type = "image/webp"

        tool_response_parts.append(
          types.Part.from_function_response(
            name = requested_tool,
            response = {
              "status": "success",
            },
            parts = [types.FunctionResponsePart(
                inline_data = types.FunctionResponseBlob(
                  mime_type=image_type,
                  data=bytes,
                ),
            )]
          )
        )
      elif requested_tool in text_tool_map:
        result = await text_tool_map[requested_tool](**function_call.args)
        tool_response_parts.append(
          types.Part.from_function_response(
            name = requested_tool,
            response = {
              "status": "success",
              "output": result
            },
          )
        )
      else:
        result = json.dumps({"error": "unknown function"})
      
      history.append(
        types.Content(role="tool", parts=tool_response_parts)
      )

      return await generate(None) # call the function again, allowing the model to call multiple tools back-to-back
  
  part_texts = []
  for part in model_response.candidates[0].content.parts: # type: ignore
    if part.text:
      part_texts.append(part.text)
  return "".join(part_texts)

    

def main():
  print(f"""lana v0.0.1
-----------""")
  while True:
    print(asyncio.run(generate(input("[user] > "))))

if __name__ == "__main__":
  main()
