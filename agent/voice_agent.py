"""
AI Agent Module
Uses ChatOllama with bind_tools() + manual tool dispatch loop.
Compatible with langchain-ollama and langchain-core v0.3+.
No dependency on langchain.agents at all.
"""

from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from tools.system_tools import SYSTEM_TOOLS
from typing import Optional, Callable
import json


# ─── System Prompt ────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are VoiceFlow, a helpful voice assistant running locally on the user's computer.

You have tools to perform system actions like opening websites, launching apps, and searching the web.

Rules:
- For "open youtube / google / github / etc" -> use open_website tool
- For "open notepad / calculator / terminal / etc" -> use open_application tool
- For "search for X" or "look up X" -> use search_web tool
- For "play X on youtube" or "search youtube for X" -> use search_youtube tool
- For everything else, answer directly from your knowledge
- Keep responses brief and conversational — they will be spoken aloud
- Never use markdown formatting in responses
"""


class VoiceAgent:
    def __init__(
        self,
        model_name: str = "minimax-m2.7:cloud",
        base_url: str = "http://localhost:11434",
        temperature: float = 0.7,
        memory_window: int = 10,
    ):
        self.model_name = model_name
        self.base_url = base_url
        self.temperature = temperature
        self.memory_window = memory_window
        self._llm = None
        self._llm_with_tools = None
        self._chat_history: list = []  # list of LangChain message objects
        self._tool_map = {t.name: t for t in SYSTEM_TOOLS}

    def initialize(self, status_callback: Optional[Callable] = None) -> bool:
        """Initialize the LLM. Returns True on success."""
        try:
            if status_callback:
                status_callback(f"Loading model '{self.model_name}' via Ollama...")

            self._llm = ChatOllama(
                model=self.model_name,
                base_url=self.base_url,
                temperature=self.temperature,
            )

            # Verify connection
            self._llm.invoke("Hi")

            # Bind tools so the model knows what's available
            self._llm_with_tools = self._llm.bind_tools(SYSTEM_TOOLS)

            if status_callback:
                status_callback(f"✅ Agent ready with model: {self.model_name}")
            return True

        except Exception as e:
            if status_callback:
                status_callback(f"❌ Failed to initialize agent: {e}")
            return False

    def process(self, user_input: str) -> str:
        """Process user input, execute any tool calls, return final response."""
        if not self._llm_with_tools:
            return "❌ Agent not initialized. Please check Ollama is running."

        if not user_input.strip():
            return "I didn't receive any input. Please try again."

        try:
            # Build message list: system + recent history + new user message
            messages = [SystemMessage(content=SYSTEM_PROMPT)]
            messages += self._chat_history[-self.memory_window * 2:]
            messages.append(HumanMessage(content=user_input))

            # First LLM call — may return tool calls
            response = self._llm_with_tools.invoke(messages)

            # Tool execution loop
            max_loops = 5
            loop = 0
            while hasattr(response, "tool_calls") and response.tool_calls and loop < max_loops:
                messages.append(response)  # append the AIMessage with tool_calls

                for tool_call in response.tool_calls:
                    tool_name = tool_call["name"]
                    tool_args = tool_call["args"]
                    tool_id   = tool_call.get("id", tool_name)

                    tool = self._tool_map.get(tool_name)
                    if tool:
                        try:
                            # args may be a dict or a plain string
                            if isinstance(tool_args, dict):
                                # Most tools take a single string arg
                                arg_value = next(iter(tool_args.values()), "")
                                tool_result = tool.invoke(arg_value)
                            else:
                                tool_result = tool.invoke(str(tool_args))
                        except Exception as e:
                            tool_result = f"Tool error: {e}"
                    else:
                        tool_result = f"Unknown tool: {tool_name}"

                    messages.append(
                        ToolMessage(content=str(tool_result), tool_call_id=tool_id)
                    )

                # Follow-up LLM call with tool results
                response = self._llm.invoke(messages)  # plain LLM, no tools needed now
                loop += 1

            # Extract final text
            output = response.content if hasattr(response, "content") else str(response)
            output = output.strip().replace("**", "").replace("`", "")

            # Save to history
            self._chat_history.append(HumanMessage(content=user_input))
            self._chat_history.append(AIMessage(content=output))

            return output

        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}"

    def clear_memory(self):
        self._chat_history.clear()

    def change_model(
        self, model_name: str, status_callback: Optional[Callable] = None
    ) -> bool:
        self.model_name = model_name
        self.clear_memory()
        return self.initialize(status_callback)

    @staticmethod
    def get_available_models() -> list:
        import subprocess
        try:
            result = subprocess.run(
                ["ollama", "list"], capture_output=True, text=True, timeout=5
            )
            lines = result.stdout.strip().split("\n")[1:]
            models = [line.split()[0] for line in lines if line.strip()]

            # Ollama cloud models
            cloud_models = ["minimax-m2.7:cloud", "kimi-k2.5:cloud" , "gemma4:31b-cloud"]
            for m in cloud_models:
                if m not in models:
                    models.append(m)

            return models if models else ["minimax-m2.7:cloud", "kimi-k2.5:cloud" , "gemma4:31b-cloud"]
        except Exception:
            return ["minimax-m2.7:cloud", "kimi-k2.5:cloud", "gemma4:31b-cloud"]