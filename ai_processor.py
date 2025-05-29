"""
AI processing module for GenAI Content Monitor
Handles content classification and summarization using Hugging Face models
"""

import logging
import re
from typing import List, Optional
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from transformers import BartTokenizer, BartForConditionalGeneration
import torch

logger = logging.getLogger(__name__)

class AIProcessor:
    """AI processor for content classification and summarization"""
    
    def __init__(self, config):
        self.config = config
        self.genai_keywords = config.GENAI_KEYWORDS
        
        # Initialize models
        self._init_summarizer()
        
    def _init_summarizer(self):
        """Initialize the summarization model"""
        try:
            logger.info(f"Loading summarization model: {self.config.SUMMARIZATION_MODEL}")
            self.summarizer = pipeline(
                "summarization",
                model=self.config.SUMMARIZATION_MODEL,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device=0 if torch.cuda.is_available() else -1
            )
            logger.info("Summarization model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load summarization model: {e}")
            self.summarizer = None
    
    def is_genai_related(self, content: str) -> bool:
        """
        Determine if content is related to Generative AI
        Uses keyword matching and context analysis
        """
        if not content:
            return False
        
        content_lower = content.lower()
        
        # First pass: keyword matching
        keyword_matches = 0
        for keyword in self.genai_keywords:
            if keyword in content_lower:
                keyword_matches += 1
        
        # Calculate keyword density
        word_count = len(content.split())
        keyword_density = keyword_matches / max(word_count, 1) if word_count > 0 else 0
        
        # Enhanced pattern matching for GenAI concepts
        genai_patterns = [
            r'\b(gpt-?\d+|chatgpt|claude|dall-?e|midjourney)\b',
            r'\b(large language model|llm)s?\b',
            r'\b(neural network|transformer|diffusion)\b',
            r'\b(text generation|image generation|content generation)\b',
            r'\b(artificial intelligence|machine learning)\b',
            r'\b(natural language processing|nlp)\b',
            r'\b(generative\s+ai|genai)\b'
        ]
        
        pattern_matches = 0
        for pattern in genai_patterns:
            if re.search(pattern, content_lower):
                pattern_matches += 1
        
        # Decision logic
        # High confidence: multiple keyword matches or pattern matches
        if keyword_matches >= 3 or pattern_matches >= 2:
            logger.debug(f"High confidence GenAI content detected (keywords: {keyword_matches}, patterns: {pattern_matches})")
            return True
        
        # Medium confidence: some keywords and reasonable density
        if keyword_matches >= 1 and (keyword_density > 0.001 or pattern_matches >= 1):
            logger.debug(f"Medium confidence GenAI content detected (keywords: {keyword_matches}, patterns: {pattern_matches})")
            return True
        
        # Check for GenAI context even without direct keywords
        context_indicators = [
            'artificial intelligence', 'machine learning', 'deep learning',
            'neural', 'algorithm', 'model training', 'language model',
            'computer vision', 'natural language'
        ]
        
        context_matches = sum(1 for indicator in context_indicators if indicator in content_lower)
        if context_matches >= 3 and keyword_matches >= 1:
            logger.debug(f"Context-based GenAI content detected (context: {context_matches}, keywords: {keyword_matches})")
            return True
        
        logger.debug(f"Content not classified as GenAI (keywords: {keyword_matches}, patterns: {pattern_matches}, context: {context_matches})")
        return False
    
    def summarize_article(self, content: str, max_length: int = 150, min_length: int = 50) -> str:
        """
        Summarize article content using the loaded model
        """
        if not content or not self.summarizer:
            return "Summary not available"
        
        try:
            # Prepare content for summarization
            # Truncate very long content to avoid model limits
            max_input_length = 1024  # Conservative limit for BART
            if len(content.split()) > max_input_length:
                words = content.split()[:max_input_length]
                content = ' '.join(words)
            
            # Generate summary
            summary_result = self.summarizer(
                content,
                max_length=max_length,
                min_length=min_length,
                do_sample=False,
                truncation=True
            )
            
            summary = summary_result[0]['summary_text']
            
            # Clean up summary
            summary = summary.strip()
            if not summary.endswith('.'):
                summary += '.'
            
            logger.debug(f"Generated summary: {summary[:100]}...")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return self._generate_extractive_summary(content, max_length)
    
    def _generate_extractive_summary(self, content: str, max_length: int = 150) -> str:
        """
        Fallback extractive summarization when model fails
        """
        try:
            sentences = content.split('. ')
            if len(sentences) <= 2:
                return content[:max_length] + "..." if len(content) > max_length else content
            
            # Score sentences based on GenAI keyword presence
            scored_sentences = []
            for i, sentence in enumerate(sentences):
                score = 0
                sentence_lower = sentence.lower()
                
                # Score based on keyword presence
                for keyword in self.genai_keywords:
                    if keyword in sentence_lower:
                        score += 1
                
                # Bonus for first few sentences (likely to contain key info)
                if i < 3:
                    score += 0.5
                
                scored_sentences.append((score, sentence))
            
            # Sort by score and take top sentences
            scored_sentences.sort(key=lambda x: x[0], reverse=True)
            
            # Build summary from top sentences
            summary_parts = []
            current_length = 0
            
            for score, sentence in scored_sentences:
                if current_length + len(sentence) > max_length:
                    break
                summary_parts.append(sentence)
                current_length += len(sentence)
            
            summary = '. '.join(summary_parts)
            if summary and not summary.endswith('.'):
                summary += '.'
            
            return summary if summary else content[:max_length] + "..."
            
        except Exception as e:
            logger.error(f"Error in extractive summarization: {e}")
            return content[:max_length] + "..." if len(content) > max_length else content
