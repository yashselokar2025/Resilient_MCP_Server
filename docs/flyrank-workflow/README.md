# FlyRank Repeatable AI Workflow

## 1. Objective
Performing deep technical research across multiple complex websites is extremely time-consuming. Doing it manually involves battling anti-bot protections, scrolling through bloated DOMs to find the actual content, synthesizing the findings, and structuring a final report. This workflow solves this by providing a repeatable, 5-step AI-driven pipeline that automates the gathering, extraction, synthesis, drafting, and review of research topics. By making this repeatable, we dramatically reduce time-to-insight while maintaining human oversight at the critical final review stage.

## 2. Relationship to Resilient MCP Server
The existing **Resilient MCP Server** provides the core technical infrastructure (browser automation, token management, stealth bypassing) required to make this workflow possible. 

This project was initially built to solve systemic failures in agentic browser automation (token explosion, shadow DOM blindness, anti-bot blocking, and concurrency crashes). **This FlyRank assignment applies that existing infrastructure to a defined, repeatable research pipeline.** The MCP server handles the difficult execution of Steps 1 and 2 (Gather & Extract), while the LLM client (e.g., Claude Desktop) executes Steps 3-5 (Synthesize, Draft, Review) utilizing the gathered data.

## 3. Workflow Diagram
```mermaid
flowchart TD
    A[Research Topic Input] --> B[Step 1: Gather Sources]
    B --> C[Step 2: Extract Key Information]
    C --> D[Step 3: Synthesize Findings]
    D --> E[Step 4: Draft Research Brief]
    E --> F[Step 5: Review and Verify]
    F --> G[Human Review & Final Output]
    
    subgraph Resilient MCP Server
        B
        C
    end
    
    subgraph LLM Client (Claude)
        D
        E
        F
    end
```

## 4. Step-by-Step Workflow

### Step 1 — Gather
* **Purpose:** Collect relevant URLs and navigate to the target data sources.
* **Input:** A research topic or specific target URL.
* **Tool/Action:** Claude uses the MCP server's `navigate` tool.
* **Prompt/Configuration:** *See PROMPTS.md -> Gather Prompt*
* **Output:** The raw, token-trimmed DOM of the target page.
* **Handoff:** The LLM evaluates the raw DOM to determine what specific data needs extraction.
* **Possible Failure Modes:** Cloudflare block (mitigated by stealth), navigation timeout.

### Step 2 — Extract
* **Purpose:** Pull structured facts, concepts, and evidence from the bloated web page.
* **Input:** The loaded web page context.
* **Tool/Action:** Claude uses the MCP server's `extract` tool (or natively parses the trimmed DOM).
* **Prompt/Configuration:** *See PROMPTS.md -> Extraction Prompt*
* **Output:** A structured list of facts and evidence.
* **Handoff:** The structured facts are passed to the synthesis engine.
* **Possible Failure Modes:** Data hidden in deep Shadow DOMs (mitigated by custom JS piercer), incomplete extraction due to token limits (mitigated by HybridTokenTrimmer).

### Step 3 — Synthesize
* **Purpose:** Combine and organize the gathered facts from one or multiple sources into a coherent understanding.
* **Input:** Extracted facts and evidence.
* **Tool/Action:** LLM internal reasoning.
* **Prompt/Configuration:** *See PROMPTS.md -> Synthesis Prompt*
* **Output:** A logical outline of the findings.
* **Handoff:** Outline is passed to the drafting step.
* **Possible Failure Modes:** Hallucination of connections between unrelated facts, loss of source attribution.

### Step 4 — Draft
* **Purpose:** Generate a structured, highly readable research brief.
* **Input:** Synthesized outline.
* **Tool/Action:** LLM generation.
* **Prompt/Configuration:** *See PROMPTS.md -> Draft Prompt*
* **Output:** A complete Markdown research brief.
* **Handoff:** Draft is passed to the AI review step before final human review.
* **Possible Failure Modes:** Formatting errors, failure to adhere to the requested schema.

### Step 5 — Review
* **Purpose:** Check factual support, identify missing context, and flag unsupported claims.
* **Input:** Drafted research brief.
* **Tool/Action:** LLM verification pass.
* **Prompt/Configuration:** *See PROMPTS.md -> Review Prompt*
* **Output:** A list of warnings, caveats, and confidence scores appended to the brief.
* **Handoff:** Handed off to the human user for final approval.
* **Possible Failure Modes:** AI failing to catch its own hallucinations (confirmation bias).

## 5. Prompts and Configurations
All workflow instructions and prompts required to reproduce this pipeline are documented in `PROMPTS.md`. 
To run this pipeline, you provide the Master System Prompt to Claude Desktop (or equivalent LLM client), which configures it to execute the 5-step sequence using the connected MCP server.

## 6. Five Real Runs
*Currently Marked as Pending Execution.*
Because this workflow relies on your specific Claude Desktop configuration and local environment variables, the runs must be executed by you. Please refer to `TEST_RUNS.md` for the exact template and instructions on how to execute and record the 5 real runs.

## 7. Manual vs Workflow Time Comparison
*(Estimates based on typical research tasks; update with real data after executing the 5 runs)*

| Activity | Manual Time (Estimated) | Workflow Time (Estimated) |
|----------|------------------------|---------------------------|
| Research/source gathering | 15 mins | 1 min (MCP Navigation) |
| Information extraction | 20 mins | 2 mins (LLM Parsing) |
| Synthesis | 15 mins | 1 min (LLM Reasoning) |
| Drafting | 30 mins | 1 min (LLM Generation) |
| Review | 10 mins | 5 mins (Human + AI Review) |
| **Total per run** | **90 mins** | **10 mins** |

**One-Time Setup Costs:**
* Initial setup/build time (MCP Server): ~4 hours (already completed)
* Configuration time (Claude Desktop): ~10 mins
* Testing time: ~30 mins

## 8. Failure Points
* **Anti-Bot Challenge Escalation:** While the server uses `playwright-stealth v2.x` to bypass mid-tier Cloudflare, extremely strict Turnstile challenges might still block the browser.
* **Token/Context Limitations:** If extracting from a massive Wikipedia page, the LLM might lose the thread or the `HybridTokenTrimmer` might aggressively truncate vital information near the bottom of the page.
* **Concurrency Issues:** If the LLM fires multiple tool calls in rapid succession, they are queued by the `asyncio.Lock()`. If the queue gets too long, the LLM client might time out waiting for a response.
* **Hallucinated/Unsupported Claims:** During the synthesis phase, the LLM might hallucinate connections between extracted facts that don't actually exist in the source material.

## 9. Human Review
The AI workflow should **NOT** be trusted to finalize the following automatically:
* **Source Credibility:** The AI cannot reliably judge if the scraped website is a trustworthy source of truth.
* **Critical Numerical Data:** Financial figures, dates, and statistics must be spot-checked against the raw source.
* **Conclusions & Strategic Decisions:** The AI can summarize the data, but the human must verify the final strategic conclusion.

## 10. Resilience Features
The existing MCP server provides the following resilience mechanisms to ensure the workflow doesn't crash mid-execution:
* **Browser Session Handling:** A `PersistentBrowserManager` maintains a Singleton Playwright context, allowing multi-step workflows without cold-starting the browser.
* **Token Estimation/Context Safety:** The `HybridTokenTrimmer` uses local estimation (`len // 4`) to prevent the LLM context window from crashing when parsing massive DOMs.
* **Asyncio Lock/Concurrency Control:** Strict `asyncio.Lock()` implementation ensures that parallel tool calls from the LLM do not crash Playwright with "Navigation already in progress" errors.
* **Shadow DOM Piercing:** Custom JS recursively extracts text from isolated Web Components that standard scrapers miss.

## 11. Reproducibility
To run this workflow yourself:
1. Ensure you have Python 3.10+ and Node.js installed.
2. Clone this repository and install dependencies (`pip install -r requirements.txt`).
3. Install Playwright browsers (`playwright install chromium`).
4. Configure Claude Desktop to use this FastMCP server by adding it to your `claude_desktop_config.json`:
   ```json
   "mcpServers": {
     "resilient_research": {
       "command": "python",
       "args": ["/absolute/path/to/server.py"]
     }
   }
   ```
5. Restart Claude Desktop.
6. Paste the **Master Workflow Prompt** (from `PROMPTS.md`) into Claude and provide your research topic.

## 12. Evaluation Criteria Mapping

| FlyRank Requirement | Evidence |
|---------------------|----------|
| End-to-end workflow | See step-by-step documentation in this README and execution prompts in `PROMPTS.md`. |
| 3+ distinct steps | Implemented 5 steps: Gather, Extract, Synthesize, Draft, Review. |
| Defined handoffs | Handoffs explicitly documented in Section 4. |
| Five real runs | Setup instructions provided; data to be logged in `TEST_RUNS.md`. |
| Honest time accounting | Table provided in Section 7 (to be updated with actual test metrics). |
| Failure points | Documented in Section 8 based on actual architecture limitations. |
| Human review | Documented in Section 9. |

## 13. Conclusion
This workflow demonstrates how a highly resilient, low-level browser automation tool (the MCP server) can be paired with high-level cognitive automation (Claude Desktop) to create a repeatable research pipeline. While the workflow dramatically reduces the time spent on manual scraping and drafting, it relies heavily on the human-in-the-loop for the final factual verification. The primary limitation currently is the hard context window limit of the LLM, which necessitates our aggressive token-trimming infrastructure.
