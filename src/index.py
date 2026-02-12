# lana v0.0.1 /// src/main.py
# a simple terminal-based client for the gemini api
# xorydev, licensed under wtfpl (technically OSS). See LICENSE.

from google import genai
from google.genai import types
from dotenv import load_dotenv
from consts import DEFAULT_SYSTEM_PROMPT, extension_mime_type_map, thinking_level_map
from tools import text_tool_map, multimodal_tool_map, tools
import os
import asyncio
import json
import argparse

parser = argparse.ArgumentParser(
  prog="lana",
  description="a terminal-based semi-agentic gemini chatbot"
)
parser.add_argument("-m", "--model")
parser.add_argument("-t", "--thinking-level")
parser.add_argument("-i", "--input-file")
parser.add_argument("-c", "--config")

class Config:
  def __init__(self, model: str, thinking_level: types.ThinkingLevel, system_prompt: str):
    self.model: str = model
    self.thinking_level: types.ThinkingLevel = thinking_level
    self.system_prompt: str = system_prompt
  
  def load_from_file(self, file_path):
    config_file_text = ""
    if file_path:
      with open(file_path, "r") as config_file:
        config_file_text = config_file.read()
    config = json.loads(config_file_text)

    self.model = config["default_model"]
    self.thinking_level = thinking_level_map[config["default_thinking_level"]]
    self.system_prompt = config["system_prompt"]

    if args.model:
      self.model = args.model
    if args.thinking_level:
      self.thinking_level = get_user_defined_thinking_level()

# env init
load_dotenv()
args = parser.parse_args()
history = []
gem_client = genai.Client(api_key=os.getenv("GEM_API_KEY"))
config = Config("gemini-3-flash-preview", types.ThinkingLevel.LOW, DEFAULT_SYSTEM_PROMPT)
if args.config:
  config.load_from_file(args.config)
else:
  try:
    config.load_from_file("config.jsonc") # TODO dynamically load this file from the relevant program configuration storage directory, such as linux's XDG_CONFIG_HOME, depending on the user's operating system
  except FileNotFoundError:
    print("[!] you have not created a configuration file. using default values.") # TODO more precise instructions and/or automatically create default configuration
    pass



def get_user_defined_thinking_level() -> types.ThinkingLevel:
  if args.thinking_level and args.thinking_level in thinking_level_map:
    return thinking_level_map[args.thinking_level]
  else:
    return types.ThinkingLevel.LOW # the default is low since it's support by both flash and pro but doesn't waste resources
  

# abstracted generate function for expandability's sake
async def generate(prompt: str | None, file: bytes | None, file_mime_type: str | None) -> str:
  if prompt:
    if file and file_mime_type:
      history.append(types.Content(role="user", parts=[types.Part(text=prompt), types.Part.from_bytes(data=file, mime_type=file_mime_type)]))
    else:
      history.append(types.Content(role="user", parts=[types.Part(text=prompt)]))

  model_response = await gem_client.aio.models.generate_content(
    contents=history,
    model=config.model,
    config=types.GenerateContentConfig(
      tools=tools,
      system_instruction=config.system_prompt,
      thinking_config=types.ThinkingConfig(thinking_level=config.thinking_level)
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
      if requested_tool in multimodal_tool_map:
        bytes = await multimodal_tool_map[requested_tool](**function_call.args)
        file_path = function_call.args["file_path"]
        file_name = os.path.basename(file_path)
        _, file_extension = os.path.splitext(file_name)
        file_type = ""
        match file_extension:
          case ".png":
            file_type = "image/png"
          case ".jpg":
            file_type = "image/jpeg"
          case ".webp":
            file_type = "image/webp"

        tool_response_parts.append(
          types.Part.from_function_response(
            name = requested_tool,
            response = {
              "status": "success",
            },
            parts = [types.FunctionResponsePart(
                inline_data = types.FunctionResponseBlob(
                  mime_type=file_type,
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

      return await generate(None, None, None) # call the function again, allowing the model to call multiple tools back-to-back
  
  part_texts = []
  for part in model_response.candidates[0].content.parts: # type: ignore
    if part.text:
      part_texts.append(part.text)
  return "".join(part_texts)

    
def get_user_attached_file() -> tuple[bytes, str]:
  file_path = args.input_file
  _, file_extension = os.path.splitext(file_path)
  file_type = extension_mime_type_map[file_extension]
  with open(file_path, "rb") as file:
    file_data = file.read()
    return (file_data, file_type)

def main():
  print(config.model)
  print(config.thinking_level)
  print(config.system_prompt)

  if config.model != "gemini-3-flash-preview" and (config.thinking_level == types.ThinkingLevel.MINIMAL or config.thinking_level == types.ThinkingLevel.MEDIUM):
    raise Exception("invalid argument: thinking levels minimal and medium are only available for gemini 3 flash")

  while True: # chat loop
    is_first_prompt = True
    print("-- enter user prompt (ctrl-d on an empty line to submit) --")
    lines = []
    while True: # we use a while loop for multi-line user input
      line = ""

      try:
        line = input()
      except EOFError:
        break
      
      lines.append(line)
    print("-- end user prompt --\n[i] generating...")

    if args.input_file and is_first_prompt:
      file = get_user_attached_file()
      model_response = asyncio.run(generate("\n".join(lines), file[0], file[1]))
    else:
      model_response = asyncio.run(generate("\n".join(lines), None, None))
    
    print(f"-- model response --\n\n{model_response}\n")

if __name__ == "__main__":
  main()
