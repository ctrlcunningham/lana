# lana v0.0.1 /// src/tools.py
# a simple terminal-based client for the gemini api
# xorydev, licensed under wtfpl (technically OSS). See LICENSE.

from markdownify import markdownify as md
from typing_extensions import TypedDict
from datetime import datetime
import requests
import aiohttp
import asyncio
import subprocess

class SearchResult(TypedDict):
  url: str
  title: str
  content: str
  score: int


# def legacy_searxng(query: str) -> list[SearchResult]:
#   """
#   searxng search tool. uses https://searx.xorydev.xyz/
#   
#   args:
#     query: string containing search query
#   returns: list of search results
#   """
#   print(f"[tool called] searxng: {query}")
#   response = requests.post("https://searx.xorydev.xyz/search", params={ "format": "json", "q": query })
#   json = response.json()
#   return_object: list[SearchResult] = []
#   for result in json["results"]:
#     return_object.append({ "url": result["url"], "title": result["title"], "score": result["score"], "content": result["content"] })
#   return_object.sort(key=lambda search_result: search_result["score"], reverse=True)
#   return return_object

async def searxng(query: str) -> list[SearchResult]:
  """
  searxng search tool. uses https://searx.xorydev.xyz/
  
  args:
    query: string containing search query
  returns: list of search results
  """
  print(f"[tool called] searxng: {query}")

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

async def open_url(url: str) -> str:
  """
  open a url. currently uses a get request.
  
  
  args:
    url: url as a string
  returns: string containing the html parsed into markdown by markdownify
  """
  async with aiohttp.ClientSession() as session:
    async with session.get(url, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:147.0) Gecko/20100101 Firefox/147.0"}) as response:
      response_body = await response.text()
      return response_body

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
  print(f"[tool called] shell eval: {command}")
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
  print("[tool called] python eval: ", end="")
  timestamp = datetime.now().timestamp()
  file_path = f"/tmp/lana-eval-${timestamp}.py"
  with open(file_path, "w") as python_file:
    python_file.write(code)
  print(file_path)
  
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