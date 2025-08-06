# IPL MCP Server – Data Analyst Technical Assessment

**GitHub Repository (all code and IPL data):**  
[https://github.com/MadhavKrishna09/ipl-mcp-server](https://github.com/MadhavKrishna09/ipl-mcp-server)

## 🏏 Project Overview

This project is a self-contained MCP (Model Context Protocol) server designed to answer a wide range of natural language questions about Indian Premier League (IPL) cricket data.

## 📦 Repo Contents

- `ipl_mcp_server.py` – MCP server (main logic)
- `data_loader.py` – Loads IPL JSON into SQLite
- `schema.sql` – Database schema (relational)
- `requirements.txt` – Python package requirements
- `ipl_data/` – ** IPL JSON files needed** 
- `ipl_data.db` – Created by loader script (SQLite DB)
- `demo_queries.md` – Example/test queries for Claude Desktop
- `claude_desktop_config_template.json` – Claude integration config
- `README.md` – This file

---

## ⚡️ Quick Start

1. **Clone this repository:**
   ```bash
   git clone https://github.com/MadhavKrishna09/ipl-mcp-server.git
   cd ipl-mcp-server
   ```

2. **Install dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```

3. **IPL Data Directory**  
   The `ipl_data/` folder **folder in this repository already contains IPL JSON files for instant out-of-the-box use!**.  
   **No need to download or unpack extra data.**

   *Want to analyze more matches?*
   
    You can simply add new IPL match JSON files (for example, downloaded from cricsheet.org) into the ipl_data/ folder alongside the existing files.

5. **Load the data into the SQLite database:**
   ```bash
   python3 data_loader.py
   ```
   *You should see logs indicating matches and deliveries have loaded successfully.*

6. **Configure Claude Desktop for MCP integration:**
   - Find your python path:
     ```bash
     which python3
     ```
   - Edit the provided `claude_desktop_config_template.json` with your python path and project folder.
   - Copy this config to your Claude config directory:
     - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Example config:
     ```json
     {
         "mcpServers": {
             "ipl-cricket-analyzer": {
                 "command": "/your/python3/path",
                 "args": ["/your/full/path/ipl_mcp_server.py"],
                 "env": {"PYTHONUNBUFFERED": "1"}
             }
         }
     }
     ```

7. **Restart Claude Desktop** (close completely and reopen for config to take effect).

## 📝 Full Setup Instructions

### Prerequisites

- Python 3.8 or higher (tested on 3.13)
- Claude Desktop (latest version, with MCP support)
- git, pip, and command-line environment

### 1. Clone and Install

```bash
git clone https://github.com/MadhavKrishna09/ipl-mcp-server.git
cd ipl-mcp-server
pip3 install -r requirements.txt
```

### 2. Check IPL Data Directory

Ensure the following yields a nonzero count:
```bash
ls ipl_data/*.json | wc -l
```
*If it does, you’re ready. No further data actions needed.*

### 3. Load the Database

```bash
python3 data_loader.py
```

### 4. MCP Server & Claude Desktop Setup

- Use the provided config template file.
- Ensure all paths are absolute and correct.
- Restart Claude Desktop.
- Look for the MCP server/tool indicator at the bottom of the Claude interface.

## 👩🔬 How to Demo/Verify

- Use queries from [`demo_queries.md`](demo_queries.md) in the Claude Desktop chat prompt.
- Check that answers are returned, in readable text/tables, generated from your IPL data.

## 🧩 Troubleshooting

- **Server does not connect in Claude:**  
  Double-check your python path, `claude_desktop_config.json` and that `ipl_data/` is present.
- **Database errors:**  
  Re-run `python3 data_loader.py`.
- **No output or errors in Claude:**  
  Restart Claude after changing config, check logs.


\*\*Thank you for reviewing!\*\*

