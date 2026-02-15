# lana

a semi-agentic (potentially agentic soon) chatbot built around the terminal.

## context

i wanted aistudio in the terminal. but i kept going.

## ai usage

- used to help understand docs
- used to implement a prototype solution to one complicated problem that i then studied/understood and replaced w/ my own solution
- the project itself is merely a client for AI APIs

## roadmap/to-do

### core

- [x] basic gemini api interface
- [x] conversation
- [x] basic search tool calls
- [x] file manipulation and code execution tools (make these not suck)
- [x] sysprompt encouraging _heavy_ tool usage
- [x] asyncification
- [x] switch to selenium

### user interaction

- [x] multimodal inputs
- [x] multi-line user prompts
- [x] user image/video/etc input
  - [x] argparse
  - [x] mime type detection
  - [x] inserting files into prompts after the first, TBD alongside UI improvements
- [x] user-defined system prompt
- [x] improve ui and ux
  - [x] `rich` formatting
  - [x] configuration/settings interface
  - [x] saved chats interface
- [ ] easy installation
- [ ] tba

### tools and data retrieval

- [x] selenium improvements
  - [x] switch to selenium headless
  - [x] click on element with css selector
  - [x] type text with css selector
  - [x] take screenshot
- [x] persistent chats
  - [x] context-to-file serialisation
  - [x] file-to-context deserialisation
- [ ] tba

### agentic functionality

- [ ] persistence
  - [x] persistent chats, see "tools and data retrieval"
  - [ ] "notebooks"
    - basically just markdown files that contain certain kinds of info
    - similar to openclaw's SOUL.md, MEMORY.md, HEARTBEAT.md, etc.
    - model can literally just write to these using the provided tools i think?
- [ ] sub-agents
  - sub-agents. the "root" agent should be able to activate these via tool call and they run in the background
  - this would require some kind of multi-threading or idk maybe asyncio has something useful?
  - have the main loop poll the agents on every generation, so we can inject the sub-agent return as a tool return even if the sub-agent tool already returned "sub-agent started" or similar.
  - sub-agents should be able to spawn their own sub-agents (should they be? i'm not sure about this), which means that certain environment variables (system prompt, running/owned sub-agents, etc.) should be tied to an agent. speaking of which, i should probably make this more OOP-like (see: internal codebase changes)
  - post ship
- [ ] tba

### internal codebase

- [x] tool-calling boilerplate cleanup
- [ ] stronger typing
- [ ] tba
