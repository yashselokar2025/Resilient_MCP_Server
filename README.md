# Resilient Research MCP Server

> ⚠️ **PROPRIETARY & CONFIDENTIAL**  
> This repository contains proprietary portfolio work. All rights reserved. **Copying, forking, redistributing, or using this code for any open-source, commercial, or personal projects without explicit written permission is strictly prohibited.**

> **"An advanced, production-grade Model Context Protocol (MCP) server that equips AI Agents with a highly resilient, stealth-capable, and context-aware web browsing engine. Engineered specifically to overcome the fatal limitations of standard AI browser automation, this proprietary system enables seamless multi-step workflows, extracts deep structural data, and guarantees context window safety across the most complex web environments."**

## Key Advantages & Capabilities

Standard AI browser automation scripts consistently fail in production environments due to bot-blocking, data obfuscation, and context window crashing. This proprietary architecture was built from the ground up to guarantee resilient agentic operation.

### 1. Zero-Crash Token Safety
Dumping raw web data into an LLM will instantly crash its context window. 
* **The Advantage:** Features a custom-built Hybrid Token Engine that performs instantaneous, zero-latency character-to-token limit checks. When navigating massive pages, the system intelligently strips non-semantic code and automatically truncates data right before the boundary limit, guaranteeing the AI never crashes.

### 2. Deep Shadow DOM Penetration
Modern web applications hide their most valuable data inside isolated, closed components that standard scraping engines cannot see.
* **The Advantage:** Utilizes a highly specialized, proprietary DOM-piercing injection module. The engine recursively crawls through isolated web components, forcibly extracting hidden datasets and surfacing them into the light DOM for the AI to parse. 

### 3. Advanced Anti-Bot Masking
Standard headless browsers are immediately detected and blocked by modern security firewalls like Cloudflare or DataDome.
* **The Advantage:** Implements deeply integrated browser fingerprint masking. The engine systematically alters its JS footprint and network signatures to effortlessly bypass mid-tier JavaScript bot challenges and access protected endpoints.

### 4. Persistent Multi-Step Sessions
Basic automation tools spin up a completely fresh, amnesiac browser for every single command, making it impossible to perform sequential tasks (like logging in, then clicking a button).
* **The Advantage:** Built around a custom Singleton state manager. The engine maintains a continuous, persistent browser session across multiple AI tool calls. The AI can navigate, scroll, extract, and interact sequentially within the exact same window.

### 5. Highly Concurrent Execution Queue
When AI agents attempt to execute multiple browser actions in parallel, standard engines crash with fatal race conditions.
* **The Advantage:** Features a strict, thread-safe asynchronous locking architecture. When the AI rapidly fires multiple concurrent commands, the engine intelligently queues and strictly serializes them, guaranteeing perfectly stable execution even under heavy parallel load.

## Running the Verification Tests

This project includes 4 hardened verification scripts that prove the architecture's resilience under extreme stress:

* `python test_stealth.py` - Proves the fingerprint masking engine successfully bypasses live Cloudflare protection.
* `python test_shadow_dom.py` - Proves the recursive DOM-piercing module successfully extracts deeply hidden closed-component text.
* `python test_token_overflow.py` - Proves the Hybrid Token Engine safely truncates massively bloated datasets (e.g., world-record Wikipedia pages) without data loss.
* `python test_concurrency.py` - Stress-tests the asynchronous execution lock by safely queueing simultaneous parallel commands without engine failure.
