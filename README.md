# MCP Bloomeo Server

A server that connects Claude Desktop to Bloomeo experiment data using the Model Context Protocol (MCP).

## What is MCP?

MCP (Model Context Protocol) lets AI assistants like Claude access external data sources safely. Instead of copying data or using complex APIs, MCP creates a direct connection between Claude and your data.

When you ask Claude about your experiments, it can:
- Query your Bloomeo database directly
- Get real-time data
- Access specific experiments, trials, and measurements
- Search and filter results

## What is FastMCP?

FastMCP is a Python framework that makes building MCP servers easy. Instead of handling the complex MCP protocol manually, you just write simple functions. FastMCP handles:
- Network communication
- Data formatting  
- Error handling
- Authentication

## What This Server Does

This server gives Claude access to your Bloomeo experiment data. Claude can:
- Count your experiments (only considering the Trials List)
- List experiments with pagination
- Get experiment details including notebooks and treatments
- Search experiments by name
- Access trial data, variable groups, and measurements

## Installation

### Requirements
- Python 3.8+
- Access to Bloomeo with a Bearer token

### Install
```bash
git clone https://github.com/mcrimi/bloomeomcp.git
cd bloomeomcp
pip install -e .
```

## Setup with Claude Desktop

### 1. Get Your Bearer Token

If you don't know or you don't have access to the user token you can:

- Open Bloomeo in your browser
- Press F12 to open developer tools
- Go to Network tab
- Make any request in Bloomeo
- Copy the Bearer token from the Authorization header

### 2. Configure Claude Desktop

**macOS**: Edit `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: Edit `%APPDATA%\Claude\claude_desktop_config.json`

Add this configuration:
```json
{
  "mcpServers": {
    "bloomeo": {
      "command": "python",
      "args": ["-m", "mcp_bloomeo"],
      "env": {
        "BLOOMEO_BEARER_TOKEN": "your_bearer_token_here"
      }
    }
  }
}
```

### 3. Restart Claude Desktop

If everything went well you should now see a new integration called *Bloomeo*:

![CleanShot 2025-06-26 at 16 01 27@2x](https://github.com/user-attachments/assets/d6bf3a63-239f-4e83-8c1d-17af28a56f83)


## Available Functions

### Experiment Discovery
- `get_experiments_count` - Returns total count (221 experiments)
- `get_all_experiments` - Gets one page of experiments  
- `get_all_experiments_paginated` - Gets multiple pages automatically
- `search_experiments_by_name` - Search by experiment name

### Experiment Data
- `get_experiment_data` - Gets complete experiment information
- `get_experiment_notebook` - Gets notebook entries for a trial
- `get_experiment_treatment` - Gets treatment data
- `get_trial_notation` - Gets trial notes
- `get_variable_groups` - Gets measurement variables

## Usage Examples

Ask Claude in natural language:

```
"Give me a summary of all experiments"
"Tell me abou experiment [trial_name}"
"Plot the all the notation data of experiment [trial_name]"
```


## Development

### Project Structure
```
mcp_bloomeo/
├── __init__.py          # Package setup
├── __main__.py          # Entry point  
├── fastmcp_server.py    # MCP server with tools
├── client.py           # Bloomeo API client
└── models.py           # Data models
```

