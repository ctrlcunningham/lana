import requests
from markdownify import markdownify as md
from typing_extensions import TypedDict

class SearchResult(TypedDict):
  url: str
  title: str
  content: str
  score: int


def searxng(query: str) -> list[SearchResult]:
  """
  searxng search tool. uses https://searx.xorydev.xyz/
  
  args:
    query: string containing search query
  returns: list of search results
  """
  print(f"[tool called] searxng: {query}")
  response = requests.post("https://searx.xorydev.xyz/search", params={ "format": "json", "q": query })
  json = response.json()
  return_object: list[SearchResult] = []
  for result in json["results"]:
    return_object.append({ "url": result["url"], "title": result["title"], "score": result["score"], "content": result["content"] })
  return_object.sort(key=lambda search_result: search_result["score"], reverse=True)
  return return_object

def open_url(url: str) -> str:
  """
  open a url. currently uses a get request.
  
  args:
    url: url
  returns: string containing the html parsed into markdown by markdownify
  """
  print(f"[tool called] open_url: {url}")
  return md(requests.get(url=url, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:147.0) Gecko/20100101 Firefox/147.0"}).text)