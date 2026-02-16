# lana v1.0.0 /// src/consts.py
# xorydev, licensed under AGPL 3. See LICENSE.

from google.genai import types

DEFAULT_SYSTEM_PROMPT = """you are lana, a semi-agentic ai chatbot built on gemini 3.
your outputs are to be in all-lowercase (except for cases such as case-sensitive code) informal british english with a cutesy style using emoticons like :3 (not uwu tho)
feel free to use your tools heavily and thoroughly. in other words, be extremely liberal with tool usage. use them to cross-reference, double-check and wherever else applicable."""

extension_mime_type_map = {
    # image
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    
    # audio
    ".aac": "audio/aac",
    ".flac": "audio/flac",
    ".mp3": "audio/mpeg",
    ".m4a": "audio/mp4",
    ".mpga": "audio/mpga",
    ".opus": "audio/opus",
    ".wav": "audio/wav",
    
    # video
    ".flv": "video/x-flv",
    ".mov": "video/quicktime",
    ".mpeg": "video/mpeg",
    ".mpg": "video/mpg",
    ".mp4": "video/mp4",
    ".webm": "video/webm",
    ".wmv": "video/wmv",
    ".3gp": "video/3gpp",
    ".3gpp": "video/3gpp",
    
    # document
    ".pdf": "application/pdf",
    ".txt": "text/plain",
    ".md": "text/markdown",
    ".markdown": "text/markdown",
    ".csv": "text/csv",
    ".rtf": "application/rtf",
    ".html": "text/html",
    ".htm": "text/html",
    ".css": "text/css",
    ".js": "text/javascript",
    ".json": "application/json",
    ".xml": "application/xml",
    ".yaml": "text/yaml",
    ".yml": "text/yaml",
}

thinking_level_map = {
  "minimal": types.ThinkingLevel.MINIMAL,
  "low": types.ThinkingLevel.LOW,
  "medium": types.ThinkingLevel.MEDIUM,
  "high": types.ThinkingLevel.HIGH,
}

reverse_thinking_level_map = {
  types.ThinkingLevel.MINIMAL: "minimal",
  types.ThinkingLevel.LOW: "low",
  types.ThinkingLevel.MEDIUM:"medium",
  types.ThinkingLevel.HIGH: "high"
}