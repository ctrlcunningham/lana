# lana v0.0.1 /// src/main.py
# a simple terminal-based client for the gemini api
# xorydev, licensed under wtfpl (technically OSS). See LICENSE.

from google import genai
from google.genai import types
from dotenv import load_dotenv
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.shortcuts import PromptSession
from prompt_toolkit.application import run_in_terminal
from rich.console import Console
from rich.markdown import Markdown
from consts import DEFAULT_SYSTEM_PROMPT, extension_mime_type_map, thinking_level_map
from tools import text_tool_map, multimodal_tool_map, tools
import os
import json
import base64
import argparse
import asyncio

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
console = Console()
bindings = KeyBindings()
session = PromptSession(key_bindings=bindings)

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
    console.print("[red]model returned no response[/red]")
  
  if model_response.candidates and model_response.candidates[0].content:
    history.append(model_response.candidates[0].content)
    tool_response_parts = []
    if model_response.function_calls:
      for function_call in model_response.function_calls:
        if function_call.args is not None:
          requested_tool = function_call.name
          console.print(f"[tool called] {requested_tool} {function_call.args}")
          if requested_tool in multimodal_tool_map:
            bytes_data = await multimodal_tool_map[requested_tool](**function_call.args)
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
                # NOTE: double check if your SDK version supports 'parts' inside from_function_response
                # usually the binary data goes into the response dict or a separate mechanism.
                # assuming this part was working for you before:
                parts = [types.FunctionResponsePart(
                    inline_data = types.FunctionResponseBlob(
                      mime_type=file_type,
                      data=bytes_data,
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
            # handle unknown tools gracefully
            if requested_tool:
              tool_response_parts.append(
                types.Part.from_function_response(
                    name=requested_tool,
                    response={"error": "unknown function"}
                )
              )
          
          history.append(
            types.Content(role="tool", parts=tool_response_parts)
          )

          # recurse to let the model generate the final answer
          return await generate(None, None, None)
  
  part_texts = []
  if model_response.candidates:
    if model_response.candidates[0].content:
      if model_response.candidates[0].content.parts:
        for part in model_response.candidates[0].content.parts:
          if part.text:
            part_texts.append(part.text)
  response = "".join(part_texts)
  if response.isspace():
    return await generate(None, None, None)
  else:
    return response

    
def serialise_history() -> str:
  def _json_serializer(obj):
    if isinstance(obj, bytes):
      return base64.b64encode(obj).decode('utf-8')
    raise TypeError(f"Type {type(obj)} not serializable")
  
  return json.dumps([c.model_dump() for c in history], default=_json_serializer, indent=2)

def get_user_attached_file() -> tuple[bytes, str]:
  file_path = args.input_file
  _, file_extension = os.path.splitext(file_path)
  file_type = extension_mime_type_map[file_extension]
  with open(file_path, "rb") as file:
    file_data = file.read()
    return (file_data, file_type)

def main():
  console.print("[bold cyan]lana[/bold cyan]")
  console.print("[dim]made by xorydev[/dim]")

  attached_file: bytes | None = None
  attachment_file_name: str | None = None

  try:
    while True:
      text = session.prompt("> ", key_bindings=bindings, multiline=True)
      match text:
        case "/save":
          file_name = session.prompt("enter filename to save current conversation as: ")
          if file_name:
            if not file_name.endswith(".json"):
              file_name = f"{file_name}.json"
            with open(file_name, "w") as file:
              file.write(serialise_history())
            console.print(f"[green]saved to {file_name}[/green]")
          continue
        case "/attach":
          attachment_file_name = session.prompt("enter name or path of file to attach: ")
          if attachment_file_name:
            with open(attachment_file_name, "rb") as attachment_file:
              attached_file = attachment_file.read()
            console.print(f"[green]file {attachment_file_name} will be attached to next message")
          continue
        case _:
          if attached_file and attachment_file_name:
            _, attached_file_extension = os.path.splitext(attachment_file_name)
            console.print(Markdown(asyncio.run(generate(text, attached_file, extension_mime_type_map[attached_file_extension]))))
            
            # clear attachments so we don't append them on the next message
            attached_file = None
            attachment_file_name = None
          else:
            console.print(Markdown(asyncio.run(generate(text, None, None))))
  except (EOFError, KeyboardInterrupt):
    console.print("bai")


if __name__ == "__main__":
  main()