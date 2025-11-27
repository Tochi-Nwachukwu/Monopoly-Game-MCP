"""
Monopoly MCP Server - Exposes game actions as tools for AI agents
"""

import json
import asyncio
from typing import Any, Optional
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from game_engine import MonopolyGame, GamePhase


# Global game instance
game: Optional[MonopolyGame] = None
server = Server("monopoly-game")


def get_game() -> MonopolyGame:
    global game
    if game is None:
        raise ValueError("Game not initialized. Call 'start_game' first.")
    return game


# ============================================================================
# TOOL DEFINITIONS
# ============================================================================

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="start_game",
            description="Initialize a new Monopoly game with specified players. Must be called before any other action.",
            inputSchema={
                "type": "object",
                "properties": {
                    "players": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of player names",
                        "minItems": 2,
                        "maxItems": 6
                    }
                },
                "required": ["players"]
            }
        ),
        Tool(
            name="get_game_state",
            description="Get the current state of the game including all player positions, money, properties, and whose turn it is.",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="get_my_status",
            description="Get detailed status for a specific player including their money, position, properties, and available actions.",
            inputSchema={
                "type": "object",
                "properties": {
                    "player_name": {"type": "string", "description": "Name of the player"}
                },
                "required": ["player_name"]
            }
        ),
        Tool(
            name="roll_dice_and_move",
            description="Roll the dice and move the current player. Returns the dice result, new position, and what's on that tile.",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="buy_property",
            description="Buy the property the current player is standing on. Only works if property is unowned and player has enough money.",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="decline_purchase",
            description="Decline to buy the current property. This will trigger an auction among all players.",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="place_bid",
            description="Place a bid in the current auction.",
            inputSchema={
                "type": "object",
                "properties": {
                    "player_name": {"type": "string", "description": "Name of the bidding player"},
                    "amount": {"type": "integer", "description": "Bid amount in dollars", "minimum": 1}
                },
                "required": ["player_name", "amount"]
            }
        ),
        Tool(
            name="pass_auction",
            description="Pass (withdraw) from the current auction.",
            inputSchema={
                "type": "object",
                "properties": {
                    "player_name": {"type": "string", "description": "Name of the player passing"}
                },
                "required": ["player_name"]
            }
        ),
        Tool(
            name="pay_jail_bail",
            description="Pay $50 bail to get out of jail.",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="use_jail_card",
            description="Use a 'Get Out of Jail Free' card.",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="roll_for_doubles",
            description="Attempt to roll doubles to escape jail.",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="build_house",
            description="Build a house on a property you own. Must own all properties in the color group.",
            inputSchema={
                "type": "object",
                "properties": {
                    "property_position": {"type": "integer", "description": "Board position of the property (0-39)"}
                },
                "required": ["property_position"]
            }
        ),
        Tool(
            name="mortgage_property",
            description="Mortgage a property to get cash from the bank.",
            inputSchema={
                "type": "object",
                "properties": {
                    "property_position": {"type": "integer", "description": "Board position of the property"}
                },
                "required": ["property_position"]
            }
        ),
        Tool(
            name="unmortgage_property",
            description="Pay off a mortgage to restore a property.",
            inputSchema={
                "type": "object",
                "properties": {
                    "property_position": {"type": "integer", "description": "Board position of the property"}
                },
                "required": ["property_position"]
            }
        ),
        Tool(
            name="end_turn",
            description="End the current player's turn and move to the next player.",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="get_property_info",
            description="Get detailed information about a specific property on the board.",
            inputSchema={
                "type": "object",
                "properties": {
                    "position": {"type": "integer", "description": "Board position (0-39)"}
                },
                "required": ["position"]
            }
        ),
        Tool(
            name="get_available_actions",
            description="Get a list of valid actions the current player can take right now.",
            inputSchema={"type": "object", "properties": {}}
        ),
    ]


# ============================================================================
# TOOL HANDLERS
# ============================================================================

@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    global game
    
    try:
        if name == "start_game":
            players = arguments.get("players", ["Player1", "Player2"])
            game = MonopolyGame(players)
            result = game.initialize()
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        g = get_game()
        
        if name == "get_game_state":
            result = g.get_full_state()
        
        elif name == "get_my_status":
            player_name = arguments["player_name"]
            result = g.get_player_status(player_name)
        
        elif name == "roll_dice_and_move":
            result = g.roll_and_move()
        
        elif name == "buy_property":
            result = g.buy_current_property()
        
        elif name == "decline_purchase":
            result = g.decline_purchase()
        
        elif name == "place_bid":
            result = g.place_bid(arguments["player_name"], arguments["amount"])
        
        elif name == "pass_auction":
            result = g.pass_auction(arguments["player_name"])
        
        elif name == "pay_jail_bail":
            result = g.pay_bail()
        
        elif name == "use_jail_card":
            result = g.use_jail_card()
        
        elif name == "roll_for_doubles":
            result = g.roll_for_doubles()
        
        elif name == "build_house":
            result = g.build_house(arguments["property_position"])
        
        elif name == "mortgage_property":
            result = g.mortgage_property(arguments["property_position"])
        
        elif name == "unmortgage_property":
            result = g.unmortgage_property(arguments["property_position"])
        
        elif name == "end_turn":
            result = g.end_turn()
        
        elif name == "get_property_info":
            result = g.get_property_info(arguments["position"])
        
        elif name == "get_available_actions":
            result = g.get_available_actions()
        
        else:
            result = {"error": f"Unknown tool: {name}"}
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    except Exception as e:
        return [TextContent(type="text", text=json.dumps({"error": str(e)}))]


# ============================================================================
# SERVER ENTRY POINT
# ============================================================================

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="monopoly-game",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())