# On-Call Schedule Renderer

A Python implementation of an on-call schedule rendering system with override support for incident.io.

## Overview

The aim of this tool is create an on-call schedule by combining
- a Base rotation schedule - Regular repeating shifts across a team
- Override entries - Temporary modifications for specific time period

## Requirements

- Python 3.7 or higher (uses dataclasses and type hints)
- No external dependencies required (uses standard library only)

## Usage

Firstly run this command to ensure the script is executable
```chmod +x render-schedule```

Then run the script with arguments

```./render-schedule \
  --schedule=<path-to-schedule.json> \
  --overrides=<path-to-overrides.json> \
  --from='<ISO-8601-timestamp>' \
  --until='<ISO-8601-timestamp>'
```

### Example

```
 ./render-schedule \
    --schedule=schedule.json \
    --overrides=overrides.json \
    --from='2025-11-07T17:00:00Z' \
    --until='2025-11-21T17:00:00Z'
```
