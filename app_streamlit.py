from __future__ import annotations

import asyncio
import os

import streamlit as st
from dotenv import load_dotenv

from client_langchain import DEFAULT_MODEL, _run_agent, _stream_agent_response


def _run_async(coro):
    try:
        return asyncio.run(coro)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()


def _ask_agent(prompt: str, model: str, temperature: float) -> str:
    return _run_async(
        _run_agent(
            user_prompt=prompt,
            model=model,
            temperature=temperature,
            list_tools=False,
        )
    )


def _list_tools(model: str, temperature: float) -> str:
    return _run_async(
        _run_agent(
            user_prompt="List available tools",
            model=model,
            temperature=temperature,
            list_tools=True,
        )
    )


def _stream_agent_to_ui(placeholder, prompt: str, model: str, temperature: float) -> str:
    async def _runner() -> str:
        parts: list[str] = []
        async for token in _stream_agent_response(
            user_prompt=prompt,
            model=model,
            temperature=temperature,
        ):
            parts.append(token)
            placeholder.markdown("".join(parts))
        return "".join(parts)

    return _run_async(_runner())


def main() -> None:
    load_dotenv()
    st.set_page_config(page_title="TIB MCP Chat", layout="wide")

    st.title("TIB MCP Chat")
    st.caption("LangChain + OpenAI + FastMCP tools")

    with st.sidebar:
        st.subheader("Configuration")
        model = st.text_input("OpenAI model", value=os.getenv("OPENAI_MODEL", DEFAULT_MODEL))
        temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.0, step=0.1)

        if st.button("List MCP tools", use_container_width=True):
            try:
                tool_names = _list_tools(model=model, temperature=temperature)
                st.code(tool_names, language="text")
            except Exception as exc:  # pragma: no cover
                st.error(f"Unable to list tools: {exc}")

        st.markdown("---")
        st.write("MCP transport", os.getenv("MCP_CLIENT_TRANSPORT", "streamable-http"))
        st.write("MCP endpoint", os.getenv("MCP_CLIENT_URL", "http://127.0.0.1:8000/mcp"))

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("Ask me anything about scientific papers")
    if not prompt:
        return

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if not os.getenv("OPENAI_API_KEY"):
        error_msg = "OPENAI_API_KEY is missing from your environment or .env file."
        st.session_state.messages.append({"role": "assistant", "content": error_msg})
        with st.chat_message("assistant"):
            st.error(error_msg)
        return

    with st.chat_message("assistant"):
        with st.spinner("I'm thinking with the MCP tools..."):
            try:
                response_placeholder = st.empty()
                response = _stream_agent_to_ui(
                    response_placeholder,
                    prompt=prompt,
                    model=model,
                    temperature=temperature,
                )
                if not response:
                    response = _ask_agent(prompt=prompt, model=model, temperature=temperature)
                    response_placeholder.markdown(response)
            except Exception as exc:
                response = f"Error: {exc}"
                st.error(response)

    st.session_state.messages.append({"role": "assistant", "content": response})


if __name__ == "__main__":
    main()
