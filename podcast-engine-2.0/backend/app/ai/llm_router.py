import os
import json
import logging
from litellm import completion

logging.basicConfig(level=logging.INFO)

class PodcastCuratorLLM:
    def __init__(self, use_local=False, model_name=None):
        """
        Initializes the LLM router using LiteLLM.
        Supports seamless switching between Claude/OpenAI and Local Ollama models.
        """
        self.use_local = use_local
        
        # Determine the model routing
        if self.use_local:
            # Assumes Ollama is running locally on default port
            self.model = model_name or "ollama/llama3"
            logging.info(f"Initialized Local LLM Engine using: {self.model}")
        else:
            self.model = model_name or "anthropic/claude-3-haiku-20240307"
            # LiteLLM automatically picks up ANTHROPIC_API_KEY from environment
            logging.info(f"Initialized Cloud LLM Engine using: {self.model}")

    def analyze_chunk(self, transcript_chunk, known_concepts_summary=""):
        """
        Sends a chunk of a podcast transcript to the LLM to extract dense knowledge.
        """
        prompt = f"""You are an elite podcast editor and curator.
Your task is to analyze the following podcast transcript chunk and decide which timestamps contain highly dense, valuable knowledge. 
You must filter out:
1. Ads and sponsor reads.
2. Filler conversation, small talk, and generic banter.
3. Repetitive fluff that takes too long to get to the point.
4. Concepts the user already knows well.

User's Known Concepts:
{known_concepts_summary}

Transcript Chunk (JSON with word/sentence timestamps):
{transcript_chunk}

Output a clean JSON list of segment objects to KEEP. Each object must have:
- "start": start time in seconds (float)
- "end": end time in seconds (float)
- "reasoning": a brief 1-sentence explanation of why this is valuable new knowledge.

Do NOT output anything other than valid JSON. If the entire chunk is useless, output an empty list `[]`.
"""
        messages = [{"role": "user", "content": prompt}]
        
        try:
            logging.info(f"Sending chunk to {self.model} for analysis...")
            
            # LiteLLM abstracts the API differences
            response = completion(
                model=self.model,
                messages=messages,
                temperature=0.1,
                max_tokens=2048
            )
            
            content = response.choices[0].message.content
            
            # Basic cleanup for markdown code blocks
            if content.startswith("```json"):
                content = content[7:-3].strip()
            elif content.startswith("```"):
                content = content[3:-3].strip()
                
            return json.loads(content)
            
        except Exception as e:
            logging.error(f"Error during LLM analysis: {e}")
            return []

if __name__ == "__main__":
    # Test stub
    print("LiteLLM router module loaded.")
