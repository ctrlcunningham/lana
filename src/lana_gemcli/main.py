# lana v1.0.0 /// src/main.py
# xorydev, licensed under AGPL 3. See LICENSE.

from google import genai
from google.genai import types
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.shortcuts import PromptSession
from prompt_toolkit.application import run_in_terminal
from rich.console import Console
from rich.markdown import Markdown
from .consts import DEFAULT_SYSTEM_PROMPT, extension_mime_type_map, thinking_level_map, reverse_thinking_level_map
from .tools import text_tool_map, multimodal_tool_map, tools
from platformdirs import user_config_dir
from pathlib import Path
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

# env init

class Config:
  def __init__(self, api_key: str, model: str, thinking_level: types.ThinkingLevel, system_prompt: str):
    self.api_key: str = api_key
    self.model: str = model
    self.thinking_level: types.ThinkingLevel = thinking_level
    self.system_prompt: str = system_prompt
  
  def load_from_file(self, file_path):
    config_file_text = ""
    if file_path:
      with open(file_path, "r") as config_file:
        config_file_text = config_file.read()
    config = json.loads(config_file_text)

    self.api_key = config["api_key"]
    self.model = config["default_model"]
    self.thinking_level = thinking_level_map[config["default_thinking_level"]]
    self.system_prompt = config["system_prompt"]

    if args.model:
      self.model = args.model
    if args.thinking_level:
      self.thinking_level = get_user_defined_thinking_level()

  def save_to_file(self, file_path):
    config_dict = {
      "api_key": self.api_key,
      "default_model": self.model,
      "default_thinking_level": reverse_thinking_level_map[self.thinking_level],
      "system_prompt": self.system_prompt
    }
    if file_path:
      with open(file_path, "w") as config_file:
        config_file.write(json.dumps(config_dict))


args = parser.parse_args()

config_dir = user_config_dir("lana", "lana")
config_path = Path(config_dir) / "config.json"
config_path.parent.mkdir(parents=True, exist_ok=True)

console = Console()
bindings = KeyBindings()
session = PromptSession(key_bindings=bindings)

config = Config("", "gemini-3-flash-preview", types.ThinkingLevel.LOW, DEFAULT_SYSTEM_PROMPT)
if args.config:
  config.load_from_file(args.config)
else:
  try:
    config.load_from_file(config_path)
  except FileNotFoundError:
    console.print("[red]you have not created a configuration file. using default values. use the config save command after setting your options to create one.[/red]")
    console.print("[bold]a gemini api key is required to use this software. set a gemini api key using the set api_key command. you can create one over at https://ai.studio[/bold]")

    pass

history: list[types.ContentUnion] = []


def get_user_defined_thinking_level() -> types.ThinkingLevel:
  if args.thinking_level and args.thinking_level in thinking_level_map:
    return thinking_level_map[args.thinking_level]
  else:
    return types.ThinkingLevel.LOW # the default is low since it's support by both flash and pro but doesn't waste resources


async def generate(prompt: str | None, file: bytes | None, file_mime_type: str | None) -> str:
  if not config.api_key:
    console.print("[bold red]a gemini api key has not been set. use the relevant set command to set one.[/bold red]")
    return ""
  gem_client = genai.Client(api_key=config.api_key) # client is created inside the generate function so that the user can use /set for the api key.
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
          # console.print(f"[tool called] {requested_tool} {function_call.args}")
          console.print(f"[dim]- tool call: {requested_tool}[/dim]")
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
  
  return json.dumps([c.model_dump() for c in history if isinstance(c, types.Content)], default=_json_serializer, indent=2)

def deserialise_history(json_data: str):
  global history
  history = [types.Content.model_validate(c) for c in json.loads(json_data)]

def get_user_attached_file() -> tuple[bytes, str]:
  file_path = args.input_file
  _, file_extension = os.path.splitext(file_path)
  file_type = extension_mime_type_map[file_extension]
  with open(file_path, "rb") as file:
    file_data = file.read()
    return (file_data, file_type)

def main():
  print("""
\033[1;35m   _               
  //               
 // __.  ____  __. 
</_(_/|_/ / <_(_/|_ """, end="\033[0m")
  console.print("""[cyan underline]a simple yet useful chatbot for the terminal[/cyan underline]
[bold]press enter to add a newline, alt+enter to send[/bold]
[pink]command list available with /help[/pink]""")


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
            console.print(f"[cyan]saved to {file_name}[/cyan]")
          continue
        case "/load":
          file_name = session.prompt("enter filename to load conversation from: ")
          if file_name:
            if not file_name.endswith(".json"):
              file_name = f"{file_name}.json"
            try:
              with open(file_name, "r") as file:
                deserialise_history(file.read())
              console.print(f"[cyan]loaded history from {file_name}[/cyan]")
            except Exception as e:
              console.print(f"[red]failed to load history: {e}[/red]")
          continue
        case "/attach":
          attachment_file_name = session.prompt("enter name or path of file to attach: ")
          if attachment_file_name:
            with open(attachment_file_name, "rb") as attachment_file:
              attached_file = attachment_file.read()
            console.print(f"[cyan]file {attachment_file_name} will be attached to next message[/cyan]")
          continue
        case "/set model":
          new_model_name = session.prompt("enter new model name: ")
          if new_model_name:
            config.model = new_model_name
            console.print(f"[cyan]will now use model {new_model_name}[/cyan]")
        case "/set api_key":
          api_key = session.prompt("paste in new gemini api_key: ")
          if api_key:
            config.api_key = api_key
            console.print(f"[cyan]api key updated[/cyan]")
        case "/set thinking_level":
          new_thinking_level = session.prompt("enter new thinking level: ")
          if new_thinking_level:
            new_thinking_level_typed = thinking_level_map[new_thinking_level]
            config.thinking_level = new_thinking_level_typed
            console.print(f"[cyan]will now use thinking level {new_thinking_level}[/cyan]")
          continue
        case "/set system_prompt":
          system_prompt_file_name_or_path = session.prompt("path or file name of text or markdown file to load new system prompt from: ")
          if system_prompt_file_name_or_path:
            if system_prompt_file_name_or_path == "DEFAULT":
              config.system_prompt = DEFAULT_SYSTEM_PROMPT
              continue
            with open(system_prompt_file_name_or_path, "r") as system_prompt_file:
              config.system_prompt = system_prompt_file.read()
        case "/config":
          console.print(Markdown(f"""
**current configuration**
- model: {config.model}
- thinking level: {reverse_thinking_level_map[config.thinking_level]}
"""))
        case "/config save":
          config.save_to_file(config_path)
          continue
        case "/config reload":
          config.load_from_file(config_path)
          continue
        case "/help":
          console.print("""[magenta bold underline]lana command help[/magenta bold underline]
all commands are prexifed with a /""", end="")
          console.print(Markdown("""
- help: print this page
- save: save chat
- load: load chat
- attach: attach a file to the next message
- config: show current configuration
- set api_key: set the api key to use
- set model: set the model to use
- set thinking_level: set the thinking level to use
- set system_prompt: set the system prompt to use (loads from a file)
- config save: save config
- config reload: reset config to what's currently on disk
- quit: quit"""))
        case "/quit" | "/bye" | "/exit":
          exit(0)
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