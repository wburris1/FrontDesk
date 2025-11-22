import json
from openai import OpenAI
from ..config import Config
from .prompts import SYSTEM_PROMPT
from .tools import TOOLS, execute_tool_call

client = OpenAI(api_key=Config.OPENAI_API_KEY)
    
class LLMManager:
    def __init__(self):
        self.history = []  # list of dicts with role/content

    def add(self, role, content):
        self.history.append({"role": role, "content": content})

    def ask(self, user_text: str) -> str:
        self.add("user", user_text)
        
        # Initial LLM response
        response = client.responses.create(
            model=Config.OPENAI_MODEL,
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                *self.history
            ],
            tools=TOOLS,
            tool_choice="auto"
        )
        
        # Look for a tool call anywhere in response.output
        tool_call_obj = None
        message_obj = None

        for item in response.output:
            # Detect ResponseFunctionToolCall
            if hasattr(item, "type") and item.type == "function_call":
                tool_call_obj = item
                break
            # Optionally capture a normal message if present
            elif hasattr(item, "content") and item.content:
                message_obj = item

        # 3. If there is a tool call
        if tool_call_obj:
            tool_name = tool_call_obj.name
            args = json.loads(tool_call_obj.arguments)

            print(args)
            print(tool_call_obj)
            tool_result = execute_tool_call(tool_name, args)

            self.add("assistant", f"<tool_call:{tool_name}>{args}")
            self.add("assistant", f"<tool_call_result:{tool_name}>{json.dumps(tool_result)}")

            # Ask LLM to produce final natural-language reply
            followup = client.responses.create(
                model=Config.OPENAI_MODEL,
                input=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    *self.history
                ]
            )

            final_text = followup.output[0].content[0].text
            self.add("assistant", final_text)
            return final_text

        # Otherwise, normal assistant message
        if message_obj:
            final_text = message_obj.content[0].text
        else:
            # fallback: first content of output[0] if nothing else
            final_text = response.output[0].content[0].text

        self.add("assistant", final_text)
        return final_text