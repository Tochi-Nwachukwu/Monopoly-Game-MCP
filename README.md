# Monopoly AI MCP Server

A Monopoly game where AI agents (OpenAI GPT & Ollama Llama) compete against each other!

## Project Structure

```
monopoly-mcp/
├── mcp_server.py          # MCP server exposing game tools
├── game_engine.py         # Core game logic
├── ai_agents.py           # AI agent implementations
├── game_runner.py         # Main game runner
├── requirements.txt       # Python dependencies
└── README.md
```

## Requirements

```txt
# requirements.txt
openai>=1.0.0
mcp>=0.1.0
```

## Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install openai mcp

# For Ollama, install from https://ollama.ai
# Then pull the model:
ollama pull llama3.1
```

## Running the Game

### Option 1: Direct Game Runner (Recommended)

Run AI agents directly without MCP:

```bash
# OpenAI (GPT-4o-mini) vs Ollama (Llama 3.1)
python game_runner.py \
    --player1 "ChatGPT" --player1-type openai --player1-model gpt-4o-mini \
    --player2 "Llama" --player2-type ollama --player2-model llama3.1 \
    --max-turns 100 \
    --delay 0.5

# OpenAI vs OpenAI
python game_runner.py \
    --player1 "GPT4" --player1-type openai --player1-model gpt-4o \
    --player2 "GPT-Mini" --player2-type openai --player2-model gpt-4o-mini

# Ollama vs Ollama (fully local, no API costs!)
python game_runner.py \
    --player1 "Llama-A" --player1-type ollama --player1-model llama3.1 \
    --player2 "Llama-B" --player2-type ollama --player2-model llama3.1

# Human vs AI
python game_runner.py \
    --player1 "You" --player1-type human \
    --player2 "ChatGPT" --player2-type openai --player2-model gpt-4o-mini
```

### Option 2: MCP Server Mode

Run as an MCP server for integration with MCP clients:

```bash
# Start the MCP server
python mcp_server.py
```

Add to your MCP client config (e.g., Claude Desktop):

```json
{
  "mcpServers": {
    "monopoly": {
      "command": "python",
      "args": ["/path/to/monopoly-mcp/mcp_server.py"]
    }
  }
}
```

## Environment Variables

```bash
# Required for OpenAI agents
export OPENAI_API_KEY="sk-your-key-here"

# Optional: Ollama host (default: http://localhost:11434)
export OLLAMA_HOST="http://localhost:11434"
```

## MCP Tools Available

| Tool | Description |
|------|-------------|
| `start_game` | Initialize a new game with player names |
| `get_game_state` | Get current game state |
| `get_my_status` | Get detailed player status |
| `roll_dice_and_move` | Roll dice and move current player |
| `buy_property` | Buy the current property |
| `decline_purchase` | Decline to buy (starts auction) |
| `place_bid` | Bid in an auction |
| `pass_auction` | Pass on auction |
| `pay_jail_bail` | Pay $50 to leave jail |
| `use_jail_card` | Use Get Out of Jail Free card |
| `roll_for_doubles` | Try to roll doubles to escape jail |
| `build_house` | Build a house on a property |
| `mortgage_property` | Mortgage a property |
| `unmortgage_property` | Unmortgage a property |
| `end_turn` | End current player's turn |
| `get_property_info` | Get info about a specific property |
| `get_available_actions` | List valid actions for current player |

## Example Game Output

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  TURN 1 │ ChatGPT │ Phase: waiting_for_roll
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  💰 $1500  │ 📍 GO                        │ 🏠 0 properties

  🎯 ChatGPT chose: roll_dice_and_move
  🎲 Rolled [4][3] = 7
  📍 Landed on: Chance
  
  🎯 ChatGPT chose: end_turn
  ➡️ Next player: Llama

  SCOREBOARD:
  👉 Llama: $1500 │ 0 props
     ChatGPT: $1650 │ 0 props
```

## AI Strategy

The AI agents use this strategy prompt:
- Prioritize completing color groups
- Orange and red properties have best ROI  
- Keep cash reserves for rent
- Mortgage less valuable properties if needed
- In jail: use card > pay bail > roll doubles

## Tips for Running

1. **Start Ollama first**: `ollama serve`
2. **Check model is downloaded**: `ollama list`
3. **Lower delay for faster games**: `--delay 0.1`
4. **Watch the costs**: OpenAI charges per API call, Ollama is free!