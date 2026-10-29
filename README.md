# SynTree OS — LL(1) Parse Tree Generator & Compiler Workbench

An interactive syntax analysis workbench and automated parse tree visualizer built with Python (Flask) and dynamic HTML5 Canvas.

## 🚀 Key Features
- **Context-Free Grammar (CFG) Processing**: Automatic extraction of non-terminals, terminals, and start symbol.
- **Set Computation**: Real-time evaluation of mathematical FIRST and FOLLOW sets.
- **LL(1) Matrix Construction**: Automatic predictive parsing table generation with conflict detection.
- **Pushdown Stack Emulation**: Step-by-step trace of parser actions, input stream pointers, and stack memory.
- **Dynamic Tree Visualization**: Canvas-rendered hierarchical parse tree for accepted strings.
- **Diagnostic Error Reporting**: Pinpointed syntax error detection for non-conforming tokens.

## 🛠️ Tech Stack
- **Backend**: Python 3.x, Flask
- **Frontend**: HTML5, CSS3 (Cyber Theme), JavaScript (HTML5 Canvas Engine)

## 💻 Local Setup & Execution
1. Clone the repository:
   ```bash
   git clone [https://github.com/](https://github.com/)<your-username>/<repo-name>.git
   cd <repo-name>