# 💻 AI Coding Assistant

An AI-powered coding assistant chatbot built with **Python, Streamlit, and Ollama**.

The application helps users analyze programming code, identify syntax errors, understand code behavior, and receive corrected code suggestions through a conversational interface.

## ✨ Features

* 🤖 AI-powered coding assistance
* 🔍 Automatic programming-language identification
* 🐛 Syntax-error detection
* 🧠 Logic-error analysis
* ⚠️ Runtime and potential-issue explanations
* 🛠️ Corrected-code suggestions
* 💬 Conversational chat interface
* 🐍 Deterministic Python syntax checking using Python's `AST` parser
* 🗑️ New Chat option
* 🔒 `.env` configuration kept out of GitHub
* 🏠 Runs locally using Ollama

## 🛠️ Technologies Used

* **Python**
* **Streamlit**
* **Ollama**
* **Qwen2.5-Coder 1.5B**
* **Python AST**
* **python-dotenv**
* **Regular Expressions**

## 📂 Project Structure

```text
coding-assistant-chatbot/
│
├── app.py
├── requirements.txt
├── .gitignore
└── README.md
```

## ⚙️ How It Works

The application uses **Streamlit** for the user interface and **Ollama** to run the local AI model.

When a user submits code:

1. The application receives the user's input.
2. Code blocks and language information are extracted.
3. Python code can be checked using Python's built-in `AST` parser.
4. The input and static-analysis information are sent to the Ollama model.
5. The AI analyzes the code.
6. The application displays:

   * Programming language
   * Code purpose
   * Syntax errors
   * Logic errors
   * Runtime/potential issues
   * Detailed explanation
   * Corrected code
   * Additional suggestions

## 🧪 Example

### Input

```python
def add(a, b) return a - b

print(add(5, 3))
```

### Detected Problem

```text
Syntax Error:
Missing ':' after def add(a, b)
```

### Corrected Code

```python
def add(a, b):
    return a - b

print(add(5, 3))
```

The application does not automatically treat `a - b` as an error simply because the function is named `add`.

## 📋 Requirements

Before running the project, make sure you have:

* Python 3.x
* Git
* Ollama
* A supported Ollama model

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/maria3t378-ai/coding-assistant-chatbot.git
```

### 2. Open the project folder

```bash
cd coding-assistant-chatbot
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

## 🤖 Ollama Setup

Install Ollama and make sure the Ollama server is running.

Pull the model used by this project:

```bash
ollama pull qwen2.5-coder:1.5b
```

Start the Ollama server if necessary:

```bash
ollama serve
```

The application uses:

```text
http://127.0.0.1:11434
```

## 🔐 Environment Configuration

Create a `.env` file in the project folder:

```env
OLLAMA_MODEL=qwen2.5-coder:1.5b
OLLAMA_HOST=http://localhost:11434
```

The `.env` file is excluded from Git using `.gitignore`.

## ▶️ Run the Application

Start Streamlit with:

```bash
python -m streamlit run app.py
```

Then open the local Streamlit address shown in the terminal.

## 💬 Example Questions

You can ask the assistant questions such as:

```text
Why is this Python code giving a syntax error?
```

```text
Explain this code in simple terms.
```

```text
Find the errors in this code.
```

```text
Correct this code without changing its intended functionality.
```

## 🔎 Static Analysis

For Python code, the application uses Python's built-in `ast` module to perform deterministic syntax checking.

This helps the application identify genuine Python syntax errors independently of the AI model.

For example:

```python
def hello()
    print("Hello")
```

The Python AST parser can identify the missing colon after the function definition.

## ⚠️ Limitations

This project uses a relatively small local AI model, so AI-generated explanations may not always be perfect.

The deterministic syntax checker currently provides additional validation for **Python** code.

Logic errors, runtime problems, and code in other programming languages are primarily analyzed by the AI model and may require additional testing or language-specific tools.

The application does not execute arbitrary user code.

## 🔒 Privacy

The application is designed to run locally using Ollama.

Code submitted to the chatbot is processed through the locally running Ollama service rather than requiring a cloud AI API.

## 📌 Future Improvements

Possible future improvements include:

* Support for more programming languages
* Language-specific linters
* Better static analysis
* Code formatting
* Error highlighting
* File upload support
* Code editor integration
* More AI models
* Improved conversation management
* Automated testing
* Deployment support

## 👩‍💻 Author

**Maria Siddique**

AI & Machine Learning Developer

GitHub: [maria3t378-ai](https://github.com/maria3t378-ai)

## ⭐ Project

If you find this project useful, consider giving the repository a ⭐ on GitHub.

---

**Built with Python, Streamlit, Ollama, and AI.**
