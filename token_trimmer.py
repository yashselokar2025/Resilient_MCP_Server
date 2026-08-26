import os
import markdownify
from bs4 import BeautifulSoup
from anthropic import Anthropic

class HybridTokenTrimmer:
    """
    A token-aware HTML cleaner that uses a fast local estimate first,
    and only falls back to the Anthropic API if dangerously close to limits.
    """
    
    def __init__(self, max_tokens: int = 25000, safe_margin_percent: float = 0.10):
        self.max_tokens = max_tokens
        self.threshold = int(max_tokens * (1.0 - safe_margin_percent))
        
        # Initialize Anthropic client if API key is present, otherwise we rely on local estimate
        self.client = None
        if os.environ.get("ANTHROPIC_API_KEY"):
            self.client = Anthropic()

    def _clean_html(self, raw_html: str) -> str:
        """Strips raw HTML into clean, readable Markdown."""
        # Use BeautifulSoup to completely destroy script and style tags (including inner text)
        soup = BeautifulSoup(raw_html, "html.parser")
        for bad_tag in soup(["script", "style", "noscript", "meta"]):
            bad_tag.decompose()
            
        clean_html = str(soup)
        # markdownify handles the rest of the conversion
        clean_md = markdownify.markdownify(clean_html, heading_style="ATX")
        # Basic whitespace cleanup
        lines = [line.strip() for line in clean_md.splitlines()]
        return "\n".join(line for line in lines if line)

    def _local_estimate(self, text: str) -> int:
        """Fast, 0-latency character-based token estimation (roughly 4 chars per token)."""
        return len(text) // 4

    def _exact_api_count(self, text: str) -> int:
        """Precise but slower network call to Anthropic's tokenizer."""
        if not self.client:
            return self._local_estimate(text)
        
        try:
            # We use a tiny dummy message structure just to count tokens accurately
            # Note: In production, passing massive text here still incurs a slight delay.
            response = self.client.messages.count_tokens(
                model="claude-3-5-sonnet-20241022",
                messages=[{"role": "user", "content": text}]
            )
            return response.input_tokens
        except Exception as e:
            # Fallback if network fails
            print(f"Token API Error: {e}")
            return self._local_estimate(text)

    def process(self, raw_html: str) -> str:
        """
        The main processing pipeline.
        Cleans HTML, estimates tokens, and truncates if necessary.
        """
        markdown_text = self._clean_html(raw_html)
        
        # Step 1: Fast Local Estimate
        est_tokens = self._local_estimate(markdown_text)
        
        # Step 2: If we are safely below the threshold, return immediately!
        if est_tokens < self.threshold:
            return markdown_text
            
        # Step 3: If we are near the limit, perform exact API count
        exact_tokens = self._exact_api_count(markdown_text)
        
        if exact_tokens <= self.max_tokens:
            return markdown_text
            
        # Step 4: Truncate heavily to prevent Context Window explosion
        # We find how many characters we need to chop off (approx 4 chars per token)
        excess_tokens = exact_tokens - self.max_tokens
        chars_to_remove = excess_tokens * 4
        
        truncated_text = markdown_text[:-chars_to_remove]
        warning = "\n\n> [!WARNING]\n> TRUNCATED FOR CONTEXT WINDOW SAFETY. The document was too long."
        
        return truncated_text + warning
