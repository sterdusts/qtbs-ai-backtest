\# QTBS AI Quant Strategy Frontend



AI-Powered Natural Language Quantitative Strategy Backtesting Platform



\---



\# Overview



QTBS is an AI-assisted quantitative strategy backtesting platform designed for ordinary users.



Users do not need to write Python code or build quantitative infrastructures.



By simply describing a trading strategy in natural language, QTBS can:



\- Generate executable strategy code

\- Run historical backtests

\- Visualize trading behavior

\- Analyze whether the strategy implementation matches the user’s intent

\- Review potential risks and logic problems



The core goal of QTBS is:



> Reduce the barrier of quantitative strategy validation and improve transparency in AI-generated trading systems.



\---



\# Why QTBS



The internet is full of:



\- “High win-rate strategies”

\- “Profitable systems”

\- “Indicator combinations”

\- “Trading tutorials”



However, most ordinary users:



\- Cannot verify whether strategies are truly effective

\- Cannot write Python backtesting code

\- Cannot build quantitative environments

\- Cannot judge whether AI-generated code is logically correct



As a result:



> Strategy validation remains difficult, expensive, and opaque.



QTBS attempts to solve this problem through:



\- AI-generated strategy code

\- Explainable backtesting

\- Visualization

\- AI strategy auditing



\---



\# Core Features



\## Natural Language → Strategy Code



Example input:



```text

Go long when EMA12 crosses above EMA26.

Close the position on a dead cross.

```



QTBS automatically generates executable Python strategy functions.



\---



\## AI Strategy Review



QTBS automatically analyzes:



\- Whether the generated strategy matches the user’s description

\- Whether future data leakage exists

\- Whether unnecessary logic has been added

\- Potential trading risks



And generates:



\- Match score

\- Risk explanations

\- Strategy implementation notes



\---



\## Visualized Backtesting



QTBS automatically generates:



\- Candlestick charts

\- Entry / exit markers

\- Floating equity curves

\- Realized equity curves

\- Volume charts

\- Position curves



This allows users to visually verify trading behavior and strategy execution logic.



\---



\## Multi-language Support



Currently supported languages:



\- English

\- 中文

\- 한국어

\- 日本語

\- Русский

\- العربية



\---



\# Tech Stack



\## Frontend



\- Gradio

\- HTML

\- CSS

\- JavaScript



\## AI System



\- DeepSeek API

\- Natural language strategy parsing

\- AI strategy auditing



\## Backtesting Engine



\- Python

\- Pandas

\- NumPy



\## Visualization



\- Pyecharts

\- Apache ECharts



\---



\# Environment Setup



Before running the project, create a `.env` file in the project root directory.



Example:



```env

DEEPSEEK\_API\_KEY=your\_api\_key\_here

```



Current AI Provider:



```python

DEEPSEEK\_BASE\_URL = "https://api.deepseek.com"

MODEL\_NAME = "deepseek-chat"

```



Currently, QTBS only supports the DeepSeek API.



Get your API key from:



https://platform.deepseek.com/



\---



\# Installation



Install dependencies:



```bash

pip install -r requirements.txt

```



Run the project:



```bash

python webUI.py

```



\---



\# Important Notes



\- `.env` is not included in this repository for security reasons

\- Never upload API keys to GitHub

\- Make sure `.env` is added to `.gitignore`



Example:



```gitignore

.env

```



\---



\# Current Status



Current version already supports:



\- Natural-language strategy generation

\- Historical backtesting

\- Visualized chart systems

\- AI strategy match analysis

\- Multi-language UI support



\---



\# Future Plans



Planned future features:



\- Advanced position management systems

\- Multi-strategy portfolios

\- AI-driven strategy optimization

\- Risk analysis modules

\- Local model deployment

\- More OpenAI-compatible API providers



\---



\# Project Positioning



QTBS is not intended to compete with institutional-grade quantitative trading platforms.



It is currently positioned as:



\- AI-assisted strategy verification tool

\- Educational quant platform

\- Lightweight quantitative analysis platform for ordinary users



QTBS focuses heavily on:



\- Transparency

\- Explainability

\- Verification

\- Visualization

\- AI-assisted auditing



\---



\# Philosophy



QTBS does not simply output backtest results.



It also attempts to answer:



\- Why was a position opened?

\- Why was a position closed?

\- Did the AI truly understand the user’s intent?

\- Does the generated strategy actually match the description?



The project emphasizes:



> “Determinism and transparency in AI-generated trading systems.”



\---



\# License



MIT License



\---



\# Disclaimer



This project is for research and educational purposes only.



QTBS does not provide financial advice or investment guarantees.



All trading strategies involve risk.

