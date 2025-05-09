"""Module: seo.py"""
"""
Provides comprehensive SEO keyword recommendations and optimisation tips for content creators 
with support for YouTube, Google trends, and competitor analysis.
"""

from youtubesearchpython import Suggestions, VideosSearch
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
import string
import re
from collections import Counter
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('seo')


def clean_keyword(word):
    """
    Lowercases, strips punctuation and trims whitespace from keyword.
    
    Args:
        word (str): The keyword to clean
        
    Returns:
        str: The cleaned keyword
    """
    if not word or not isinstance(word, str):
        return ""
    return word.lower().strip().translate(str.maketrans('', '', string.punctuation))


def filter_stopwords(words, custom_stopwords=None):
    """
    Removes common stopwords from a list of words.
    
    Args:
        words (list): List of words to filter
        custom_stopwords (list, optional): Additional stopwords to filter
        
    Returns:
        list: Filtered list of words
    """
    if not words:
        return []
        
    stopwords = set(ENGLISH_STOP_WORDS)
    if custom_stopwords:
        stopwords.update(custom_stopwords)
    
    return [w for w in words if w and w.lower() not in stopwords and len(w) > 1]


def get_keyword_variations(keyword):
    """
    Generates variations of the keyword including questions and modifiers.
    
    Args:
        keyword (str): Base keyword
        
    Returns:
        list: List of keyword variations
    """
    clean = clean_keyword(keyword)
    if not clean:
        return []
        
    variations = [
        f"how to {clean}",
        f"best {clean}",
        f"{clean} tutorial",
        f"{clean} guide",
        f"why {clean}",
        f"{clean} tips",
        f"{clean} for beginners",
        f"{clean} advanced",
        f"{clean} review"
    ]
    
    return variations


def analyze_competition(keyword, max_results=5):
    """
    Analyze top videos for a keyword to identify patterns.
    
    Args:
        keyword (str): Keyword to analyze competition for
        max_results (int): Maximum number of videos to analyze
        
    Returns:
        dict: Analysis results including title patterns and video stats
    """
    clean = clean_keyword(keyword)
    if not clean:
        return {"title_patterns": [], "avg_duration": 0}
    
    try:
        search = VideosSearch(clean, limit=max_results)
        results = search.result().get('result', [])
        
        # Extract titles for pattern analysis
        titles = [result.get('title', '') for result in results]
        title_words = ' '.join(titles).lower()
        title_words = re.sub(r'[^\w\s]', ' ', title_words)
        word_counts = Counter(title_words.split())
        
        # Find common patterns excluding stopwords
        common_words = [word for word, count in word_counts.most_common(10) 
                       if word not in ENGLISH_STOP_WORDS and len(word) > 3]
        
        # Calculate average duration if available
        durations = []
        for result in results:
            if 'duration' in result:
                # Parse duration in MM:SS format
                try:
                    parts = result['duration'].split(':')
                    if len(parts) == 2:
                        minutes, seconds = map(int, parts)
                        durations.append(minutes * 60 + seconds)
                except (ValueError, KeyError):
                    pass
        
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        return {
            "title_patterns": common_words,
            "avg_duration": avg_duration
        }
    except Exception as e:
        logger.error(f"Error analyzing competition: {e}")
        return {"title_patterns": [], "avg_duration": 0}


def generate_custom_tips(keyword, competition_data):
    """
    Generate customised tips based on keyword and competition analysis.
    
    Args:
        keyword (str): Base keyword
        competition_data (dict): Data from competition analysis
        
    Returns:
        list: Customised SEO tips
    """
    clean = clean_keyword(keyword)
    tips = [
        f"Include the keyword '{clean}' in your video title, preferably near the beginning.",
        "Place your primary keyword in the first 25 words of the description.",
        f"Create timestamps in your description to increase user engagement and watch time.",
    ]
    
    # Add competition-based tips
    patterns = competition_data.get("title_patterns", [])
    if patterns:
        tips.append(f"Consider including these words that appear in successful videos: {', '.join(patterns[:5])}")
    
    avg_duration = competition_data.get("avg_duration", 0)
    if avg_duration:
        minutes = int(avg_duration // 60)
        if minutes < 8:
            tips.append(f"Top videos for this topic average {minutes} minutes. Consider making your video similarly concise.")
        elif minutes > 15:
            tips.append(f"Top videos for this topic average {minutes} minutes. Plan for detailed, in-depth content.")
    
    # Additional platform-specific tips
    tips.extend([
        "Add closed captions and subtitles to boost accessibility and engagement.",
        "Create playlists to group similar content and increase watch time.",
        "Use end screens and cards to promote related content and increase session time.",
        "Optimise your thumbnail with high contrast colours and minimal text.",
        "Research trending hashtags related to your content and include 3-5 in your description."
    ])
    
    return tips


def categorize_keywords(keywords):
    """
    Categorise keywords by intent (informational, commercial, etc).
    
    Args:
        keywords (list): List of keywords to categorise
        
    Returns:
        dict: Categorised keywords
    """
    if not keywords:
        return {}
        
    categories = {
        "informational": [],
        "commercial": [],
        "navigational": []
    }
    
    info_indicators = ["how", "what", "why", "guide", "tutorial", "tips", "learn"]
    commercial_indicators = ["buy", "price", "cost", "review", "best", "top", "vs", "versus", "comparison"]
    
    for kw in keywords:
        if any(ind in kw for ind in info_indicators):
            categories["informational"].append(kw)
        elif any(ind in kw for ind in commercial_indicators):
            categories["commercial"].append(kw)
        else:
            categories["navigational"].append(kw)
    
    return categories


def get_seo_recommendations(keyword, include_competition=True, debug=False):
    """
    Returns comprehensive SEO recommendations based on YouTube suggestions and competition analysis.

    Args:
        keyword (str): The base keyword to analyse.
        include_competition (bool): Whether to include competition analysis.
        debug (bool): If True, prints raw API response for inspection.

    Returns:
        dict: {
            "primary_keyword": cleaned primary keyword,
            "tags": list of recommended tags,
            "categorised_keywords": keywords organised by search intent,
            "variations": suggested keyword variations,
            "competition": competition analysis results,
            "tips": customised SEO recommendations
        }
    """
    clean = clean_keyword(keyword)
    if not clean:
        logger.warning("Empty or invalid keyword provided")
        return {"error": "Please provide a valid keyword"}
    
    result = {
        "primary_keyword": clean,
        "tags": [],
        "categorized_keywords": {},
        "variations": [],
        "competition": {},
        "tips": []
    }
    
    try:
        # Get YouTube suggestions
        suggestions = Suggestions().get(clean)
        raw_keywords = suggestions.get('result', [])

        if debug:
            logger.debug(f"Raw Suggestions: {raw_keywords}")

        # Clean and filter
        cleaned_tags = [clean_keyword(kw) for kw in raw_keywords]
        filtered_tags = filter_stopwords(cleaned_tags)
        result["tags"] = list(dict.fromkeys(filtered_tags))[:15]  # Deduplicate and limit
        
        # Generate variations
        result["variations"] = get_keyword_variations(clean)
        
        # Categorise keywords
        result["categorised_keywords"] = categorize_keywords(filtered_tags)
        
        # Competition analysis if requested
        if include_competition:
            result["competition"] = analyze_competition(clean)
            
        # Generate tips based on all collected data
        result["tips"] = generate_custom_tips(clean, result["competition"])

    except Exception as e:
        logger.error(f"Error in SEO recommendation generation: {e}")
        result["error"] = str(e)

    return result


# Advanced functionality for more comprehensive analysis
def get_trending_score(keyword, period="month"):
    """
    Placeholder for integrating with Google Trends API to get trending score.
    This would require additional dependencies like pytrends.
    
    Args:
        keyword (str): Keyword to check
        period (str): Time period for trend analysis
        
    Returns:
        float: Trending score from 0-100
    """
    # Implementation would connect to Google Trends API
    return 50  # Placeholder value


def export_recommendations(recommendations, format="markdown"):
    """
    Export recommendations in various formats.
    
    Args:
        recommendations (dict): SEO recommendations from get_seo_recommendations
        format (str): Output format (markdown, json, csv)
        
    Returns:
        str: Formatted recommendations
    """
    if format == "markdown":
        output = f"# SEO Recommendations for '{recommendations['primary_keyword']}'\n\n"
        
        output += "## Recommended Tags\n"
        for tag in recommendations.get('tags', []):
            output += f"- {tag}\n"
        
        output += "\n## Keyword Variations\n"
        for var in recommendations.get('variations', []):
            output += f"- {var}\n"
            
        output += "\n## Optimization Tips\n"
        for i, tip in enumerate(recommendations.get('tips', []), 1):
            output += f"{i}. {tip}\n"
            
        if "competition" in recommendations:
            output += "\n## Competition Analysis\n"
            patterns = recommendations['competition'].get('title_patterns', [])
            if patterns:
                output += "Common words in top videos: " + ", ".join(patterns) + "\n"
            
            avg_duration = recommendations['competition'].get('avg_duration', 0)
            if avg_duration:
                minutes = int(avg_duration // 60)
                seconds = int(avg_duration % 60)
                output += f"Average video length: {minutes}:{seconds:02d}\n"
        
        return output
    
    # Could add JSON and CSV export options here
    
    return "Unsupported format requested"