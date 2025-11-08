import os
import base64
from typing import List, Dict, Optional
from openai import OpenAI


class OpenAIClient:
    """Handle OpenAI API interactions for summarization"""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.model = model or os.getenv('OPENAI_MODEL', 'gpt-4-turbo')
        self.client = OpenAI(api_key=self.api_key)

    def summarize_text(self, text: str, context: str = "") -> Dict:
        """
        Summarize text content
        Returns: {summary, keywords}
        """
        try:
            system_prompt = """You are an expert document analyzer. Your task is to create concise, informative summaries of document sections.

For each section, provide:
1. A clear summary (2-3 paragraphs) capturing the main points
2. Key concepts and keywords (5-10 items)

Focus on:
- Main ideas and arguments
- Important facts and data
- Key conclusions
- Actionable insights"""

            user_prompt = f"""Please summarize the following text.

{f'Context: {context}' if context else ''}

Text to summarize:
{text}

Provide your response in the following format:
SUMMARY:
[Your summary here]

KEYWORDS:
[Comma-separated keywords]"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )

            content = response.choices[0].message.content

            # Parse response
            summary, keywords = self._parse_summary_response(content)

            return {
                'summary': summary,
                'keywords': keywords,
                'tokens_used': response.usage.total_tokens
            }

        except Exception as e:
            raise Exception(f"Error summarizing text: {str(e)}")

    def summarize_with_image(self, text: str, image_bytes: bytes, context: str = "") -> Dict:
        """
        Summarize content with both text and image (for scanned pages)
        Returns: {summary, keywords}
        """
        try:
            # Encode image to base64
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')

            system_prompt = """You are an expert document analyzer with vision capabilities. Analyze both the text and visual content to create comprehensive summaries.

For each section, provide:
1. A clear summary (2-3 paragraphs) capturing the main points from both text and images
2. Key concepts and keywords (5-10 items)
3. Description of any important visual elements (charts, diagrams, tables)"""

            user_prompt = f"""Please summarize the following content, analyzing both text and visual elements.

{f'Context: {context}' if context else ''}

{f'Text content: {text}' if text else 'No text extracted - please analyze the image.'}

Provide your response in the following format:
SUMMARY:
[Your summary here]

KEYWORDS:
[Comma-separated keywords]"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": user_prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                temperature=0.3,
                max_tokens=1000
            )

            content = response.choices[0].message.content

            # Parse response
            summary, keywords = self._parse_summary_response(content)

            return {
                'summary': summary,
                'keywords': keywords,
                'tokens_used': response.usage.total_tokens
            }

        except Exception as e:
            raise Exception(f"Error summarizing with image: {str(e)}")

    def create_overall_summary(self, chapter_summaries: List[str]) -> Dict:
        """
        Create overall document summary from chapter summaries
        Returns: {summary, keywords}
        """
        try:
            system_prompt = """You are an expert document analyzer. Your task is to create a comprehensive overview of an entire document based on chapter summaries.

Provide:
1. An executive summary (3-5 paragraphs) that captures the document's main themes
2. Overall key concepts and insights (10-15 items)
3. Document structure overview"""

            chapters_text = "\n\n".join([
                f"Chapter {i+1} Summary:\n{summary}"
                for i, summary in enumerate(chapter_summaries)
            ])

            user_prompt = f"""Please create an overall summary of this document based on the following chapter summaries:

{chapters_text}

Provide your response in the following format:
OVERALL SUMMARY:
[Your comprehensive summary here]

KEY INSIGHTS:
[Comma-separated key insights and concepts]"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )

            content = response.choices[0].message.content

            # Parse response
            summary, keywords = self._parse_summary_response(content)

            return {
                'summary': summary,
                'keywords': keywords,
                'tokens_used': response.usage.total_tokens
            }

        except Exception as e:
            raise Exception(f"Error creating overall summary: {str(e)}")

    def _parse_summary_response(self, content: str) -> tuple:
        """Parse summary and keywords from API response"""
        lines = content.split('\n')

        summary_lines = []
        keywords_lines = []
        current_section = None

        for line in lines:
            line_upper = line.strip().upper()

            if 'SUMMARY' in line_upper and ':' in line_upper:
                current_section = 'summary'
                # Check if summary starts on same line
                if line.split(':', 1)[1].strip():
                    summary_lines.append(line.split(':', 1)[1].strip())
                continue
            elif 'KEYWORD' in line_upper or 'INSIGHT' in line_upper:
                current_section = 'keywords'
                # Check if keywords start on same line
                if ':' in line and line.split(':', 1)[1].strip():
                    keywords_lines.append(line.split(':', 1)[1].strip())
                continue

            if current_section == 'summary' and line.strip():
                summary_lines.append(line.strip())
            elif current_section == 'keywords' and line.strip():
                keywords_lines.append(line.strip())

        summary = '\n'.join(summary_lines).strip()
        keywords = ', '.join(keywords_lines).strip()

        return summary, keywords
