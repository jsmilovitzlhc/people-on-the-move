"""
AI-powered post generation using Claude API.
Falls back to templates if API is unavailable.
"""
import logging
from typing import Dict, Optional

from config import settings
from .templates import generate_post_from_template

logger = logging.getLogger(__name__)


class PostGenerator:
    """Generate LinkedIn posts using Claude API or fallback templates."""

    def __init__(self):
        self.client = None
        self._init_client()

    def _init_client(self):
        """Initialize Anthropic client if API key is available."""
        if not settings.ANTHROPIC_API_KEY:
            logger.warning("ANTHROPIC_API_KEY not set - using template fallback")
            return

        try:
            from anthropic import Anthropic
            self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            logger.info("Claude API client initialized")
        except ImportError:
            logger.warning("anthropic package not installed - using template fallback")
        except Exception as e:
            logger.error(f"Error initializing Claude client: {e}")

    def _build_prompt(self, announcement: Dict) -> str:
        """Build the prompt for Claude."""
        parts = []

        parts.append("Write a LinkedIn post celebrating this executive career move:")
        parts.append("")

        if announcement.get('person_name'):
            parts.append(f"Person: {announcement['person_name']}")

        if announcement.get('new_title'):
            parts.append(f"New Title: {announcement['new_title']}")

        if announcement.get('company_name'):
            parts.append(f"Company: {announcement['company_name']}")

        if announcement.get('action'):
            parts.append(f"Action: {announcement['action']}")

        if announcement.get('previous_title'):
            parts.append(f"Previous Title: {announcement['previous_title']}")

        if announcement.get('previous_company'):
            parts.append(f"Previous Company: {announcement['previous_company']}")

        # Add context from raw article if available
        if announcement.get('raw_text'):
            # Truncate to avoid token limits
            raw_text = announcement['raw_text'][:500]
            parts.append("")
            parts.append(f"Article excerpt: {raw_text}")

        return "\n".join(parts)

    def generate_with_claude(self, announcement: Dict) -> Optional[str]:
        """
        Generate post using Claude API.

        Args:
            announcement: Dict with announcement data

        Returns:
            Generated post string, or None if generation fails
        """
        if not self.client:
            return None

        try:
            prompt = self._build_prompt(announcement)

            response = self.client.messages.create(
                model=settings.CLAUDE_MODEL,
                max_tokens=settings.CLAUDE_MAX_TOKENS,
                system=settings.POST_SYSTEM_PROMPT,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # Extract text from response
            if response.content and len(response.content) > 0:
                post = response.content[0].text
                logger.info("Generated post with Claude API")
                return post.strip()

            return None

        except Exception as e:
            logger.error(f"Error generating post with Claude: {e}")
            return None

    def generate(self, announcement: Dict, use_ai: bool = True) -> str:
        """
        Generate a LinkedIn post for an announcement.

        Args:
            announcement: Dict with announcement data
            use_ai: If True, try Claude API first; if False, use templates only

        Returns:
            Generated post string
        """
        # Try Claude API first if enabled
        if use_ai and self.client:
            ai_post = self.generate_with_claude(announcement)
            if ai_post:
                return ai_post
            logger.info("Claude API failed, falling back to templates")

        # Fall back to templates
        return generate_post_from_template(announcement)

    def regenerate(self, announcement: Dict) -> str:
        """
        Generate a new version of a post (always uses AI if available).

        Args:
            announcement: Dict with announcement data

        Returns:
            New generated post string
        """
        return self.generate(announcement, use_ai=True)


# Singleton instance
_generator = None


def get_generator() -> PostGenerator:
    """Get or create the PostGenerator singleton."""
    global _generator
    if _generator is None:
        _generator = PostGenerator()
    return _generator


def generate_post(announcement: Dict, use_ai: bool = True) -> str:
    """
    Convenience function to generate a post.

    Args:
        announcement: Dict with announcement data
        use_ai: If True, try Claude API first

    Returns:
        Generated post string
    """
    generator = get_generator()
    return generator.generate(announcement, use_ai=use_ai)
