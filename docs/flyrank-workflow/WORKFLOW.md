# Technical Workflow Specification

## Objective
To automate the end-to-end research process by utilizing a resilient MCP-backed browser to scrape targeted web data, and an LLM to synthesize that data into a structured, human-verifiable research brief.

## Core Components
1. **Execution Environment:** Claude Desktop (or any MCP-compatible LLM client).
2. **Automation Engine:** Resilient MCP Server (FastMCP, Playwright, asyncio).

## Input Schema
The workflow is triggered by the user providing a topic and an optional list of target URLs.
```json
{
  "topic": "String (e.g., 'Recent advancements in solid-state batteries')",
  "target_urls": ["Array of Strings (Optional)"],
  "focus_areas": ["Array of Strings (Optional)"]
}
```

## Output Schema
The final output is a Markdown-formatted research brief containing:
1. Executive Summary
2. Key Findings (with source attribution)
3. Synthesized Analysis
4. AI Review & Caveats (Confidence score and flagged unverified claims)

## Stages & Dependencies

| Stage | Action | Tool Dependency | Handoff |
|-------|--------|-----------------|---------|
| **1. Gather** | Navigate to URLs / Search | MCP `navigate` tool | Raw trimmed DOM |
| **2. Extract** | Pull specific facts based on focus areas | MCP `extract` tool / LLM parsing | Structured JSON/Markdown facts |
| **3. Synthesize** | Cross-reference facts and build outline | LLM Reasoning | Logical outline |
| **4. Draft** | Generate the research brief | LLM Generation | Markdown Draft |
| **5. Review** | Audit the draft against extracted facts | LLM Reasoning | Final Output with Caveats |

## Error Handling
* **Navigation Failures:** If `navigate` fails due to timeouts or bot-blocks, the LLM is instructed to notify the user and attempt an alternative URL.
* **Context Overflow:** The MCP server's `HybridTokenTrimmer` automatically strips non-semantic nodes and truncates content to prevent the LLM from crashing during the Gather stage.
* **Concurrency Crashes:** Handled server-side via `asyncio.Lock()` to queue parallel tool calls automatically.

## Human Review Points
The workflow explicitly pauses at the end of Stage 5. The human must:
1. Review the generated "AI Review & Caveats" section.
2. Manually verify any statistics or hard numbers cited in the "Key Findings" against the original URLs.
