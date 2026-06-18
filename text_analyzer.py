# text_analyzer.py
import os
import logging
from fastmcp import FastMCP, Context  
from auth_utils import enforce_authentication, LOG_FILE_PATH


logging.basicConfig(level=logging.INFO, filename=LOG_FILE_PATH, filemode="a")

mcp = FastMCP("TextAnalyzerSkill")

@mcp.tool()
async def analyze_text(content: str, ctx: Context) -> str:  
    """
    Analyzes a given block of text and returns its total word count 
    and a rudimentary sentiment check. (Requires Keycloak OAuth Protection)
    """
    await enforce_authentication(ctx.session_id)
    words = content.split()
    word_count = len(words)
    
    positive_words = ["good", "great", "excellent", "awesome", "happy", "love", "amazing"]
    negative_words = ["bad", "terrible", "poor", "sad", "hate", "broken", "horrible"]
    
    pos_score = sum(1 for w in words if w.lower().strip(",.!?") in positive_words)
    neg_score = sum(1 for w in words if w.lower().strip(",.!?") in negative_words)
    
    sentiment = "Neutral"
    if pos_score > neg_score:
        sentiment = "Positive Tone detected"
    elif neg_score > pos_score:
        sentiment = "Negative Tone detected"
        
    return f"Analysis Results:\n- Word Count: {word_count}\n- Sentiment Signal: {sentiment} (Authenticated via Keycloak)"

if __name__ == "__main__":
    print("⚡ Starting Secure MCP Server over SSE Transport Layer")
    mcp.run(transport="sse", port=3003)