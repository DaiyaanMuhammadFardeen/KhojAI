"""
Ultimate Async Web Scraping Module - Enterprise Edition
A high-performance, async web scraping solution with real-time progress tracking.

Features:
- Fully asynchronous for handling multiple concurrent scrapes
- Real-time progress callbacks for UI updates
- Multiple extraction strategies with intelligent fallbacks
- Advanced ad/promo/noise filtering with 80+ patterns
- Honeypot and anti-scraping detection
- Error page recognition (404, 403, CAPTCHA, rate limits)
- Production-ready error handling

Installation:
    pip install aiohttp beautifulsoup4 trafilatura lxml aiofiles

Usage:
    import asyncio
    from scrape import scrape_webpage

    async def main():
        result = await scrape_webpage(
            "https://example.com/article",
            progress_callback=lambda msg: print(f"Progress: {msg}")
        )
        if result['success']:
            print(result['content'])

    asyncio.run(main())

With Web Framework (FastAPI example):
    from fastapi import FastAPI, WebSocket
    from scrape import scrape_webpage

    app = FastAPI()

    @app.websocket("/scrape")
    async def websocket_scrape(websocket: WebSocket):
        await websocket.accept()
        url = await websocket.receive_text()

        async def send_progress(msg):
            await websocket.send_json({"type": "progress", "message": msg})

        result = await scrape_webpage(url, progress_callback=send_progress)
        await websocket.send_json({"type": "result", "data": result})
"""

import re
import json
import asyncio
from typing import Dict, List, Optional, Tuple, Callable, Awaitable
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import aiohttp
from bs4 import BeautifulSoup, Comment
import trafilatura


# ============================================================================
# CONFIGURATION
# ============================================================================

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

# Comprehensive ad/promo/noise selectors
AD_SELECTORS = [
    # Advertisements
    '[id*="ad-"]', '[id*="ads-"]', '[id*="ad_"]', '[id*="adsense"]',
    '[class*="advertisement"]', '[class*="ad-container"]', '[class*="ad-wrapper"]',
    '[class*="ad_"]', '[class*="ad-"]', '[class*="ads-"]', '[class*="adsbygoogle"]',
    '[class*="ad-placement"]', '[class*="ad-slot"]', '[class*="ad-unit"]',
    '[data-ad-slot]', '[data-ad-name]', '[data-ad-region]', '[class*="dfp"]',
    '.ad', '#ad', '.ads', '#ads',

    # Ad networks and trackers
    'iframe[src*="doubleclick"]', 'iframe[src*="googlesyndication"]',
    'iframe[src*="adserver"]', 'iframe[src*="ads."]', '[id*="google_ads"]',
    '[id*="taboola"]', '[id*="outbrain"]', '[id*="disqus"]',
    '[class*="taboola"]', '[class*="outbrain"]', '[class*="revcontent"]',
    '[class*="mgid"]', '[class*="zergnet"]', '[class*="criteo"]',

    # Sponsorships and promotions
    '[id*="sponsor"]', '[class*="sponsor"]', '[class*="sponsored"]',
    '[class*="promo"]', '[class*="promotion"]', '[class*="promotional"]',
    '[class*="partner-content"]', '[data-sponsor]', '[class*="affiliate"]',
    '[class*="native-ad"]', '[class*="paid-content"]',

    # Banners and pop-ups
    '[class*="banner"]', '[id*="banner"]', '[class*="popup"]', '[class*="pop-up"]',
    '[class*="modal"]', '[class*="overlay"]', '[class*="lightbox"]',
    '[class*="interstitial"]', '[role="dialog"][class*="ad"]',

    # Navigation elements
    'nav', 'header', 'footer', '[role="navigation"]', '[role="banner"]',
    '[role="contentinfo"]', '[class*="navbar"]', '[class*="nav-"]',
    '[id*="navbar"]', '[id*="navigation"]', '[class*="menu"]',
    '[class*="breadcrumb"]', '[class*="pagination"]', '[class*="pager"]',

    # Sidebars and widgets
    'aside', '[class*="sidebar"]', '[id*="sidebar"]', '[class*="widget"]',
    '[class*="side-"]', '[class*="rail"]', '[id*="rail"]',

    # Social and sharing
    '[class*="social"]', '[class*="share"]', '[class*="sharing"]',
    '[class*="follow"]', '[class*="subscribe"]', '[class*="newsletter"]',
    '[id*="social"]', '[id*="share"]', '[aria-label*="share"]',

    # Related and recommended content
    '[class*="related"]', '[class*="recommended"]', '[class*="you-may-like"]',
    '[class*="more-stories"]', '[class*="also-read"]', '[class*="trending"]',
    '[id*="related"]', '[id*="recommended"]',

    # Comments
    '[class*="comment"]', '[id*="comment"]', '[class*="discussion"]',
    '[id*="disqus"]', '[class*="fb-comments"]', '[id*="respond"]',

    # Legal and boilerplate
    '[class*="disclaimer"]', '[class*="legal"]', '[class*="cookie"]',
    '[class*="gdpr"]', '[class*="consent"]', '[id*="cookie"]',
    '[class*="privacy-notice"]', '[class*="terms"]',

    # Honeypots and hidden elements
    '[style*="display:none"]', '[style*="display: none"]',
    '[style*="visibility:hidden"]', '[style*="visibility: hidden"]',
    '[hidden]', '[aria-hidden="true"]', '.hidden', '#hidden',
    '[class*="honeypot"]', '[id*="honeypot"]', '[class*="hp-"]',

    # Search and forms
    '[class*="search-form"]', '[id*="search"]', '[role="search"]',

    # Metadata and tracking
    '[class*="metadata"]', '[class*="byline"]', '[class*="author-bio"]',
    '[class*="published"]', '[class*="timestamp"]', '[class*="tags"]',
    '[class*="category"]', '[class*="analytics"]', '[class*="tracking"]'
]

# IAB standard ad sizes
COMMON_AD_SIZES = [
    (728, 90), (300, 250), (160, 600), (320, 50), (300, 600),
    (970, 250), (320, 100), (336, 280), (300, 1050), (970, 90)
]

# Content-positive and content-negative class/id patterns
POSITIVE_PATTERNS = r'article|content|post|entry|text|body|main|story|paragraph|prose'
NEGATIVE_PATTERNS = r'sidebar|nav|footer|header|comment|widget|ad|promo|banner|related|share|social|sponsor|recommended|trending|popular|subscribe|newsletter|author-bio|metadata|breadcrumb|pagination|menu'

# Promotion and marketing keywords
PROMO_KEYWORDS = [
    'buy now', 'shop now', 'order now', 'subscribe', 'sign up', 'register',
    'download now', 'get started', 'try free', 'free trial', 'limited offer',
    'special offer', 'discount', 'sale', 'coupon', 'promo code', 'deal',
    'sponsored', 'advertisement', 'click here', 'learn more', 'read more',
    'see also', 'related products', 'you may also like', 'recommended for you',
    'trending now', 'popular posts', 'don\'t miss', 'follow us', 'join us',
    'share this', 'tweet this', 'pin it', 'email us', 'contact us',
    'view all', 'load more', 'show more', 'continue reading'
]

# Error page indicators
ERROR_INDICATORS = [
    '404', 'not found', 'page not found', 'error',
    'access denied', 'forbidden', 'rate limit', 'too many requests',
    'captcha', 'robot', 'blocked', 'unavailable', 'maintenance',
    'coming soon', 'under construction'
]

# Boilerplate patterns to remove
BOILERPLATE_PATTERNS = [
    r'all rights reserved',
    r'copyright \d{4}',
    r'terms of service',
    r'privacy policy',
    r'cookie policy',
    r'gdpr',
    r'this website uses cookies',
    r'by continuing to use',
    r'accept cookies',
    r'share this article',
    r'follow us on',
    r'subscribe to our newsletter',
    r'sign up for updates',
    r'related articles',
    r'you may also like',
    r'recommended for you',
    r'trending now',
    r'popular posts',
    r'advertisement',
    r'sponsored content'
]


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

async def progress_log(message: str, callback: Optional[Callable[[str], Awaitable[None]]] = None):
    """Log progress message and call callback if provided."""
    print(message)
    if callback:
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(message)
            else:
                callback(message)
        except Exception as e:
            print(f"Progress callback error: {e}")


async def check_robots_txt(url: str, timeout: int = 10) -> bool:
    """Check if URL is allowed by robots.txt with improved async handling."""
    try:
        rp = RobotFileParser()
        parsed = urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        rp.set_url(robots_url)

        # Run in executor since RobotFileParser is blocking
        # Set timeout for the HTTP request
        def fetch_with_timeout():
            import socket
            # Set global socket timeout temporarily
            old_timeout = socket.getdefaulttimeout()
            socket.setdefaulttimeout(timeout)
            try:
                rp.read()
                return rp.can_fetch(USER_AGENT, url)
            finally:
                socket.setdefaulttimeout(old_timeout)
        
        loop = asyncio.get_event_loop()
        # Add jitter to timeout to prevent thundering herd
        jittered_timeout = timeout + (0.1 * (hash(url) % 10))
        result = await asyncio.wait_for(loop.run_in_executor(None, fetch_with_timeout), timeout=jittered_timeout)
        return result
    except asyncio.TimeoutError:
        # Log timeout but allow scraping to continue
        print(f"⚠️  Robots.txt check timed out for {url}, continuing anyway")
        return True  # Allow if robots.txt check times out
    except Exception as e:
        print(f"⚠️  Robots.txt check failed for {url}: {e}, continuing anyway")
        return True  # Allow if robots.txt check fails


async def fetch_page(
    url: str,
    timeout: int = 15,
    callback: Optional[Callable[[str], Awaitable[None]]] = None
) -> Tuple[Optional[str], Optional[int]]:
    """
    Fetch webpage HTML with proper headers and error handling.

    Returns:
        Tuple of (html_content, status_code) or (None, status_code) on error
    """
    headers = {
        'User-Agent': USER_AGENT,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }

    try:
        await progress_log(f"🌐 Fetching URL: {url}", callback)

        timeout_obj = aiohttp.ClientTimeout(total=timeout)
        async with aiohttp.ClientSession(timeout=timeout_obj) as session:
            async with session.get(url, headers=headers, allow_redirects=True) as response:
                status_code = response.status

                # Check for common error status codes
                if status_code == 403:
                    await progress_log("⚠️  Access forbidden (403) - possible anti-scraping measure", callback)
                    return None, 403
                elif status_code == 429:
                    await progress_log("⚠️  Rate limited (429) - too many requests", callback)
                    return None, 429
                elif status_code == 503:
                    await progress_log("⚠️  Service unavailable (503) - server error", callback)
                    return None, 503
                elif status_code >= 400:
                    await progress_log(f"⚠️  HTTP error {status_code}", callback)
                    return None, status_code

                html = await response.text()

                # Check for CAPTCHA indicators in content
                content_lower = html.lower()
                captcha_indicators = ['captcha', 'recaptcha', 'hcaptcha', 'cloudflare']
                if any(indicator in content_lower for indicator in captcha_indicators):
                    if 'complete the captcha' in content_lower or 'verify you are human' in content_lower:
                        await progress_log("⚠️  CAPTCHA detected - page requires human verification", callback)
                        return None, 403

                await progress_log(f"✅ Fetched {len(html)} bytes", callback)
                return html, status_code

    except asyncio.TimeoutError:
        await progress_log(f"⚠️  Request timeout after {timeout} seconds", callback)
        return None, 408
    except aiohttp.ClientError as e:
        await progress_log(f"⚠️  Request failed: {e}", callback)
        return None, None


def is_error_page(soup: BeautifulSoup, text: str) -> bool:
    """Check if page is an error page (404, 403, CAPTCHA, etc.)."""
    text_lower = text.lower()

    # Check for error indicators in text
    for indicator in ERROR_INDICATORS:
        if indicator in text_lower and len(text) < 1000:
            return True

    # Check title for error indicators
    title = soup.find('title')
    if title:
        title_text = title.get_text().lower()
        for indicator in ERROR_INDICATORS:
            if indicator in title_text:
                return True

    # Check for CAPTCHA forms
    if soup.find('form', {'id': re.compile(r'captcha', re.I)}):
        return True

    return False


def is_honeypot_element(element) -> bool:
    """Detect honeypot elements designed to catch scrapers."""
    # Check inline styles for hidden elements
    style = element.get('style', '')
    if any(pattern in style.lower() for pattern in ['display:none', 'display: none', 'visibility:hidden', 'visibility: hidden']):
        return True

    # Check classes for honeypot indicators
    classes = ' '.join(element.get('class', [])).lower()
    if 'honeypot' in classes or 'hp-' in classes or 'hidden' in classes:
        return True

    # Check for hidden attribute
    if element.has_attr('hidden') or element.get('aria-hidden') == 'true':
        return True

    # Check for off-screen positioning
    if 'position:absolute' in style and ('left:-' in style or 'top:-' in style):
        return True

    return False


async def extract_json_ld(soup: BeautifulSoup, callback: Optional[Callable[[str], Awaitable[None]]] = None) -> Optional[Dict]:
    """Extract structured data from JSON-LD schema.org markup."""
    scripts = soup.find_all('script', type='application/ld+json')
    for script in scripts:
        try:
            data = json.loads(script.string)

            # Handle nested structures
            if isinstance(data, list):
                data = next((item for item in data if item.get('@type') == 'Article'), data[0] if data else {})

            if data.get('@type') in ['Article', 'NewsArticle', 'BlogPosting']:
                await progress_log("📄 Found JSON-LD structured data", callback)
                return {
                    'title': data.get('headline', ''),
                    'content': data.get('articleBody', ''),
                    'author': data.get('author', {}).get('name', '') if isinstance(data.get('author'), dict) else '',
                    'date': data.get('datePublished', '')
                }
        except (json.JSONDecodeError, AttributeError, StopIteration):
            continue
    return None


def remove_ads_and_noise(soup: BeautifulSoup) -> None:
    """Remove ads, scripts, styles, and other noise from parsed HTML."""
    # Remove script, style, and other non-content tags
    for tag in soup(['script', 'style', 'noscript', 'iframe', 'embed', 'object', 'svg']):
        tag.decompose()

    # Remove comments
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()

    # Remove honeypot elements first (before other filtering)
    for element in soup.find_all():
        if is_honeypot_element(element):
            element.decompose()

    # Remove ad-related elements by selector
    for selector in AD_SELECTORS:
        try:
            for element in soup.select(selector):
                element.decompose()
        except Exception:
            continue

    # Remove navigation, header, footer elements
    for tag in ['nav', 'header', 'footer', 'aside']:
        for element in soup.find_all(tag):
            element.decompose()

    # Remove elements with navigation/menu roles
    for element in soup.find_all(role=['navigation', 'banner', 'contentinfo', 'complementary']):
        element.decompose()

    # Remove breadcrumbs, pagination
    for element in soup.find_all(class_=re.compile(r'breadcrumb|pagination|pager', re.I)):
        element.decompose()

    # Remove social sharing elements
    for element in soup.find_all(class_=re.compile(r'social|share|sharing|follow', re.I)):
        element.decompose()

    # Remove related/recommended content sections
    for element in soup.find_all(class_=re.compile(r'related|recommended|trending|popular', re.I)):
        element.decompose()

    # Remove comment sections
    for element in soup.find_all(id=re.compile(r'comment|disqus|respond', re.I)):
        element.decompose()

    # Remove elements with ad-sized dimensions
    for elem in soup.find_all(['div', 'aside', 'section']):
        try:
            width = elem.get('width', '')
            height = elem.get('height', '')
            style = elem.get('style', '')

            width_match = re.search(r'width:\s*(\d+)px', style)
            height_match = re.search(r'height:\s*(\d+)px', style)

            if width_match and height_match:
                w, h = int(width_match.group(1)), int(height_match.group(1))
                if (w, h) in COMMON_AD_SIZES:
                    elem.decompose()
                    continue

            if width and height:
                try:
                    if (int(width), int(height)) in COMMON_AD_SIZES:
                        elem.decompose()
                        continue
                except ValueError:
                    pass
        except (ValueError, TypeError, AttributeError):
            pass

    # Remove forms
    for form in soup.find_all('form'):
        form.decompose()

    # Remove empty elements
    for _ in range(2):
        for elem in soup.find_all():
            if not elem.get_text(strip=True) and not elem.find_all(['img', 'video', 'audio']):
                elem.decompose()

    # Remove elements with promotional keywords
    for elem in soup.find_all(['div', 'p', 'span', 'a']):
        text = elem.get_text(strip=True).lower()
        if len(text) < 100:
            if any(keyword in text for keyword in PROMO_KEYWORDS):
                words = text.split()
                promo_word_count = sum(1 for word in words if any(k in word for k in PROMO_KEYWORDS))
                if promo_word_count / max(len(words), 1) > 0.3:
                    elem.decompose()


def calculate_content_score(element) -> float:
    """Calculate content quality score for an element."""
    if not element:
        return 0.0

    text = element.get_text(strip=True)
    if len(text) < 25:
        return 0.0

    score = 0.0
    score += min(len(text) / 100, 10)

    paragraphs = element.find_all('p')
    score += len(paragraphs) * 3

    if paragraphs:
        avg_p_length = sum(len(p.get_text(strip=True)) for p in paragraphs) / len(paragraphs)
        if avg_p_length > 50:
            score += 5

    links = element.find_all('a')
    if text:
        link_text = sum(len(a.get_text(strip=True)) for a in links)
        link_density = link_text / len(text)
        if link_density > 0.5:
            score -= 10
        elif link_density < 0.2:
            score += 3

    attrs = ' '.join(element.get('class', []) + [element.get('id', '') or ''])
    if re.search(POSITIVE_PATTERNS, attrs, re.I):
        score += 8
    if re.search(NEGATIVE_PATTERNS, attrs, re.I):
        score -= 8

    if element.name in ['article', 'main', 'section']:
        score += 10
    elif element.name in ['aside', 'nav', 'footer', 'header']:
        score -= 10

    html_length = len(str(element))
    if html_length > 0:
        density = len(text) / html_length
        score += density * 10

    return score


def find_main_content(soup: BeautifulSoup) -> Optional[BeautifulSoup]:
    """Find main content area using multiple strategies."""
    # Strategy 1: Semantic HTML5 tags
    for tag in ['article', 'main']:
        element = soup.find(tag)
        if element and len(element.get_text(strip=True)) > 200:
            return element

    # Strategy 2: Score all potential content containers
    candidates = []
    for tag in ['div', 'section', 'article']:
        elements = soup.find_all(tag)
        for elem in elements:
            score = calculate_content_score(elem)
            if score > 5:
                candidates.append((score, elem))

    if candidates:
        candidates.sort(reverse=True, key=lambda x: x[0])
        return candidates[0][1]

    # Strategy 3: Common content class names
    content_patterns = ['content', 'post-content', 'article-content', 'entry-content', 'post-body']
    for pattern in content_patterns:
        element = soup.find(class_=re.compile(pattern, re.I))
        if element and len(element.get_text(strip=True)) > 200:
            return element

    return None


def extract_sentences(text: str, min_words: int = 5, max_words: int = 100) -> List[str]:
    """Extract meaningful sentences from text with advanced filtering."""
    sentences = re.split(r'[.!?]+', text)

    valid_sentences = []
    seen_sentences = set()

    for sent in sentences:
        sent = sent.strip()

        if not sent:
            continue

        words = sent.split()
        word_count = len(words)

        if word_count < min_words or word_count > max_words:
            continue

        sent_lower = sent.lower()
        if sent_lower in seen_sentences:
            continue
        seen_sentences.add(sent_lower)

        if re.match(r'^(Home|About|Contact|Menu|Skip|Share|Tweet|Follow|Subscribe|Login|Logout|Register|Sign up|Sign in)', sent, re.I):
            continue

        if re.match(r'^(Click|Read|View|See|Watch|Download|Buy|Shop|Order|Get|Try|Start)', sent, re.I):
            continue

        promo_count = sum(1 for keyword in PROMO_KEYWORDS if keyword in sent_lower)
        if promo_count >= 2:
            continue

        digit_ratio = sum(c.isdigit() for c in sent) / max(len(sent), 1)
        if digit_ratio > 0.3:
            continue

        if sent.isupper() and len(sent) > 10:
            continue

        upper_ratio = sum(c.isupper() for c in sent) / max(len(sent), 1)
        if upper_ratio > 0.5 and len(sent) > 20:
            continue

        if sent.count(',') > word_count * 0.3:
            continue

        punct_ratio = sum(c in '!@#$%^&*()[]{}|\\/<>~`' for c in sent) / max(len(sent), 1)
        if punct_ratio > 0.2:
            continue

        if re.search(r'copyright|©|®|™|all rights reserved|terms of service|privacy policy', sent_lower):
            continue

        if re.search(r'follow us|like us|share this|tweet this|subscribe|newsletter', sent_lower):
            continue

        if re.search(r'related article|you may also|recommended for|trending now|popular post', sent_lower):
            continue

        alpha_count = sum(c.isalpha() for c in sent)
        if alpha_count < word_count * 2:
            continue

        if re.match(r'^\w+\s+\d+,\s+\d{4}', sent):
            continue
        if re.match(r'^By\s+\w+', sent, re.I):
            continue
        if re.match(r'^\d+\s+(min|minute|hour|comment|view|share)', sent, re.I):
            continue

        valid_sentences.append(sent)

    return valid_sentences


def clean_text(text: str) -> str:
    """Clean and normalize extracted text."""
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'\t+', ' ', text)

    text = re.sub(r'(Share on|Follow us|Subscribe to|Read more|Click here|Learn more|View all|Show more|Load more|Continue reading)', '', text, flags=re.I)

    for pattern in BOILERPLATE_PATTERNS:
        text = re.sub(pattern, '', text, flags=re.I)

    text = re.sub(r'\S+@\S+\.\S+', '', text)
    text = re.sub(r'http\S+|www\.\S+', '', text)
    text = re.sub(r'@\w+', '', text)
    text = re.sub(r'#\w+', '', text)
    text = re.sub(r'\.{2,}', '.', text)
    text = re.sub(r'\!{2,}', '!', text)
    text = re.sub(r'\?{2,}', '?', text)
    text = re.sub(r'[^\x20-\x7E\n]', '', text)
    text = re.sub(r'[\|•·►▪▫■□●○◆◇★☆]+', '', text)
    text = re.sub(r'\{.*?\}', '', text)
    text = re.sub(r'function\s*\(.*?\)', '', text)
    text = re.sub(r'var\s+\w+\s*=', '', text)
    text = re.sub(r'\d{1,2}/\d{1,2}/\d{2,4}', '', text)
    text = re.sub(r'\d{1,2}:\d{2}\s*(AM|PM|am|pm)?', '', text)
    text = re.sub(r'\d+\s*(min|mins|minute|minutes|hour|hours)\s*(read|reading)', '', text, flags=re.I)
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


# ============================================================================
# MAIN ASYNC SCRAPING FUNCTION
# ============================================================================

async def scrape_webpage(
    url: str,
    max_content_length: int = 10000,
    respect_robots: bool = True,
    min_content_length: int = 100,
    extract_sentences_flag: bool = True,
    progress_callback: Optional[Callable[[str], Awaitable[None]]] = None
) -> Dict[str, any]:
    """
    Ultimate async web scraping function with real-time progress tracking.
    """
    result = {
        'url': url,
        'title': '',
        'content': '',
        'method': '',
        'success': False,
        'error': None
    }

    # Use progress_callback (not callback)
    await progress_log(f"\n{'='*60}", progress_callback)
    await progress_log(f"🔍 Starting scrape: {url}", progress_callback)
    await progress_log(f"{'='*60}", progress_callback)

    # Check robots.txt
    if respect_robots:
        await progress_log("🤖 Checking robots.txt...", progress_callback)
        allowed = await check_robots_txt(url, timeout=10)
        if not allowed:
            result['error'] = 'Blocked by robots.txt'
            await progress_log(f"❌ {result['error']}", progress_callback)
            return result
        await progress_log("✅ Robots.txt check passed", progress_callback)

    # Fetch page
    fetch_result = await fetch_page(url, callback=progress_callback)
    if not fetch_result or fetch_result[0] is None:
        html, status_code = fetch_result if fetch_result else (None, None)
        if status_code == 403:
            result['error'] = 'Access forbidden (403) - possible anti-scraping or authentication required'
        elif status_code == 429:
            result['error'] = 'Rate limited (429) - too many requests'
        elif status_code == 503:
            result['error'] = 'Service unavailable (503)'
        elif status_code == 408:
            result['error'] = 'Request timeout'
        elif status_code:
            result['error'] = f'HTTP error {status_code}'
        else:
            result['error'] = 'Failed to fetch page'
        await progress_log(f"❌ {result['error']}", progress_callback)
        return result

    html, status_code = fetch_result

    await progress_log("🔨 Parsing HTML...", progress_callback)
    soup = BeautifulSoup(html, 'html.parser')

    # Check if it's an error page
    page_text = soup.get_text()
    if is_error_page(soup, page_text):
        result['error'] = 'Error page detected (404, 403, CAPTCHA, or maintenance)'
        await progress_log(f"❌ {result['error']}", progress_callback)
        return result

    # Extract title
    title_tag = soup.find('title')
    result['title'] = title_tag.get_text(strip=True) if title_tag else 'No title'
    await progress_log(f"📌 Page title: {result['title'][:60]}...", progress_callback)

    # ========================================================================
    # STRATEGY 1: Try Trafilatura (specialized extraction library)
    # ========================================================================
    try:
        await progress_log("🔍 Strategy 1: Trying Trafilatura extraction...", progress_callback)

        loop = asyncio.get_event_loop()
        content = await asyncio.wait_for(
            loop.run_in_executor(
                None,
                lambda: trafilatura.extract(
                    html,
                    include_comments=False,
                    include_tables=True,
                    no_fallback=False
                )
            ),
            timeout=30
        )

        if content and len(content) >= min_content_length:
            result['content'] = content
            result['method'] = 'trafilatura'
            result['success'] = True
            await progress_log(f"✅ Trafilatura success: {len(content)} chars extracted", progress_callback)
        else:
            await progress_log(f"⚠️  Trafilatura insufficient: {len(content) if content else 0} chars", progress_callback)
    except Exception as e:
        await progress_log(f"⚠️  Trafilatura failed: {e}", progress_callback)

    # ========================================================================
    # STRATEGY 2: JSON-LD Structured Data
    # ========================================================================
    if not result['success']:
        await progress_log("🔍 Strategy 2: Trying JSON-LD extraction...", progress_callback)
        json_ld_data = await asyncio.wait_for(extract_json_ld(soup, progress_callback), timeout=10)

        if json_ld_data and json_ld_data.get('content'):
            content = json_ld_data['content']
            if len(content) >= min_content_length:
                result['content'] = content
                result['title'] = json_ld_data.get('title') or result['title']
                result['method'] = 'json-ld'
                result['success'] = True
                await progress_log(f"✅ JSON-LD success: {len(content)} chars extracted", progress_callback)
            else:
                await progress_log(f"⚠️  JSON-LD insufficient: {len(content)} chars", progress_callback)
        else:
            await progress_log("⚠️  No valid JSON-LD data found", progress_callback)

    # ========================================================================
    # STRATEGY 3: Custom Content Extraction with Scoring
    # ========================================================================
    if not result['success']:
        await progress_log("🔍 Strategy 3: Custom content extraction...", progress_callback)

        await progress_log("🧹 Removing ads and noise...", progress_callback)
        remove_ads_and_noise(soup)

        await progress_log("🎯 Finding main content area...", progress_callback)
        main_content = find_main_content(soup)

        if main_content:
            content = main_content.get_text(separator=' ', strip=True)

            if len(content) >= min_content_length:
                result['content'] = content
                result['method'] = 'custom'
                result['success'] = True
                await progress_log(f"✅ Custom extraction success: {len(content)} chars", progress_callback)
            else:
                await progress_log(f"⚠️  Custom extraction insufficient: {len(content)} chars", progress_callback)
        else:
            await progress_log("⚠️  Could not identify main content", progress_callback)

    # ========================================================================
    # FALLBACK: Get all remaining text
    # ========================================================================
    if not result['success']:
        await progress_log("🔍 Fallback: Extracting all remaining text...", progress_callback)
        content = soup.get_text(separator=' ', strip=True)

        if len(content) >= min_content_length:
            result['content'] = content
            result['method'] = 'fallback'
            result['success'] = True
            await progress_log(f"✅ Fallback successful: {len(content)} chars", progress_callback)
        else:
            result['error'] = f'Insufficient content ({len(content)} chars)'
            await progress_log(f"❌ {result['error']}", progress_callback)
            return result

    # ========================================================================
    # POST-PROCESSING
    # ========================================================================
    if result['success']:
        await progress_log("🧼 Cleaning text...", progress_callback)
        result['content'] = clean_text(result['content'])

        if len(result['content']) < min_content_length:
            result['success'] = False
            result['error'] = f'Insufficient content after cleaning ({len(result["content"])} chars)'
            await progress_log(f"❌ {result['error']}", progress_callback)
            return result

        if extract_sentences_flag and result['method'] != 'trafilatura':
            await progress_log("📝 Extracting meaningful sentences...", progress_callback)
            sentences = extract_sentences(result['content'])
            if sentences:
                result['content'] = ' '.join(sentences)
                await progress_log(f"✅ Extracted {len(sentences)} clean sentences", progress_callback)
            else:
                await progress_log(f"⚠️  No valid sentences found, keeping cleaned content", progress_callback)

        if extract_sentences_flag:
            await progress_log("🔄 Removing duplicate sentences...", progress_callback)
            sentences = result['content'].split('. ')
            seen = set()
            unique_sentences = []
            for sent in sentences:
                sent_clean = sent.strip().lower()
                if sent_clean and sent_clean not in seen and len(sent_clean) > 20:
                    seen.add(sent_clean)
                    unique_sentences.append(sent.strip())

            if unique_sentences:
                result['content'] = '. '.join(unique_sentences)
                if not result['content'].endswith('.'):
                    result['content'] += '.'

        if max_content_length > 0 and len(result['content']) > max_content_length:
            await progress_log(f"✂️  Truncating content to {max_content_length} chars...", progress_callback)
            truncated = result['content'][:max_content_length]
            last_period = truncated.rfind('.')
            if last_period > max_content_length * 0.8:
                result['content'] = truncated[:last_period + 1]
            else:
                result['content'] = truncated + '...'

        content_lower = result['content'].lower()
        error_signs = ['404', 'not found', 'access denied', 'captcha']
        if len(result['content']) < 500 and any(sign in content_lower for sign in error_signs):
            result['success'] = False
            result['error'] = 'Content appears to be an error page'
            await progress_log(f"❌ {result['error']}", progress_callback)
            return result

        await progress_log(f"\n{'='*60}", progress_callback)
        await progress_log(f"✅ SCRAPING COMPLETE", progress_callback)
        await progress_log(f"{'='*60}", progress_callback)
        await progress_log(f"Method: {result['method']}", progress_callback)
        await progress_log(f"Title: {result['title'][:60]}..." if len(result['title']) > 60 else f"Title: {result['title']}", progress_callback)
        await progress_log(f"Content length: {len(result['content'])} chars", progress_callback)
        await progress_log(f"Status: ✅ Success", progress_callback)
        await progress_log(f"{'='*60}\n", progress_callback)

    return result


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

async def scrape_multiple(
    urls: List[str],
    delay: float = 1.0,
    progress_callback: Optional[Callable[[str], Awaitable[None]]] = None,
    **kwargs
) -> List[Dict]:
    """
    Scrape multiple URLs sequentially with polite delays.

    Args:
        urls: List of URLs to scrape
        delay: Delay between requests in seconds
        progress_callback: Async callback for progress updates
        **kwargs: Additional arguments to pass to scrape_webpage()

    Returns:
        List of result dictionaries
    """
    results = []
    for i, url in enumerate(urls):
        if progress_callback:
            await progress_callback(f"\n[{i+1}/{len(urls)}] Processing: {url}")

        try:
            result = await asyncio.wait_for(scrape_webpage(url, progress_callback=progress_callback, **kwargs), timeout=60)
            results.append(result)
        except asyncio.TimeoutError:
            results.append({
                'url': url,
                'title': '',
                'content': '',
                'method': '',
                'success': False,
                'error': 'Scraping timeout'
            })

        if i < len(urls) - 1:
            await asyncio.sleep(delay)

    return results


async def scrape_concurrent(
    urls: List[str],
    max_concurrent: int = 5,
    progress_callback: Optional[Callable[[str], Awaitable[None]]] = None,
    **kwargs
) -> List[Dict]:
    """
    Scrape multiple URLs concurrently with a concurrency limit.

    Args:
        urls: List of URLs to scrape
        max_concurrent: Maximum number of concurrent requests
        progress_callback: Async callback for progress updates
        **kwargs: Additional arguments to pass to scrape_webpage()

    Returns:
        List of result dictionaries
    """
    semaphore = asyncio.Semaphore(max_concurrent)

    async def scrape_with_semaphore(url: str, index: int):
        async with semaphore:
            if progress_callback:
                await progress_callback(f"\n[{index+1}/{len(urls)}] Starting: {url}")
            return await scrape_webpage(url, progress_callback=progress_callback, **kwargs)

    tasks = [scrape_with_semaphore(url, i) for i, url in enumerate(urls)]
    results = await asyncio.wait_for(asyncio.gather(*tasks, return_exceptions=True), timeout=len(urls) * 60)

    # Handle exceptions in results
    processed_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            processed_results.append({
                'url': urls[i],
                'title': '',
                'content': '',
                'method': '',
                'success': False,
                'error': f'Exception: {str(result)}'
            })
        else:
            processed_results.append(result)

    return processed_results


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    async def main():
        # Example 1: Single URL with progress tracking
        print("=" * 80)
        print("EXAMPLE 1: Single URL Scraping")
        print("=" * 80)

        async def progress_callback(message: str):
            """Print progress messages in real-time."""
            print(f"[PROGRESS] {message}")

        test_url = "https://www.scrapethissite.com/pages/ajax-javascript/"
        result = await scrape_webpage(
            test_url,
            progress_callback=progress_callback,
            max_content_length=3000
        )

        if result['success']:
            print(f"\n✅ SUCCESS!")
            print(f"Title: {result['title']}")
            print(f"Method: {result['method']}")
            print(f"\nContent preview:\n{result['content'][:500]}...")
        else:
            print(f"\n❌ FAILED: {result['error']}")

        print("\n" + "=" * 80)
        print("EXAMPLE 2: Concurrent Scraping (Multiple URLs)")
        print("=" * 80)

        # Example 2: Multiple URLs concurrently
        test_urls = [
            "https://www.scrapethissite.com/pages/simple/",
            "https://www.scrapethissite.com/pages/forms/",
            "https://www.scrapethissite.com/pages/frames/",
            "https://www.scrapethissite.com/pages/advanced/?gotcha=headers"
        ]

        results = await scrape_concurrent(
            test_urls,
            max_concurrent=3,
            progress_callback=progress_callback,
            max_content_length=2000
        )

        print("\n" + "=" * 80)
        print("CONCURRENT SCRAPING RESULTS")
        print("=" * 80)
        for i, result in enumerate(results):
            print(f"\n[{i+1}] {result['url']}")
            print(f"    Status: {'✅ Success' if result['success'] else '❌ Failed'}")
            if result['success']:
                print(f"    Method: {result['method']}")
                print(f"    Content: \n{'=' * 60}\n{result['content']}\n{'=' * 60}")
            else:
                print(f"    Error: {result['error']}")

    # Run the async main function
    asyncio.run(main())
