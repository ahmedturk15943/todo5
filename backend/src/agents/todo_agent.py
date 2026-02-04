"""
Gemini Agent for todo task management using proper function calling.
"""

from typing import List, Dict, Any, Optional
import os
import logging
from google import genai
from google.genai import types
from dotenv import load_dotenv

from ..mcp.server import mcp_server

load_dotenv()
logger = logging.getLogger(__name__)


class TodoAgent:
    """
    AI Agent using Gemini with native function calling.

    This implements a proper agent architecture where:
    1. The LLM decides when to use tools
    2. Tools are called through Gemini's function calling API
    3. Results are fed back to continue the conversation
    """

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")

        self.client = genai.Client(api_key=api_key)
        # Using gemini-flash-latest - may have separate quota
        self.model_name = "models/gemini-flash-latest"

        self.system_instruction = """You are a helpful AI Todo Assistant.

Your role is to help users manage their tasks naturally. You have these tools available:

1. **add_task** - Create a new task
2. **list_tasks** - Get the user's tasks (use this to find task IDs)
3. **complete_task** - Mark a task as completed (requires task_id)
4. **delete_task** - Delete a task (requires task_id)

**Important workflow for delete/complete operations:**
When a user wants to delete or complete a task by name (e.g., "delete the buy milk task"):
1. First call list_tasks to get all tasks
2. Find the matching task by title
3. Then call delete_task or complete_task with the task_id

Be conversational and helpful. Always confirm when you've completed an action."""

        logger.info(f"TodoAgent initialized with Gemini {self.model_name}")

    def _convert_mcp_tools_to_gemini(self) -> List[types.Tool]:
        """
        Convert MCP tool definitions to Gemini function declarations.

        Returns:
            List of Gemini Tool objects
        """
        mcp_tools = mcp_server.get_tools()
        gemini_functions = []

        for tool in mcp_tools:
            func_def = tool["function"]

            # Convert parameters, excluding user_id (we'll inject it)
            parameters = func_def["parameters"].copy()
            if "properties" in parameters:
                # Remove user_id from the schema since we inject it
                properties = parameters["properties"].copy()
                properties.pop("user_id", None)
                parameters["properties"] = properties

                # Remove user_id from required fields
                if "required" in parameters:
                    required = [r for r in parameters["required"] if r != "user_id"]
                    parameters["required"] = required

            gemini_functions.append(
                types.FunctionDeclaration(
                    name=func_def["name"],
                    description=func_def["description"],
                    parameters=parameters
                )
            )

        return [types.Tool(function_declarations=gemini_functions)]

    async def process_message(
        self,
        user_id: str,
        message: str,
        conversation_history: List[Dict[str, str]]
    ) -> tuple[str, List[Dict[str, Any]]]:
        """
        Process a user message using the agent architecture.

        Args:
            user_id: User identifier
            message: User's message
            conversation_history: Previous conversation messages

        Returns:
            Tuple of (response_text, tool_calls)
        """
        try:
            # Convert MCP tools to Gemini format (done dynamically to get latest tools)
            tools = self._convert_mcp_tools_to_gemini()

            # Build conversation history for Gemini
            contents = self._build_contents(conversation_history, message)

            tool_calls = []
            max_iterations = 5  # Prevent infinite loops

            # Agentic loop: keep calling functions until we get a text response
            for iteration in range(max_iterations):
                # Generate response with tools
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=self.system_instruction,
                        tools=tools,
                        temperature=0.7,
                    )
                )

                # Check if Gemini wants to call a function
                if response.candidates[0].content.parts:
                    has_function_call = False

                    for part in response.candidates[0].content.parts:
                        # Handle function calls
                        if hasattr(part, 'function_call') and part.function_call:
                            has_function_call = True
                            func_call = part.function_call
                            tool_name = func_call.name
                            tool_args = dict(func_call.args)

                            # Inject user_id
                            tool_args["user_id"] = user_id

                            logger.info(f"Agent calling tool: {tool_name} with args: {tool_args}")

                            # Execute the tool
                            result = await mcp_server.execute_tool(tool_name, tool_args)

                            tool_calls.append({
                                "tool": tool_name,
                                "parameters": tool_args,
                                "result": result
                            })

                            # Add function call to contents
                            contents.append(
                                types.Content(
                                    role="model",
                                    parts=[types.Part(function_call=func_call)]
                                )
                            )

                            # Add function response to contents
                            contents.append(
                                types.Content(
                                    role="user",
                                    parts=[
                                        types.Part(
                                            function_response=types.FunctionResponse(
                                                name=func_call.name,
                                                response={"result": result}
                                            )
                                        )
                                    ]
                                )
                            )

                            # Continue loop to allow next function call
                            break

                        # Handle text response
                        elif hasattr(part, 'text') and part.text:
                            return part.text.strip(), tool_calls

                    # If we had a function call, continue the loop
                    if has_function_call:
                        continue

                # Fallback if no parts
                return "I'm here to help! What would you like to do?", []

            # Max iterations reached
            logger.warning(f"Max iterations ({max_iterations}) reached in agent loop")
            return "I've completed the requested actions.", tool_calls

        except Exception as e:
            logger.error(f"Gemini Agent error: {e}", exc_info=True)
            return "I'm having trouble processing your request right now. Please try again.", []

    async def _generate_with_tool_result(
        self,
        original_contents: List,
        function_call: types.FunctionCall,
        tool_result: Any
    ) -> str:
        """
        Generate a natural language response after executing a tool.

        Args:
            original_contents: Original conversation contents
            function_call: The function call that was made
            tool_result: Result from executing the tool

        Returns:
            Natural language response
        """
        try:
            # Build contents with tool result
            contents = original_contents.copy()

            # Add the function call
            contents.append(
                types.Content(
                    role="model",
                    parts=[types.Part(function_call=function_call)]
                )
            )

            # Add the function response
            contents.append(
                types.Content(
                    role="user",
                    parts=[
                        types.Part(
                            function_response=types.FunctionResponse(
                                name=function_call.name,
                                response={"result": tool_result}
                            )
                        )
                    ]
                )
            )

            # Generate final response
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_instruction,
                    temperature=0.7,
                )
            )

            if response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'text') and part.text:
                        return part.text.strip()

            return "Done! ✅"

        except Exception as e:
            logger.error(f"Error generating response with tool result: {e}")
            return "Task completed successfully! ✅"

    def _build_contents(
        self,
        conversation_history: List[Dict[str, str]],
        current_message: str
    ) -> List[types.Content]:
        """
        Build Gemini contents from conversation history.

        Args:
            conversation_history: Previous messages
            current_message: Current user message

        Returns:
            List of Content objects for Gemini
        """
        contents = []

        # Add conversation history
        for msg in conversation_history:
            role = "user" if msg["role"] == "user" else "model"
            contents.append(
                types.Content(
                    role=role,
                    parts=[types.Part(text=msg["content"])]
                )
            )

        # Add current message
        contents.append(
            types.Content(
                role="user",
                parts=[types.Part(text=current_message)]
            )
        )

        return contents


# Global agent instance - lazy initialization
_todo_agent = None

def get_todo_agent():
    """Get or create the global TodoAgent instance."""
    global _todo_agent
    if _todo_agent is None:
        _todo_agent = TodoAgent()
    return _todo_agent

# For backward compatibility
todo_agent = None  # Will be initialized on first use
