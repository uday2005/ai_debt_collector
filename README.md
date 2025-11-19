# Agentic AI Trainer

## Overview

**The Agentic AI Trainer** is an intelligent, automated system,
which is used by **Debt Collection Agents**, employed in **financial instituitions**.
By leveraging the power of **LLMs**, this tool provides a conversational simulation
for Collection Agents to pratice and improve their compliance skills
before they have their conversations with real borrowers.

## Table of Contents

- [Features](#features)
- [Performance Optimizations](#performance-optimizations)
- [Technologies Used](#technologies-used)
- [Setup and Installation](#setup-and-installation)
- [Usage](#usage)
- [Agent Design](#agent-design)
- [Limitations](#limitations)
- [Product Roadmap](#product-roadmap)

## Features

- **Borrower Simulator:**
- **Web-Based Interface:**
- **Compliance reviewer:**
- **Feedback:**

## Performance Optimizations

This application has been optimized for production use with significant performance improvements:

- **ML Model Caching**: 10-100x faster feedback generation
- **HTML Caching**: 5-10x faster page loading
- **LRU Query Cache**: Up to 1000x faster compliance checks (cache hits)
- **In-Memory Processing**: 2-3x faster TTS generation
- **Optimized Encoding**: 2-5x faster audio processing

See [PERFORMANCE_IMPROVEMENTS.md](PERFORMANCE_IMPROVEMENTS.md) for detailed technical documentation and [OPTIMIZATION_SUMMARY.md](OPTIMIZATION_SUMMARY.md) for an executive summary.

## Technologies Used

- **AI:** LangGraph, Ollama
- **Backend:** python
- **Frontend:**

## Setup and Installation

> Note: Ollama installation is required.

1. Clone the repository:

   ```bash
   git clone https://github.com/uday2005/ai_debt_collector.git
   cd ai_debt_collector
   ```

2. Create and activate a virtual environment:

   - For Linux and macOS:

   ```bash
   python3 -m venv ai-agent
   source ai-agent/bin/activate
   ```

   - for Windows:

   ```powershell
   python -m venv ai-agent
   .\ai-agent\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Configure Environment Variables:

   Get your keys from [Deepgram](deepgram.com)

   ```
   DEEPGRAM_API_KEY="YOUR_API_KEY"
   ```

5. Piper Voice setup:
   Download a piper voice

   ```bash
   python3 -m piper.download_voices en_US-lessac-medium
   ```

   Update your piper voice path in `tools/tts_module.py`

   ```python
    voice = PiperVoice.load("/path/to/en_US-lessac-medium.onnx")
   ```

6. Run the application:

   ```python
   python3 web_app.py
   ```

## Usage

After starting the web application,
open your browser and navigate to the provided URL.
The interface will allow you to interact with the AI agent
to initiate and manage your debt collection training.

## Agent Design

## Limitations

## Product Roadmap
