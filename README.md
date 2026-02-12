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
- [ ] user image/video/etc input
  - [x] argparse
  - [x] mime type detection
  - [ ] inserting files into prompts after the first, TBD alongside UI improvements
- [x] user-defined system prompt
- [ ] improve ui and ux
  - [ ] `rich` formatting
  - [ ] configuration/settings interface
  - [ ] saved chats interface
- [ ] discord integration because why not
- [ ] easy installation
- [ ] tba

### tools and data retrieval

- [ ] selenium improvements
  - [x] switch to selenium headless
  - [ ] click on element with css selector
  - [ ] type text with css selector
  - [ ] take screenshot
  - [ ] scroll up/down(?)
- [ ] persistent chats
  - [ ] context-to-file serialisation
  - [ ] file-to-context deserialisation
- [ ] tba

### agentic functionality

- [ ] autonomous thinking level control
- [ ] persistence
  - [ ] persistent chats, see "tools and data retrieval"
  - [ ] "notebooks"
    - basically just markdown files that contain certain kinds of info
    - similar to openclaw's SOUL.md, MEMORY.md, HEARTBEAT.md, etc.
    - model can literally just write to these using the provided tools i think?
- [ ] sub-agents
  - sub-agents. the "root" agent should be able to activate these via tool call and they run in the background
  - this would require some kind of multi-threading or idk maybe asyncio has something useful?
  - have the main loop poll the agents on every generation, so we can inject the sub-agent return as a tool return even if the sub-agent tool already returned "sub-agent started" or similar.
  - sub-agents should be able to spawn their own sub-agents (should they be? i'm not sure about this), which means that certain environment variables (system prompt, running/owned sub-agents, etc.) should be tied to an agent. speaking of which, i should probably make this more OOP-like (see: internal codebase changes)
- [ ] openclaw-style heartbeat
  - also self-explanatory, unless the reader is not familiar with openclaw. for context's sake: openclaw has a heartbeat scheduler which infers the model every 30 seconds or 1 hour and instructs it to follow the instructions it has written down in HEARTBEAT.md, check up on anything important and either message the user or report back with "nothing to do"
  - most likely has daemonification (see: internal codebase section) as a prerequisite.
  - _very_ conflicted on whether or not this is worth implementing as well. wouldn't we just rebuilding openclaw, but with gemini api exclusivity?
- [ ] tba

### internal codebase

- [x] tool-calling boilerplate cleanup
- [ ] daemon
  - self-explanatory, split the current tool into `lanactl` (the chat interface) and `lanad` (everything else) which communicate to each other using IPC or REST or similar
  - this allows for more abstraction over input origin and makes my job with things like the discord integration a lot easier.
  - conflicted on whether or not this is worth implementing.
- [ ] use openai api
  - rather than using `google-genai`, use openai's interface. google provides an openai-compatible interface, much like every other AI API/corporation.
  - practically makes this model agnostic.
  - what about gemini-exclusive features, such as video input?
- [ ] OOP
  - use more OOP features and interfaces. f.e. custom agent/chatbot object
- [ ] tba
