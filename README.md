# biblemateagent

A headless version of BibleMate AI Agent Mode

Support md and docx export 

## Installation

```
pip install biblemateagent
```

or

```
pip install bibleagent
```

## Set up data

```
biblematedata
```

## Run BibleMate Agent

```
biblemateagent "Your Bible Study Request"
```

or

```
bibleagent "Your Bible Study Request"
```

## Configuration

Use either [agentmake default backend](https://github.com/eliranwong/agentmake), which can be configured by running:

```
ai -ec
```

Or CLI options.

## CLI Options

Find help by running:

```
biblemateagent -h
```

or

```
bibleagent -h
```

Run, for example:

```
bibleagent -b ollamacloud -m gemini-3-flash-preview -cw 1048576 -mt 65536 -docx "In-depth study of John 3:16"
```

Stdin input is also supported:

```
echo "In-depth study of John 3:16" | bibleagent -b ollamacloud -m gemini-3-flash-preview -cw 1048576 -mt 65536 -docx
```

## Use it as a python library

```
from biblemateagent import bible_agent

messages = bible_agent(
    request="In-depth study of John 3:16",
    language="eng",
    improve_prompt=False,
    md_export=False,
    docx_export=False,
    output_directory="",
    developer=False,
    cancel_event=None,
    **kwargs
)
```

# BibleMate AI Suite

Check out the BibleMate AI Suite at https://github.com/eliranwong/biblemate
