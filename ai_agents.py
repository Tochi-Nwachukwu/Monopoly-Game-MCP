"""
AI Agents for Monopoly - Uses OpenAI and Ollama to make game decisions
"""

import json
import os
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


SYSTEM_PROMPT = """You are playing Monopoly. You are a strategic player who wants to win.

RULES REMINDER:
- Buy properties when you can afford them, especially to complete color groups
- Building houses requires owning ALL properties in a color group
- Railroads are valuable - rent increases with each one owned
- Utilities multiply dice roll (4x for one, 10x for both)
- In jail: can pay $50, use Get Out of Jail Free card, or try rolling doubles (3 attempts max)
- In jail: if you cannot afford the jail bail, and you cannot roll doubles. you can choose to skip your turn
- Mortgaging gives you half the property value but you can't collect rent
- If you do not have the money to buy a property, and the acution fails repeatedly, you should choose to end your turn.
- If you bid 5 times, and it is not accepted, you MUST end your turn
- If you need more cash, and you have properties, you can choose to Mortgage properties

STRATEGY TIPS:
- Orange and red properties have best ROI
- Complete color groups to build houses
- Keep cash reserves for rent payments
- Mortgage less valuable properties if needed
- If you do not have enough money to buy a property, you can take another decision to keep the game going on
- If you need more cash, and you have properties, you may choose to Mortgage properties to get some cash.
- If you are getting bankrupt. You MUST choose to Mortgage properties to cover the debt

You must respond with ONLY a valid JSON object containing your decision.
No explanation, no markdown, just the JSON."""


def get_action_prompt(game_state: Dict, player_name: str, available_actions: List[str]) -> str:
    player_info = game_state["players"].get(player_name, {})
    
    prompt = f"""
GAME STATE:
- Your name: {player_name}
- Your money: ${player_info.get('money', 0)}
- Your position: {player_info.get('tile_name', 'Unknown')} (position {player_info.get('position', 0)})
- Your properties: {', '.join(player_info.get('properties', [])) or 'None'}
- In jail: {player_info.get('in_jail', False)}
- Get Out of Jail cards: {player_info.get('jail_cards', 0)}

CURRENT PHASE: {game_state.get('phase', 'unknown')}
LAST DICE ROLL: {game_state.get('last_dice', [0,0])}

OTHER PLAYERS:
"""
    for name, info in game_state["players"].items():
        if name != player_name:
            prompt += f"- {name}: ${info['money']}, {len(info.get('properties', []))} properties\n"

    prompt += f"""
AVAILABLE ACTIONS: {available_actions}

RECENT EVENTS:
{chr(10).join(game_state.get('recent_messages', [])[-5:])}

Choose your action. Respond with JSON only:
{{"action": "<action_name>", "params": {{}}}}

For place_bid: {{"action": "place_bid", "params": {{"player_name": "{player_name}", "amount": <bid_amount>}}}}
For pass_auction: {{"action": "pass_auction", "params": {{"player_name": "{player_name}"}}}}
For build_house: {{"action": "build_house", "params": {{"property_position": <position>}}}}
For mortgage/unmortgage: {{"action": "<action>", "params": {{"property_position": <position>}}}}
For other actions: {{"action": "<action_name>", "params": {{}}}}
"""
    return prompt


class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    def decide(self, game_state: Dict, available_actions: Dict) -> Dict[str, Any]:
        pass
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response to extract JSON action."""
        response = response.strip()
        
        # Try to extract JSON from response
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0]
        elif "```" in response:
            response = response.split("```")[1].split("```")[0]
        
        response = response.strip()
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Fallback: try to find JSON object
            import re
            match = re.search(r'\{[^{}]*\}', response)
            if match:
                try:
                    return json.loads(match.group())
                except:
                    pass
            return {"action": "end_turn", "params": {}}


class OpenAIAgent(BaseAgent):
    """Agent powered by OpenAI GPT models."""
    
    def __init__(self, name: str, model: str = "gpt-4o-mini", api_key: str = None):
        super().__init__(name)
        self.model = model
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
    
    def decide(self, game_state: Dict, available_actions: Dict) -> Dict[str, Any]:
        actions_list = available_actions.get("actions", [])
        
        if not actions_list:
            return {"action": "end_turn", "params": {}}
        
        # Simple actions that don't need LLM
        if actions_list == ["end_turn"]:
            return {"action": "end_turn", "params": {}}
        if actions_list == ["roll_dice_and_move"]:
            return {"action": "roll_dice_and_move", "params": {}}
        
        prompt = get_action_prompt(game_state, self.name, actions_list)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            content = response.choices[0].message.content
            print(f"  [{self.name}] thinking: {content[:100]}...")
            
            decision = self._parse_response(content)
            return decision
            
        except Exception as e:
            print(f"  [{self.name}] OpenAI error: {e}")
            # Fallback to simple logic
            return self._fallback_decision(game_state, actions_list)
    
    def _fallback_decision(self, game_state: Dict, actions: List[str]) -> Dict[str, Any]:
        """Simple fallback logic if API fails."""
        player = game_state["players"].get(self.name, {})
        
        if "roll_dice_and_move" in actions:
            return {"action": "roll_dice_and_move", "params": {}}
        if "buy_property" in actions and player.get("money", 0) > 200:
            return {"action": "buy_property", "params": {}}
        if "decline_purchase" in actions:
            return {"action": "decline_purchase", "params": {}}
        if "pay_jail_bail" in actions and player.get("money", 0) > 100:
            return {"action": "pay_jail_bail", "params": {}}
        if "roll_for_doubles" in actions:
            return {"action": "roll_for_doubles", "params": {}}
        if "end_turn" in actions:
            return {"action": "end_turn", "params": {}}
        
        return {"action": actions[0] if actions else "end_turn", "params": {}}


class OllamaAgent(BaseAgent):
    """Agent powered by Ollama local models (Llama 3.1, etc.)."""
    
    def __init__(self, name: str, model: str = "llama3.1", host: str = "http://localhost:11434"):
        super().__init__(name)
        self.model = model
        self.host = host
        # Use OpenAI client with Ollama endpoint
        self.client = OpenAI(
            base_url=f"{host}/v1",
            api_key="ollama"  # Ollama doesn't need real key
        )
    
    def decide(self, game_state: Dict, available_actions: Dict) -> Dict[str, Any]:
        actions_list = available_actions.get("actions", [])
        
        if not actions_list:
            return {"action": "end_turn", "params": {}}
        
        # Simple actions that don't need LLM
        if actions_list == ["end_turn"]:
            return {"action": "end_turn", "params": {}}
        if actions_list == ["roll_dice_and_move"]:
            return {"action": "roll_dice_and_move", "params": {}}
        
        prompt = get_action_prompt(game_state, self.name, actions_list)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            content = response.choices[0].message.content
            print(f"  [{self.name}] thinking: {content[:100]}...")
            
            decision = self._parse_response(content)
            return decision
            
        except Exception as e:
            print(f"  [{self.name}] Ollama error: {e}")
            return self._fallback_decision(game_state, actions_list)
    
    def _fallback_decision(self, game_state: Dict, actions: List[str]) -> Dict[str, Any]:
        """Simple fallback logic if API fails."""
        player = game_state["players"].get(self.name, {})
        
        if "roll_dice_and_move" in actions:
            return {"action": "roll_dice_and_move", "params": {}}
        if "buy_property" in actions and player.get("money", 0) > 200:
            return {"action": "buy_property", "params": {}}
        if "decline_purchase" in actions:
            return {"action": "decline_purchase", "params": {}}
        if "pay_jail_bail" in actions and player.get("money", 0) > 100:
            return {"action": "pay_jail_bail", "params": {}}
        if "roll_for_doubles" in actions:
            return {"action": "roll_for_doubles", "params": {}}
        if "end_turn" in actions:
            return {"action": "end_turn", "params": {}}
        
        return {"action": actions[0] if actions else "end_turn", "params": {}}


class HumanAgent(BaseAgent):
    """Human player via terminal input."""
    
    def decide(self, game_state: Dict, available_actions: Dict) -> Dict[str, Any]:
        actions_list = available_actions.get("actions", [])
        player = game_state["players"].get(self.name, {})
        
        print(f"\n{'='*50}")
        print(f"YOUR TURN: {self.name}")
        print(f"Money: ${player.get('money', 0)}")
        print(f"Position: {player.get('tile_name')} ({player.get('position')})")
        print(f"Properties: {', '.join(player.get('properties', [])) or 'None'}")
        print(f"\nAvailable actions:")
        for i, action in enumerate(actions_list, 1):
            print(f"  {i}. {action}")
        
        while True:
            try:
                choice = input("\nEnter action number: ").strip()
                idx = int(choice) - 1
                if 0 <= idx < len(actions_list):
                    action = actions_list[idx]
                    break
                print("Invalid choice")
            except ValueError:
                print("Enter a number")
        
        params = {}
        if "bid" in action:
            params["player_name"] = self.name
            params["amount"] = int(input("Bid amount: $"))
        elif "auction" in action:
            params["player_name"] = self.name
        elif "property_position" in action or "build" in action or "mortgage" in action:
            params["property_position"] = int(input("Property position (0-39): "))
        
        return {"action": action.split()[0], "params": params}


def create_agent(name: str, agent_type: str, **kwargs) -> BaseAgent:
    """Factory function to create agents."""
    if agent_type == "openai":
        return OpenAIAgent(name, **kwargs)
    elif agent_type == "ollama":
        return OllamaAgent(name, **kwargs)
    elif agent_type == "human":
        return HumanAgent(name)
    else:
        raise ValueError(f"Unknown agent type: {agent_type}")