from typing import List
import re
from client.openai_client import client

def generate_smart_keywords(topic: str, script: str) -> List[str]:
    prompt = f"""
    Analyze this YouTube video topic and script to generate the BEST 15 stock footage search keywords.

    Topic: "{topic}"
    Script Excerpt: "{script[:500]}"

    Instructions:
    1.  Focus on tangible objects, actions, scenes, and visual metaphors.
    2.  Keywords should be descriptive and specific (2-3 words is ideal).
    3.  AVOID abstract concepts like 'moment', 'situation', 'common', 'tricks', or 'reason'.
    4.  Include a mix of scientific and conceptual terms.
    
    Example:
    - Good: "scientist looking at brain scan", "glowing neural network", "blurry memory effect"
    - Bad: "experience", "feeling", "concept"

    Return ONLY a comma-separated list of keywords.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=150
        )
        text = (response.choices[0].message.content or "").strip()
        keywords = text.split(',')
        return [k.strip() for k in keywords][:15]
    except:
        return extract_keywords_fallback(topic, script)

def extract_keywords_fallback(topic: str, script: str) -> List[str]:
    keywords = []
    topic_words = re.findall(r'\b\w{4,}\b', topic.lower())
    keywords.extend(topic_words[:5])
    keywords.extend(["4k footage", "cinematic", "stock video", "high quality"])
    return keywords[:15]