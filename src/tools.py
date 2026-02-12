# lana v0.0.1 /// src/tools.py
# a simple terminal-based client for the gemini api
# xorydev, licensed under wtfpl (technically OSS). See LICENSE.

from google.genai import types
from markdownify import markdownify as md
from typing_extensions import TypedDict
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
# import requests
import aiohttp
import subprocess

driver_options = Options()
driver_options.add_argument("--headless")
driver = webdriver.Firefox(options=driver_options)

class SearchResult(TypedDict):
  url: str
  title: str
  content: str
  score: int

async def searxng(query: str) -> list[SearchResult]:
  """
  searxng search tool. uses https://searx.xorydev.xyz/
  
  args:
    query: string containing search query
  returns: list of search results
  """
  async with aiohttp.ClientSession() as session:
    async with session.post("https://searx.xorydev.xyz/search", params={ "format": "json", "q": query }) as response:
      json = await response.json()
      return_object: list[SearchResult] = []
      for result in json["results"]:
        return_object.append({ "url": result["url"], "title": result["title"], "score": result["score"], "content": result["content"] })
      return_object.sort(key=lambda search_result: search_result["score"], reverse=True)
      return return_object
    

# def open_url(url: str) -> str:
#   """
#   open a url. currently uses a get request.
#   
#   args:
#     url: url
#   returns: string containing the html parsed into markdown by markdownify
#   """
#   print(f"[tool called] open_url: {url}")
#   return md(requests.get(url=url, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:147.0) Gecko/20100101 Firefox/147.0"}).text)


async def sel_navigate(url: str):
  """
  navigate selenium to a url without getting the html at all

  args:
    url: url as a string
  """
  driver.get(url)

async def sel_read_current_page_as_markdown() -> str:
  """
  get the contents of the page currently opened in selenium, parsed as markdown
  
  
  returns: string containing the html parsed into markdown by markdownify
  """
  page_source = driver.page_source
  markdowned_page_source = md(page_source)
  bs4_page_source = BeautifulSoup(page_source, "html.parser")
  clickables = []
  for element in bs4_page_source.find_all(["a", "button"]):
    clickables.append(element)
  return f"""
{markdowned_page_source}

{clickables}
"""

async def sel_read_current_page_as_raw_html() -> str:
  """
  get the contents of the page currently opened in selenium

  returns: string containing the html
  """
  return driver.page_source


# async def sel_read_page_as_markdown(url: str) -> str:
#   """
#   navigate selenium to a url and get the page contents as markdown
#   
#   args:
#     url: url as a string
#   returns: string containing the html parsed into markdown by markdownify
#   """
#   driver.get(url)
#   return await sel_read_current_page_as_markdown()
# 
# async def sel_read_page_as_raw_html(url: str) -> str:
#   """
#   navigate selenium to a url and get the raw html of the page
# 
#   args:
#     url: url as a string
#   returns: string containing the html
#   """
#   driver.get(url)
#   return await sel_read_current_page_as_raw_html()

async def shell_eval(command: str) -> tuple[int, str, str]: # TODO: containerise
  """
  evaluate a shell command
  
  args:
    command: string containing the shell command
  returns:
    tuple containing:
      1. status code as int
      2. stdout as str
      3. stderr as str
  """
  command_output = subprocess.run(command, shell=True, capture_output=True)
  return_code = command_output.returncode
  stdout = command_output.stdout.decode("utf-8")
  stderr = command_output.stderr.decode("utf-8")
  return (return_code, stdout, stderr)


async def python_eval(code: str) -> tuple[int, str, str]: # TODO: containerise
  """
  evaluate python code. this function works by writing the code into a file and evaluating it using the python3 interpreter.
  thus, all output needs to be print()ed within the file's source code.

  args:
    code: string containing python code
  returns:
    tuple containing:
      1. status code as int
      2. stdout as str
      3. stderr as str
  """
  timestamp = datetime.now().timestamp()
  file_path = f"/tmp/lana-eval-${timestamp}.py"
  with open(file_path, "w") as python_file:
    python_file.write(code)
  
  command = f"python3 {file_path}"
  command_output = subprocess.run(command, shell=True, capture_output=True)
  return_code = command_output.returncode

  stdout = command_output.stdout.decode("utf-8")
  stderr = command_output.stderr.decode("utf-8")
  return (return_code, stdout, stderr)


async def file_find_and_replace(file_path: str, find: str, replace: str):
  """
  find and replace a string within a file. 
  
  args:
    file_path: file path, relative or absolute, as a string
    find: string to search for
    replace: string to replace `find` with
  """

  file_as_string: str = ""
  with open(file_path, "r") as file_read:
    file_as_string = file_read.read()

  file_as_string = file_as_string.replace(find, replace)

  with open(file_path, "w") as file_write:
    file_write.write(file_as_string)


async def open_image(file_path: str) -> bytes:
  """
  open a png image

  args:
    path: string containing the file path
  returns:
    image bytes which are processed by the function caller
  """

  with open(file_path, "rb") as file:
    bytes = file.read()

  return bytes


tools = [
  types.Tool(function_declarations=[types.FunctionDeclaration(
  name="searxng",
  description="searxng search tool. uses https://searx.xorydev.xyz/",
  parameters={ 
    "type": "object", # type: ignore because the official docs themselves are invalid, according to vscode
    "properties": {
      "query": {
        "type": "string",
        "description": "string containing search query"
      },
    },
    "required": ["query"]
  },
)]),
  types.Tool(function_declarations=[types.FunctionDeclaration(
  name="sel_navigate",
  description="navigate selenium to a url without getting the html at all",
  parameters={ 
    "type": "object", # type: ignore because the official docs themselves are invalid, according to vscode
    "properties": {
      "url": {
        "type": "string",
        "description": "url as a string"
      },
    },
    "required": ["url"]
  },
)]),
  types.Tool(function_declarations=[types.FunctionDeclaration(
  name="sel_read_current_page_as_markdown",
  description="get the contents of the page currently opened in selenium, parsed as markdown",
)]),
  types.Tool(function_declarations=[types.FunctionDeclaration(
  name="sel_read_current_page_as_raw_html",
  description="get the raw html contents of the page currently opened in selenium",
)]),
  types.Tool(function_declarations=[types.FunctionDeclaration(
  name="shell_eval",
  description="evaluate a shell command",
  parameters={ 
    "type": "object", # type: ignore because the official docs themselves are invalid, according to vscode
    "properties": {
      "command": {
        "type": "string",
        "description": "string containing the shell command"
      },
    },
    "required": ["command"]
  },
)]),
  types.Tool(function_declarations=[types.FunctionDeclaration(
  name="python_eval",
  description="evaluate python code. this function works by writing the code into a file and evaluating it using the python3 interpreter. thus, all output needs to be print()ed within the file's source code.",
  parameters={ 
    "type": "object", # type: ignore because the official docs themselves are invalid, according to vscode
    "properties": {
      "code": {
        "type": "string",
        "description": "string containing python code"
      },
    },
    "required": ["code"]
  },
)]),
  types.Tool(function_declarations=[types.FunctionDeclaration(
  name="file_find_and_replace",
  description="find and replace a string within a file",
  parameters={ 
    "type": "object", # type: ignore because the official docs themselves are invalid, according to vscode
    "properties": {
      "file_path": {
        "type": "string",
        "description": "file path, relative or absolute, as a string"
      },
      "find": {
        "type": "string",
        "description": "string to search for"
      },
      "replace": {
        "type": "string",
        "description": "string to replace `find` with"
      },
    },
    "required": ["file_path", "find", "replace"]
  },
)]),
  types.Tool(function_declarations=[types.FunctionDeclaration(
  name="open_image",
  description="open a png image",
  parameters={ 
    "type": "object", # type: ignore because the official docs themselves are invalid, according to vscode
    "properties": {
      "file_path": {
        "type": "string",
        "description": "string containing the file path"
      },
    },
    "required": ["file_path"]
  },
)]),
]

text_tool_map = {
  "searxng": searxng,
  "shell_eval": shell_eval,
  "sel_navigate": sel_navigate,
  "sel_read_current_page_as_markdown": sel_read_current_page_as_markdown,
  "sel_read_current_page_as_raw_html": sel_read_current_page_as_raw_html,
  "shell_eval": shell_eval,
  "python_eval": python_eval,
  "file_find_and_replace": file_find_and_replace,
}

multimodal_tool_map = {
  "open_image": open_image
}