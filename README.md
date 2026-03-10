# biblemateagent

A headless version of BibleMate AI Agent Mode

* supports study plan, multiple tools orchestrations
* supports single tool execution
* supports prompt refinement
* supports md and docx export of outputs
* supports developer mode

## Installation

```
pip install biblemateagent
```

Install CLI tool `pandoc` separately to support DOCX export

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

# Single Tool Execution

```
bibleagent --tool get_direct_text_response "Your Bible Study Request"
```

or

```
bibleagent --tool auto "Your Bible Study Request"
```

## Tool Description

```
bibleagent --tool_description
```

# Use as a Python Libary

```
from biblemateagent.agent import bible_agent
from biblemateagent.tool import run_single_tool
```

# Comparison Tests with Different AI Models

Check the content in directory `LLM_Capability_Tests`

# BibleMate AI Suite

Check out the BibleMate AI Suite at https://github.com/eliranwong/biblemate
