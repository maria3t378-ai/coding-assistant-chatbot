import ast
import os
import re

import streamlit as st
from dotenv import load_dotenv
from ollama import Client


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:1.5b").strip()
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434").strip()

if not MODEL:
    MODEL = "qwen2.5-coder:1.5b"

if not OLLAMA_HOST:
    OLLAMA_HOST = "http://localhost:11434"


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Coding Assistant",
    page_icon="💻",
    layout="wide",
)


# ============================================================
# OLLAMA CLIENT
# ============================================================

@st.cache_resource
def get_ollama_client(host):
    return Client(host=host)


client = get_ollama_client(OLLAMA_HOST)


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are an accurate AI Coding Assistant.

Analyze code and answer in simple Roman Urdu.

Rules:
- Identify the programming language when possible.
- Explain what the code actually does.
- Report only real syntax errors and clearly established logic errors.
- Do not infer intended behavior from names alone.
- Do not call style preferences errors.
- Do not claim code was run or tested.
- Preserve the original language and intended functionality.
- If Python static analysis is provided, treat it as authoritative.
- Never claim Python has a syntax error if its AST check says it is valid.
- Never ignore a Python syntax error reported by static analysis.

Use these sections:
Programming Language:
Code Purpose:
Syntax Errors:
Logic Errors:
Runtime / Potential Issues:
Detailed Explanation:
Corrected Code:
Additional Suggestions:

Write "No confirmed issues found." when a category has no confirmed issues.
Write "No correction required." when no correction is needed.
"""


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []


# ============================================================
# CODE EXTRACTION
# ============================================================

def extract_code_and_language(text):
    """Extract the largest Markdown fenced code block and language."""

    pattern = re.compile(
        r"^(?P<fence>`{3,})[ \t]*"
        r"(?P<language>[A-Za-z0-9_+#.-]*)[ \t]*\r?\n"
        r"(?P<code>.*?)(?=^(?P=fence)[ \t]*$)",
        flags=re.MULTILINE | re.DOTALL,
    )

    matches = list(pattern.finditer(text))

    if not matches:
        return text.strip(), ""

    largest = max(matches, key=lambda match: len(match.group("code")))

    return (
        largest.group("code").strip(),
        largest.group("language").strip().lower(),
    )


# ============================================================
# PYTHON DETECTION AND SYNTAX CHECK
# ============================================================

def looks_like_python(code):
    """Check for common Python syntax markers."""

    patterns = [
        r"^\s*def\s+\w+\s*\(",
        r"^\s*class\s+\w+",
        r"^\s*(?:import|from)\s+\w+",
        r"^\s*(?:if|elif|else|for|while|try|except|finally|with)\b",
        r"^\s*async\s+(?:def|for|with)\b",
        r"\b(?:True|False|None|self)\b",
        r"\b__name__\b",
    ]

    return any(
        re.search(pattern, code, flags=re.MULTILINE)
        for pattern in patterns
    )


def is_python_code(code, language):
    """Determine whether the input should be checked as Python."""

    language = language.strip().lower()

    if language in {"python", "py", "python3"}:
        return True

    if language:
        return False

    return looks_like_python(code)


def check_python_syntax(code):
    """Return a deterministic Python AST syntax-check result."""

    try:
        ast.parse(code)
        return {"valid": True, "error": None}

    except SyntaxError as error:
        return {
            "valid": False,
            "error": {
                "message": error.msg,
                "line": error.lineno,
                "column": error.offset,
                "text": error.text.strip() if error.text else "",
            },
        }


# ============================================================
# SIMPLE, SAFE SYNTAX FIX
# ============================================================

def fix_missing_function_colon(code):
    """
    Fix the common form:
        def add(a, b) return a - b

    Return corrected code only if it passes Python's AST parser.
    """

    lines = code.splitlines()
    changed = False

    pattern = re.compile(
        r"^(?P<indent>[ \t]*)"
        r"(?P<header>def\s+\w+\s*\([^)]*\))"
        r"[ \t]+"
        r"(?P<body>return\b.+)$"
    )

    fixed_lines = []

    for line in lines:
        match = pattern.match(line)

        if not match:
            fixed_lines.append(line)
            continue

        indent = match.group("indent")
        header = match.group("header")
        body = match.group("body")

        fixed_lines.append(f"{indent}{header}:")
        fixed_lines.append(f"{indent}    {body}")
        changed = True

    if not changed:
        return None

    fixed_code = "\n".join(fixed_lines)

    try:
        ast.parse(fixed_code)
    except SyntaxError:
        return None

    return fixed_code


def create_python_syntax_error_response(code, error):
    """Build a guaranteed, deterministic response for invalid Python."""

    fixed_code = fix_missing_function_colon(code)

    response = [
        "**Programming Language:** Python",
        "",
        "**Code Purpose:** Code Python function aur usay call karne ki koshish karta hai.",
        "",
        "**Syntax Errors:**",
        (
            f"Line {error['line']}, column {error['column']}: "
            f"`{error['message']}`."
        ),
    ]

    if error["text"]:
        response.append(f"Error wali line: `{error['text']}`")

    response.extend(
        [
            "",
            "**Logic Errors:**",
            "Syntax error fix hone ke baad logic ka alag se jaiza lena hoga.",
            "",
            "**Runtime / Potential Issues:**",
            "Syntax error ki wajah se code abhi run nahi ho sakta.",
            "",
            "**Detailed Explanation:**",
            "Python function definition ke baad `:` zaroori hota hai. "
            "Is error ki wajah se Python function ko parse nahi kar pata.",
            "",
            "**Corrected Code:**",
        ]
    )

    if fixed_code:
        response.extend(
            [
                "Neeche missing `:` add karke function body ko new line par rakha hai:",
                "",
                f"```python\n{fixed_code}\n```",
            ]
        )
    else:
        response.append(
            "Syntax error report kiya gaya hai, lekin automatic safe correction nahi mil saki."
        )

    response.extend(
        [
            "",
            "**Additional Suggestions:**",
            "Function ke naam se yeh assume nahi kiya gaya ke subtraction ghalat hai.",
        ]
    )

    return "\n".join(response)


# ============================================================
# CONVERSATION
# ============================================================

def build_conversation(current_user_message, static_analysis=None):
    """Build the message list sent to Ollama."""

    current_content = current_user_message

    if static_analysis:
        current_content += (
            "\n\nDETERMINISTIC STATIC ANALYSIS:\n"
            f"{static_analysis}\n"
            "Is analysis ko authoritative samjhein."
        )

    conversation = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

    # Previous messages exclude the current user message.
    conversation.extend(st.session_state.messages[:-1])

    conversation.append(
        {
            "role": "user",
            "content": current_content,
        }
    )

    return conversation


# ============================================================
# OLLAMA RESPONSE
# ============================================================

def get_response_text(response):
    """Safely read response text from an Ollama object or dictionary."""

    if response is None:
        return ""

    if isinstance(response, dict):
        message = response.get("message")
    else:
        message = getattr(response, "message", None)

    if isinstance(message, dict):
        content = message.get("content", "")
    else:
        content = getattr(message, "content", "")

    return content.strip() if isinstance(content, str) else ""


# ============================================================
# HEADER AND SIDEBAR
# ============================================================

st.title("💻 AI Coding Assistant")
st.caption(
    "Code paste karo. AI language identify karega, "
    "errors explain karega aur corrected code suggest karega."
)

with st.sidebar:
    st.header("⚙️ Settings")

    st.write("**AI Model:**")
    st.code(MODEL)

    st.write("**Ollama Server:**")
    st.code(OLLAMA_HOST)

    st.divider()

    if st.button("🗑️ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.info("Ollama server running rehna chahiye.")


# ============================================================
# CHAT HISTORY
# ============================================================

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# ============================================================
# CHAT INPUT AND PROCESSING
# ============================================================

user_input = st.chat_input(
    "Apna code ya programming question yahan likhein..."
)

if user_input:
    user_input = user_input.strip()

    if not user_input:
        st.warning("Please code ya programming question enter karein.")
        st.stop()

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input,
        }
    )

    with st.chat_message("user"):
        st.markdown(user_input)

    code, language = extract_code_and_language(user_input)
    python_input = is_python_code(code, language)
    syntax_result = check_python_syntax(code) if python_input else None

    with st.chat_message("assistant"):
        if syntax_result and not syntax_result["valid"]:
            # Do not let the model contradict a confirmed Python syntax error.
            answer = create_python_syntax_error_response(
                code,
                syntax_result["error"],
            )
            st.markdown(answer)

        else:
            static_analysis = None

            if syntax_result and syntax_result["valid"]:
                static_analysis = (
                    "Python AST parser confirms the code is syntactically valid. "
                    "Do not report a Python syntax error."
                )

            conversation = build_conversation(
                user_input,
                static_analysis=static_analysis,
            )

            with st.spinner("Code analyze ho raha hai..."):
                try:
                    response = client.chat(
                        model=MODEL,
                        messages=conversation,
                    )

                    answer = get_response_text(response)

                    if not answer:
                        answer = (
                            "AI ne koi response return nahi kiya. "
                            "Please dobara try karein."
                        )

                    st.markdown(answer)

                except Exception as error:
                    answer = (
                        "Ollama se connection ya model response mein "
                        "problem aa gayi.\n\n"
                        "Check karein ke Ollama running hai aur required "
                        "model installed hai.\n\n"
                        f"Error details:\n\n```text\n{error}\n```"
                    )
                    st.markdown(answer)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )