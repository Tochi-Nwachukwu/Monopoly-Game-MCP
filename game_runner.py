#!/usr/bin/env python3
"""
Monopoly AI Game Runner - Orchestrates AI agents playing Monopoly
Can run standalone or connect to MCP server
"""

import os
import time
import argparse
from typing import Dict, List, Any

from game_engine import MonopolyGame, GamePhase
from ai_agents import create_agent, BaseAgent, OpenAIAgent, OllamaAgent


def print_banner():
    print("""
╔═══════════════════════════════════════════════════════════════╗
║     __  __                              _                     ║
║    |  \/  | ___  _ __   ___  _ __   ___| |_   _               ║
║    | |\/| |/ _ \| '_ \ / _ \| '_ \ / _ \ | | | |              ║
║    | |  | | (_) | | | | (_) | |_) | (_) | | |_| |              ║
║    |_|  |_|\___/|_| |_|\___/| .__/ \___/|_|\__, |              ║
║                             |_|            |___/               ║
║                                                               ║
║              🤖 AI AGENTS EDITION 🤖                          ║
║         OpenAI GPT vs Ollama Llama 3.1                        ║
╚═══════════════════════════════════════════════════════════════╝
    """)


def print_turn_header(turn: int, player: str, phase: str):
    print(f"\n{'━'*60}")
    print(f"  TURN {turn} │ {player} │ Phase: {phase}")
    print(f"{'━'*60}")


def print_player_status(game: MonopolyGame, name: str):
    p = game.players[name]
    tile = game.tiles[p.position]
    
    status = "🔒 IN JAIL" if p.in_jail else ""
    print(f"  💰 ${p.money:<6} │ 📍 {tile.name:<25} │ 🏠 {len(p.properties)} properties {status}")


def print_all_players(game: MonopolyGame, current: str):
    print("\n  SCOREBOARD:")
    for name, p in sorted(game.players.items(), key=lambda x: -x[1].money):
        marker = "👉" if name == current else "  "
        status = "💀" if p.bankrupt else ("🔒" if p.in_jail else "")
        print(f"  {marker} {name}: ${p.money} │ {len(p.properties)} props {status}")


def run_game(agents: Dict[str, BaseAgent], max_turns: int = 100, delay: float = 1.0) -> Dict[str, Any]:
    """Run a full game with AI agents."""
    
    player_names = list(agents.keys())
    game = MonopolyGame(player_names)
    game.initialize()
    
    print(f"\n🎮 Game started with {len(player_names)} players!")
    print(f"   Players: {', '.join(player_names)}")
    print(f"   Max turns: {max_turns}")
    print_all_players(game, game.current_player.name)
    
    turn = 0
    actions_this_turn = 0
    max_actions_per_turn = 20  # Prevent infinite loops
    
    while game.phase != GamePhase.GAME_OVER and turn < max_turns:
        current_name = game.current_player.name
        agent = agents[current_name]
        
        # Get available actions
        available = game.get_available_actions()
        
        # New turn started
        if available["phase"] in ["waiting_for_roll", "in_jail"] and actions_this_turn == 0:
            turn += 1
            print_turn_header(turn, current_name, available["phase"])
            print_player_status(game, current_name)
        
        # Get agent's decision
        game_state = game.get_full_state()
        decision = agent.decide(game_state, available)
        
        action = decision.get("action", "").replace(" ", "_")
        params = decision.get("params", {})
        
        # Clean up action name (remove annotations like "(on positions: [1, 3])")
        if "(" in action:
            action = action.split("(")[0].strip()
        
        print(f"\n  🎯 {current_name} chose: {action}")
        if params:
            print(f"     params: {params}")
        
        # Execute the action
        result = execute_action(game, action, params)
        
        # Print result
        if "error" in result:
            print(f"  ❌ Error: {result['error']}")
        else:
            print_action_result(action, result)
        
        actions_this_turn += 1
        
        # Check if turn ended
        if action == "end_turn" or game.phase == GamePhase.GAME_OVER:
            actions_this_turn = 0
            print_all_players(game, game.current_player.name)
            time.sleep(delay)
        
        # Safety check
        if actions_this_turn > max_actions_per_turn:
            print(f"  ⚠️ Too many actions, forcing turn end")
            game.end_turn()
            actions_this_turn = 0
        
        # Small delay between actions
        time.sleep(delay * 0.3)
    
    # Game over
    print("\n" + "🏁" * 25)
    print("\n  GAME OVER!")
    
    active = [n for n, p in game.players.items() if not p.bankrupt]
    if len(active) == 1:
        winner = active[0]
        print(f"\n  🏆 WINNER: {winner}! 🏆")
    else:
        # Determine winner by net worth
        winner = max(game.players.items(), key=lambda x: x[1].money + len(x[1].properties) * 100)[0]
        print(f"\n  🏆 WINNER (by net worth): {winner}! 🏆")
    
    print_final_results(game)
    
    return {
        "winner": winner,
        "turns": turn,
        "final_state": game.get_full_state()
    }


def execute_action(game: MonopolyGame, action: str, params: Dict) -> Dict[str, Any]:
    """Execute a game action."""
    action_map = {
        "roll_dice_and_move": lambda: game.roll_and_move(),
        "buy_property": lambda: game.buy_current_property(),
        "decline_purchase": lambda: game.decline_purchase(),
        "place_bid": lambda: game.place_bid(params.get("player_name", ""), params.get("amount", 0)),
        "pass_auction": lambda: game.pass_auction(params.get("player_name", "")),
        "pay_jail_bail": lambda: game.pay_bail(),
        "use_jail_card": lambda: game.use_jail_card(),
        "roll_for_doubles": lambda: game.roll_for_doubles(),
        "build_house": lambda: game.build_house(params.get("property_position", 0)),
        "mortgage_property": lambda: game.mortgage_property(params.get("property_position", 0)),
        "unmortgage_property": lambda: game.unmortgage_property(params.get("property_position", 0)),
        "end_turn": lambda: game.end_turn(),
    }
    
    if action in action_map:
        return action_map[action]()
    return {"error": f"Unknown action: {action}"}


def print_action_result(action: str, result: Dict):
    """Pretty print action results."""
    if action == "roll_dice_and_move":
        dice = result.get("dice", [0, 0])
        doubles = "🎲 DOUBLES!" if result.get("doubles") else ""
        print(f"  🎲 Rolled [{dice[0]}][{dice[1]}] = {sum(dice)} {doubles}")
        print(f"  📍 Landed on: {result.get('tile', 'unknown')}")
        if result.get("result") == "unowned_property":
            print(f"  💵 Property available for ${result.get('price', 0)}")
        elif "rent" in str(result.get("result", "")):
            print(f"  💸 {result.get('result')}")
    
    elif action == "buy_property":
        if result.get("success"):
            print(f"  🏠 Bought {result.get('property')} for ${result.get('price')}")
    
    elif action == "end_turn":
        if result.get("success"):
            print(f"  ➡️ Next player: {result.get('next_player')}")
        elif result.get("game_over"):
            print(f"  🏁 Game Over! Winner: {result.get('winner')}")
    
    elif action == "place_bid":
        if result.get("success"):
            print(f"  💰 Bid ${result.get('bid')} on {result.get('property')}")
    
    elif action in ["pay_jail_bail", "use_jail_card", "roll_for_doubles"]:
        if result.get("success") or result.get("escaped"):
            print(f"  🔓 Escaped from jail!")
        elif result.get("forced_bail"):
            print(f"  💸 Forced to pay bail after 3 turns")


def print_final_results(game: MonopolyGame):
    """Print final game results."""
    print("\n" + "=" * 60)
    print("  FINAL STANDINGS")
    print("=" * 60)
    
    sorted_players = sorted(
        game.players.items(),
        key=lambda x: (not x[1].bankrupt, x[1].money + len(x[1].properties) * 100),
        reverse=True
    )
    
    for i, (name, p) in enumerate(sorted_players, 1):
        status = "💀 BANKRUPT" if p.bankrupt else ""
        net = p.money + len(p.properties) * 100
        print(f"  {i}. {name}")
        print(f"     Cash: ${p.money} │ Properties: {len(p.properties)} │ Net: ${net} {status}")
        if p.properties:
            props = [game.tiles[pos].name for pos in p.properties[:3]]
            if len(p.properties) > 3:
                props.append(f"...+{len(p.properties)-3} more")
            print(f"     Owns: {', '.join(props)}")
    
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Monopoly AI Game")
    parser.add_argument("--player1", default="ChatGPT", help="Name of player 1")
    parser.add_argument("--player1-type", default="openai", choices=["openai", "ollama", "human"])
    parser.add_argument("--player1-model", default="gpt-4o-mini", help="Model for player 1")
    parser.add_argument("--player2", default="Llama", help="Name of player 2")
    parser.add_argument("--player2-type", default="ollama", choices=["openai", "ollama", "human"])
    parser.add_argument("--player2-model", default="llama3.1", help="Model for player 2")
    parser.add_argument("--max-turns", type=int, default=100, help="Maximum turns")
    parser.add_argument("--delay", type=float, default=0.5, help="Delay between actions (seconds)")
    parser.add_argument("--openai-key", help="OpenAI API key (or set OPENAI_API_KEY env var)")
    parser.add_argument("--ollama-host", default="http://localhost:11434", help="Ollama host URL")
    args = parser.parse_args()
    
    print_banner()
    
    # Set up API key
    if args.openai_key:
        os.environ["OPENAI_API_KEY"] = args.openai_key
    
    # Create agents
    print("\n🤖 Initializing AI Agents...")
    
    agents = {}
    
    # Player 1
    if args.player1_type == "openai":
        agents[args.player1] = OpenAIAgent(args.player1, model=args.player1_model)
        print(f"  ✓ {args.player1}: OpenAI {args.player1_model}")
    elif args.player1_type == "ollama":
        agents[args.player1] = OllamaAgent(args.player1, model=args.player1_model, host=args.ollama_host)
        print(f"  ✓ {args.player1}: Ollama {args.player1_model}")
    else:
        agents[args.player1] = create_agent(args.player1, "human")
        print(f"  ✓ {args.player1}: Human player")
    
    # Player 2
    if args.player2_type == "openai":
        agents[args.player2] = OpenAIAgent(args.player2, model=args.player2_model)
        print(f"  ✓ {args.player2}: OpenAI {args.player2_model}")
    elif args.player2_type == "ollama":
        agents[args.player2] = OllamaAgent(args.player2, model=args.player2_model, host=args.ollama_host)
        print(f"  ✓ {args.player2}: Ollama {args.player2_model}")
    else:
        agents[args.player2] = create_agent(args.player2, "human")
        print(f"  ✓ {args.player2}: Human player")
    
    # Run the game
    print("\n" + "=" * 60)
    input("Press Enter to start the game...")
    
    result = run_game(agents, max_turns=args.max_turns, delay=args.delay)
    
    print(f"\n✅ Game completed in {result['turns']} turns")
    print(f"🏆 Winner: {result['winner']}")


if __name__ == "__main__":
    main()