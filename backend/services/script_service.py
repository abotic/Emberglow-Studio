import re
from typing import Dict

from client.openai_client import client

from config import MAX_SCRIPT_RETRIES
from core.models import VideoSettings, ScriptGenerationError

def generate_script(video_type: str, category: str, topic: str, video_settings: VideoSettings) -> str:
    print(f"Generating {video_type} script for: {topic}")

    country_match = re.search(r'what does ai think about ([\w\s]+)\??$', topic, re.IGNORECASE)
    if country_match and category == 'custom':
        return _generate_country_script(country_match.group(1).title(), topic, video_settings)
    
    return _generate_standard_script(video_type, category, topic, video_settings)

def _generate_country_script(country_name: str, topic: str, video_settings: VideoSettings) -> str:
    prompt = f"""
You are a helpful and insightful AI narrator for a YouTube video. Your task is to generate a script for the topic: "{topic}".

IMPORTANT: Adopt a first-person AI persona. Use phrases like "As an AI, my analysis shows...", "From my perspective...", or "To an AI like me...". You are speaking directly about the country. Do NOT explain what artificial intelligence is or how you process data.

The script MUST be structured as follows, with clear paragraphs for each section:
1.  **Introduction:** Start with a powerful hook. Announce that you, an AI, will share your unique, data-driven perspective on {country_name}.
2.  **The Bright Side (Positive Analysis):** Discuss 2-3 specific, positive aspects. Mention its culture, natural beauty, innovations, or famous contributions. Be specific and give examples.
3.  **The Complexities (Challenges & Concerns):** Discuss 2-3 specific challenges or concerns for {country_name}. This could be economic, social, or environmental issues. Present this in a balanced, objective, and neutral tone.
4.  **Hidden Gems (What Makes It Unique):** Share 2-3 fascinating, lesser-known facts, places, or cultural quirks that make {country_name} stand out from a data perspective.
5.  **Conclusion:** Briefly summarize your "thoughts," emphasizing the country's unique character and complexity. End with a memorable, thought-provoking statement and a call-to-action for viewers to share their own experiences in the comments.

CRITICAL INSTRUCTIONS:
- The total script length must be between {video_settings.word_count_min} and {video_settings.word_count_max} words.
- The tone must be conversational, engaging, and slightly awe-inspired, not robotic.
- Write ONLY the spoken narration. Do NOT include visual directions, scene headings (like "Introduction:"), brackets like [intro music], or camera instructions.
"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1500
        )
        script = response.choices[0].message.content.strip()
        return clean_script_for_voice(script)
    except Exception as e:
        raise ScriptGenerationError(f"Country-specific script generation failed: {e}")

def _generate_standard_script(video_type: str, category: str, topic: str, video_settings: VideoSettings) -> str:
    if video_type == "shorts":
        max_tokens = 200
        prompt = f"""
Write a YouTube Shorts script about: "{topic}"

IMPORTANT: Write EXACTLY {video_settings.word_count_min}-{video_settings.word_count_max} words.

Requirements:
- Hook viewers in first 3 seconds
- Ultra-concise, punchy sentences
- One surprising fact or revelation
- Call-to-action at the end
- Designed for vertical viewing
- High energy throughout

Write ONLY spoken narration. NO visual directions.
"""
    else:
        max_tokens = 1000
        if category == "why" or category == "custom":
            prompt_style = "scientific explanation with surprising facts"
        elif category == "what_if":
            prompt_style = "imaginative exploration of hypothetical scenarios"
        else:
            prompt_style = "revealing investigation into hidden systems and psychology"
        
        prompt = f"""
Write a YouTube video script about: "{topic}"

Style: {prompt_style}

IMPORTANT: Write EXACTLY {video_settings.word_count_min}-{video_settings.word_count_max} words.

Requirements:
- ELI5 tone - simple, clear, engaging
- Start with powerful hook in first sentence
- Break into 5-6 clear paragraphs
- End with memorable conclusion and call-to-action
- Curiosity-driven and educational
- Use "you" to address viewer directly

Write ONLY spoken narration. NO visual directions, NO brackets, NO camera instructions.
Just pure narration text.
"""
    
    for attempt in range(MAX_SCRIPT_RETRIES):
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=max_tokens
            )
            script = response.choices[0].message.content.strip()
            return clean_script_for_voice(script)
        except Exception as e:
            if attempt == MAX_SCRIPT_RETRIES - 1:
                raise ScriptGenerationError(f"Script generation failed after {MAX_SCRIPT_RETRIES} attempts: {e}")

def generate_youtube_metadata(topic: str, script: str, video_type: str) -> Dict:
    prompt = f"""
You are an expert in writing viral YouTube video metadata.
Your task is to generate three components for a video with the topic: "{topic}".
Provide the output in three distinct parts, separated only by "---".
IMPORTANT: Do NOT write "PART 1:", "PART 2:", or any similar headers in your response.

The first part is the video title (max 100 characters).
---
The second part is the engaging video description (2-4 sentences, with emojis, NO "subscribe" or "like" calls-to-action).
---
The third part is a comma-separated list of 10-15 relevant keywords/tags (do NOT include the '#' symbol).
"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        content = response.choices[0].message.content.strip()
        parts = content.split('---')

        if len(parts) == 3:
            title = re.sub(r'^\s*PART\s*\d:\s*', '', parts[0], flags=re.IGNORECASE).strip()
            desc_text = re.sub(r'^\s*PART\s*\d:\s*', '', parts[1], flags=re.IGNORECASE).strip()
            tags_list_str = re.sub(r'^\s*PART\s*\d:\s*', '', parts[2], flags=re.IGNORECASE).strip()
            
            if not title or not desc_text or not tags_list_str:
                raise ValueError("AI response contained empty parts")

            tags = [tag.strip() for tag in tags_list_str.split(',') if tag.strip()]
            hashtags = ' '.join([f"#{tag.replace(' ', '')}" for tag in tags])
            final_description = f"{desc_text}\n\n{hashtags}"

            return {
                "title": title,
                "description": final_description,
                "tags": tags,
                "video_type": video_type
            }
        else:
            raise ValueError("AI response did not follow expected format")

    except Exception as e:
        print(f"Primary metadata generation failed: {e}, using fallback")
        return _generate_metadata_fallback(topic, script, video_type)

def _generate_metadata_fallback(topic: str, script: str, video_type: str) -> Dict:
    return {
        "title": topic[:100],
        "description": script[:400],
        "tags": [word for word in topic.lower().split() if len(word) > 3][:15],
        "video_type": video_type
    }

def clean_script_for_voice(script: str) -> str:
    script = re.sub(r'\[.*?\]|\(.*?\)|<.*?>', '', script)
    script = re.sub(r'(Part \d+:|Section \d+:|Chapter \d+:|Scene \d+:)', '', script, flags=re.IGNORECASE)
    script = re.sub(r'\*\*|\*', '', script)
    script = re.sub(r'(Cut to:|Shot of:|Visual:|Image:|Video:|Audio:)', '', script, flags=re.IGNORECASE)
    return script.strip()