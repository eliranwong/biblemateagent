# biblemateagent
A headless version of BibleMate AI Agent Mode

## Installation

> pip install biblemateagent

or

> pip install bibleagent

## Set up data

> biblematedata

## Run BibleMate Agent

> biblemateagent "Your Bible Study Request"

or

> bibleagent "Your Bible Study Request"

## Configuration

Use either agentmake backend, which can be configured by running:

> ai -ec

Or CLI options.

## CLI Options

Find help by running:

> biblemateagent -h

or

> bibleagent -h

Run, for example:

> bibleagent -b ollamacloud -m gemini-3-flash-preview -mt 8192 -cw 200000 -docx "In-depth study of John 3:16"