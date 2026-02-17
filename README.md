# lana

a simple semi-agentic chatbot interface for gemini built around the terminal.

## context

i wanted aistudio in the terminal. but i kept going. after trimming out some feature creep, i settled on a nice little general-purpose cli chatbot with some useful tools.

## how ai was used during the creation of this project

- used to help understand docs
- used to implement prototype solutions to complicated problems that i then studied/understood and replaced w/ my own solutions
- the project itself is merely a client for AI APIs

## getting started

### usage reuirements

to use this tool you need english literacy. also, ideally, you should use a paid api key because you _will_ get ratelimited _extremely quickly_ by google on free tier.

### installation

this project is on pypi! you just have to install python and

```
pip install lana_gemcli
lana
```

however, if your system does not support direct pip install (f.e. system-managed python packages), you _will_ unfortunately have to run the cli inside a venv.
you can look up the relevant documentation for this online.

### configuration

the CLI tool name is `lana`, not `lana_gemcli`.
the CLI uses alt+enter for submit and enter for newlines (this includes commands!)
all commands are prefixed with `/` and do not take any arguments when inferred.
instead, they're given settings via user input.

so, for instance, to set the thinking level to high, it would look something like this:

```
> /set thinking_level [alt+enter]
enter new thinking level: high [alt+enter]
will now use thinking level high
```

obviously, `[alt+enter]` would be replaced by you actually pressing alt+enter.

### api keys

as expected, a gemini api key is required to use the cli.
you can generate one over at https://ai.studio.
the cli itself will instruct you on setting one. however, i am also going to provide instructions here:

1. you install the cli normally and enter.
2. inside the cli, type `/set api_key` and press alt+enter.
3. paste in your api key and press alt+enter again.
   the cli will now work, but you also want to run `/config save` to save the api key to your configuration.

### conversation

after you've set all your settings, you just type in your prompts and send them with alt+enter. you'll get the ai's response back.
there's not much to explain here.
