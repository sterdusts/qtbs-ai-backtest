English // 中文 // 한국어 =

===========================



English Version

QTBS AI Quant Strategy Frontend

Project Introduction

QTBS AI Quant Strategy Frontend is a natural-language-based quantitative strategy backtesting platform powered by large language models.



Users do not need to write code. By simply describing a strategy in natural language, the system can:



Automatically generate quantitative strategy code



Run historical backtests



Generate K-line and equity curve visualizations



Analyze whether the generated strategy correctly matches the user’s description



The goal of QTBS is to reduce the technical barrier of quantitative strategy validation and improve transparency and interpretability in AI-generated trading strategies.



Project Background

The internet contains a huge number of:



“High win-rate strategies”



“Profitable trading systems”



“Quant tutorials”



“Indicator combinations”



However, most ordinary users:



Cannot verify whether a strategy is truly effective



Do not know Python or quantitative frameworks



Cannot build backtesting environments



Cannot determine whether AI-generated code is logically correct



As a result, strategy verification remains difficult and expensive.



QTBS attempts to solve this problem through AI-assisted strategy generation and visualized backtesting.



Core Features

Natural Language → Strategy Code

Users can input strategies such as:



“Go long when EMA12 crosses above EMA26, close the position on a dead cross.”



The system automatically generates executable Python strategy functions.



AI Strategy Review

The system automatically analyzes:



Whether the generated strategy matches the user’s description



Whether future data leakage exists



Whether unnecessary logic has been added



Potential trading risks



And generates:



Match score



Risk explanation



Strategy implementation notes



Visualized Backtesting

The platform automatically generates:



Candlestick charts



Entry/exit markers



Floating equity curves



Realized equity curves



Volume charts



This allows users to visually verify trading behavior and strategy execution logic.



Multi-language Support

Currently supported languages:



Chinese



English



Korean



Japanese



Russian



Arabic



Technical Stack

Frontend

Gradio



HTML / CSS / JavaScript



AI System

DeepSeek API



Natural language strategy parsing



AI strategy auditing



Backtesting Engine

Python



Pandas



NumPy



Visualization

Pyecharts



Apache ECharts



Project Characteristics

Emphasis on Transparency

QTBS focuses not only on generating strategy code, but also on:



Verifiability



Explainability



Visualization



Strategy auditing



Designed for Ordinary Users

Users do not need to:



Learn Python



Build quantitative infrastructures



Write backtesting engines



to perform basic strategy validation.



AI + Explainable Quantitative Analysis

QTBS does not simply output results.



It also attempts to explain:



Why positions are opened



Why positions are closed



Whether the AI truly understood the user’s intent



Current Status

The current version already supports:



Natural-language strategy generation



Historical backtesting



Visualized chart systems



AI strategy match analysis



Multi-language UI support



Future plans include:



Advanced position management systems



Multi-strategy portfolios



AI-driven strategy optimization



Risk analysis modules



Local model deployment



Project Positioning

QTBS is not intended to compete with institutional-grade quantitative trading platforms.



Instead, it is currently positioned as:



An AI-assisted strategy verification tool



A learning and educational platform



A lightweight quant platform for ordinary users



The core mission of QTBS is:



To reduce the barrier of quantitative strategy validation and improve transparency in AI-generated trading systems.

===========================================================================================================================

中文

1\. 项目简介



QTBS AI Quant Strategy Frontend 是一个基于大语言模型的自然语言量化策略回测平台。



用户无需编写代码，只需输入自然语言描述，即可：



自动生成量化策略代码

自动运行历史回测

自动生成 K 线与权益曲线图

自动分析策略实现与用户描述的一致程度



项目目标是降低量化回测门槛，提高策略验证的透明度与可解释性。



2\. 项目背景



当前互联网上存在大量：



“稳赚策略”

“高胜率系统”

“量化教学”

“指标组合”



但绝大部分普通用户：



无法验证策略真实性

不具备 Python 回测能力

不会搭建量化环境

难以判断 AI 是否正确实现了策略逻辑



因此：



策略验证的成本非常高。



QTBS 希望通过 AI 与可视化回测，降低用户的验证门槛。



3\. 核心功能

自然语言生成策略代码



用户输入：



EMA12 上穿 EMA26 做多，死叉平仓



系统自动生成：



generate\_signals(df)



策略代码。



AI 策略审查



系统会自动分析：



是否符合用户描述

是否存在未来函数

是否存在额外逻辑

是否存在潜在风险



并生成：



匹配度

风险说明

策略解释

可视化回测系统



系统自动生成：



K 线图

开仓平仓点

实时权益曲线

已实现权益曲线

成交量



帮助用户直观验证策略行为。



多语言支持



当前支持：



中文

English

한국어

日本語

Русский

العربية

4\. 技术架构

前端

Gradio

HTML/CSS/JavaScript

AI

DeepSeek API

自然语言策略解析

AI 策略审查

回测核心

Python

Pandas

NumPy

图表系统

Pyecharts

ECharts

5\. 项目特点

强调“确定性”



QTBS 不仅生成代码，更强调：



可验证

可解释

可视化

可审查

面向普通用户



用户无需：



学习 Python

搭建回测框架

编写策略引擎



即可完成基础策略验证。



AI + 可解释回测



不仅输出结果，还尝试解释：



为什么这样开仓

为什么这样平仓

AI 是否正确理解了用户需求

6\. 当前阶段



当前版本已实现：



自然语言生成策略代码

历史回测

图表可视化

AI 匹配度分析

多语言支持



后续计划：



更复杂仓位系统

多策略组合

AI 自动优化策略

风险分析模块

本地模型部署

7\. 项目定位



QTBS 并非专业机构级量化平台。



当前更偏向：



AI 辅助策略验证工具

教学与学习工具

面向普通用户的轻量量化平台



核心目标是：



降低量化策略验证门槛，提高策略透明度。



==========================================================================================================================



한국어 버전

QTBS AI Quant Strategy Frontend

프로젝트 소개



QTBS AI Quant Strategy Frontend는 대형 언어 모델(LLM)을 기반으로 한 자연어 양적 전략 백테스트 플랫폼입니다.



사용자는 코드를 직접 작성할 필요 없이 자연어로 전략을 설명하기만 하면 다음 기능을 사용할 수 있습니다.



자동 전략 코드 생성

과거 데이터 기반 백테스트 실행

K선 및 수익 곡선 시각화

생성된 전략이 사용자 설명과 얼마나 일치하는지 자동 분석



QTBS의 목표는 양적 전략 검증의 기술적 진입 장벽을 낮추고, AI 기반 전략 생성의 투명성과 해석 가능성을 높이는 것입니다.



프로젝트 배경



인터넷에는 수많은:



“고승률 전략”

“수익형 시스템”

“퀀트 강의”

“지표 조합”



등이 존재합니다.



하지만 대부분의 일반 사용자는:



전략의 실제 효과를 검증할 수 없고

Python이나 퀀트 프레임워크를 모르며

백테스트 환경을 구축하지 못하고

AI가 생성한 코드가 논리적으로 올바른지 판단하기 어렵습니다.



결과적으로 전략 검증 비용이 매우 높습니다.



QTBS는 AI 기반 전략 생성과 시각화 백테스트를 통해 이 문제를 해결하고자 합니다.



핵심 기능

자연어 → 전략 코드 생성



예시 입력:



“EMA12가 EMA26을 상향 돌파하면 매수하고, 데드크로스 시 청산”



시스템은 자동으로 실행 가능한 Python 전략 함수를 생성합니다.



AI 전략 검토



시스템은 자동으로 다음 내용을 분석합니다.



전략이 사용자 설명과 일치하는지

미래 함수(Future Leakage)가 존재하는지

불필요한 로직이 추가되었는지

잠재적인 리스크가 있는지



그리고 다음 정보를 제공합니다.



전략 일치도

위험 설명

전략 구현 설명

시각화 백테스트 시스템



플랫폼은 자동으로 다음 차트를 생성합니다.



캔들 차트(K-line)

진입 / 청산 포인트

실시간 손익 곡선

실현 손익 곡선

거래량 차트



이를 통해 사용자는 전략 동작을 직관적으로 검증할 수 있습니다.



다국어 지원



현재 지원 언어:



중국어

영어

한국어

일본어

러시아어

아랍어

기술 스택

프론트엔드

Gradio

HTML / CSS / JavaScript

AI 시스템

DeepSeek API

자연어 전략 분석

AI 전략 감사

백테스트 엔진

Python

Pandas

NumPy

시각화 시스템

Pyecharts

Apache ECharts

프로젝트 특징

“투명성” 중심 설계



QTBS는 단순히 전략 코드를 생성하는 것이 아니라:



검증 가능성

설명 가능성

시각화

전략 감사



를 중요하게 생각합니다.



일반 사용자를 위한 설계



사용자는:



Python 학습

퀀트 인프라 구축

백테스트 엔진 개발



없이도 기본적인 전략 검증이 가능합니다.



AI + 설명 가능한 퀀트 분석



QTBS는 단순 결과만 출력하지 않습니다.



또한:



왜 진입했는지

왜 청산했는지

AI가 사용자 의도를 제대로 이해했는지



를 설명하려고 시도합니다.



현재 개발 단계



현재 버전에서는 다음 기능이 구현되었습니다.



자연어 전략 생성

과거 데이터 백테스트

시각화 차트 시스템

AI 전략 일치도 분석

다국어 UI 지원



향후 계획:



고급 포지션 관리 시스템

멀티 전략 포트폴리오

AI 기반 전략 자동 최적화

리스크 분석 모듈

로컬 모델 배포 지원

프로젝트 포지셔닝



QTBS는 기관급 퀀트 플랫폼을 목표로 하지 않습니다.



현재는 다음과 같은 방향에 가깝습니다.



AI 기반 전략 검증 도구

학습 및 교육 플랫폼

일반 사용자를 위한 경량 퀀트 플랫폼



QTBS의 핵심 목표는:



양적 전략 검증의 진입 장벽을 낮추고 AI 전략의 투명성을 높이는 것입니다.

