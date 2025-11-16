#!/usr/bin/env python3
"""
WebSocket crawler for real-time web crawling
"""

import asyncio
import json
import time
import os
from urllib.parse import urljoin, urlparse
from collections import deque
from bs4 import BeautifulSoup
import aiohttp
from flask_sock import Sock
from datetime import datetime

# MongoDB support (optional)
try:
    from motor.motor_asyncio import AsyncIOMotorClient
    MONGO_AVAILABLE = True
except ImportError:
    MONGO_AVAILABLE = False

class WebCrawler:
    def __init__(self, start_url, max_depth=2, max_pages=100, save_to_mongo=False, mongo_client=None):
        self.start_url = start_url
        self.max_depth = max_depth
        self.max_pages = min(max_pages, 50)  # Limit to 50 pages max on low memory
        self.visited = set()
        self.queue = deque([(start_url, 0, None)])  # (url, depth, parent_url)
        self.start_time = time.time()
        self.save_to_mongo = save_to_mongo and MONGO_AVAILABLE
        self.mongo_client = mongo_client
        self.db = None
        self.page_count = 0

        if self.save_to_mongo and mongo_client:
            self.db = mongo_client.crawler_db
            self.collection = self.db.crawled_pages

    def is_valid_url(self, url, base_domain):
        """Check if URL is valid and belongs to the same domain"""
        try:
            parsed = urlparse(url)
            base_parsed = urlparse(base_domain)
            return (
                parsed.scheme in ('http', 'https') and
                parsed.netloc == base_parsed.netloc and
                url not in self.visited
            )
        except:
            return False

    async def crawl_page(self, url, depth, session):
        """Crawl a single page and extract links"""
        try:
            async with session.get(url, timeout=10) as response:
                if response.status != 200:
                    return None, []

                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')

                # Extract title
                title = soup.find('title')
                title_text = title.string.strip() if title else url

                # Extract limited text content to save memory
                # Remove script and style elements
                for script in soup(['script', 'style', 'noscript']):
                    script.decompose()

                # Get text content (limit to first 5000 chars to save memory)
                text = soup.get_text()[:5000]
                # Clean up whitespace
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                full_text = ' '.join(chunk for chunk in chunks if chunk)[:5000]

                # Extract snippet
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                snippet = meta_desc.get('content', '')[:200] if meta_desc else ''

                # Extract text content for snippet if no meta description
                if not snippet:
                    # Use first 200 chars of full text
                    snippet = full_text[:200] if full_text else ''

                # Extract links (limit to 20 to save memory)
                links = []
                for link in soup.find_all('a', href=True)[:20]:
                    absolute_url = urljoin(url, link['href'])
                    if self.is_valid_url(absolute_url, self.start_url):
                        links.append(absolute_url)

                result = {
                    'title': title_text,
                    'text': full_text,
                    'snippet': snippet,
                    'links': links
                }

                # Clear soup to free memory
                del soup
                del html

                return result, links
        except Exception as e:
            print(f"Error crawling {url}: {e}")
            return None, []

    def _send_ws(self, ws, data):
        """Helper to send WebSocket data synchronously"""
        try:
            ws.send(json.dumps(data))
        except Exception as e:
            print(f"WebSocket send error: {e}")

    async def crawl(self, ws):
        """Main crawl loop with WebSocket updates"""
        async with aiohttp.ClientSession() as session:
            while self.queue and len(self.visited) < self.max_pages:
                url, depth, parent_url = self.queue.popleft()

                if url in self.visited or depth > self.max_depth:
                    continue

                self.visited.add(url)

                print(f"Crawling (depth {depth}): {url}")

                # Send crawling status
                self._send_ws(ws, {
                    'type': 'node',
                    'node': {
                        'url': url,
                        'depth': depth,
                        'status': 'crawling',
                        'parent': parent_url
                    }
                })

                # Crawl the page
                page_data, links = await self.crawl_page(url, depth, session)

                if page_data:
                    # Send completed status
                    self._send_ws(ws, {
                        'type': 'node',
                        'node': {
                            'url': url,
                            'depth': depth,
                            'status': 'completed',
                            'title': page_data['title'],
                            'linkCount': len(links),
                            'parent': parent_url
                        }
                    })

                    # Save to MongoDB if enabled
                    if self.save_to_mongo and self.collection is not None:
                        try:
                            # Check if URL already exists
                            existing = await self.collection.find_one({'url': url})
                            if existing:
                                # Silently skip - document already exists
                                pass
                            else:
                                # Insert new document
                                await self.collection.insert_one({
                                    'url': url,
                                    'title': page_data['title'],
                                    'text': page_data.get('text', ''),
                                    'snippet': page_data['snippet'],
                                    'depth': depth,
                                    'parent_url': parent_url,
                                    'link_count': len(links),
                                    'links': links[:50],
                                    'crawled_at': datetime.utcnow(),
                                    'start_url': self.start_url
                                })
                                print(f"✓ Saved to MongoDB: {url}")
                        except Exception as e:
                            print(f"MongoDB error for {url}: {e}")

                    # Add new links to queue (limit queue size)
                    for link in links:
                        if link not in self.visited and len(self.queue) < 100:
                            self.queue.append((link, depth + 1, url))

                    # Periodically clear old data to save memory
                    self.page_count += 1
                    if self.page_count % 10 == 0:
                        # Keep only recent visited URLs
                        if len(self.visited) > 100:
                            self.visited = set(list(self.visited)[-50:])
                else:
                    # Send error status
                    self._send_ws(ws, {
                        'type': 'node',
                        'node': {
                            'url': url,
                            'depth': depth,
                            'status': 'error',
                            'parent': parent_url
                        }
                    })

                # Send stats update
                duration = time.time() - self.start_time
                self._send_ws(ws, {
                    'type': 'stats',
                    'stats': {
                        'totalPages': len(self.visited),
                        'completedPages': len(self.visited),
                        'queueSize': len(self.queue),
                        'duration': duration,
                        'status': 'crawling'
                    }
                })

                # Small delay to prevent overwhelming
                await asyncio.sleep(0.1)

        # Send completion
        duration = time.time() - self.start_time
        self._send_ws(ws, {
            'type': 'complete',
            'stats': {
                'totalPages': len(self.visited),
                'completedPages': len(self.visited),
                'queueSize': 0,
                'duration': duration,
                'status': 'completed'
            }
        })

def setup_crawler_websocket(app):
    """Setup WebSocket endpoint for crawler"""
    sock = Sock(app)

    # Setup MongoDB connection if available
    mongo_client = None
    if MONGO_AVAILABLE:
        try:
            mongo_uri = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/')
            mongo_client = AsyncIOMotorClient(mongo_uri)
            print(f"✓ MongoDB connected: {mongo_uri}")
        except Exception as e:
            print(f"⚠ MongoDB connection failed: {e}")

    @sock.route('/ws/crawl')
    def crawl_websocket(ws):
        """WebSocket endpoint for real-time crawling"""
        try:
            # Wait for start message
            data = ws.receive()
            config = json.loads(data)

            if config.get('action') == 'start':
                start_url = config.get('url')
                max_depth = config.get('maxDepth', 2)
                max_pages = config.get('maxPages', 100)
                save_to_mongo = config.get('saveToMongo', False)

                print(f"Starting crawl: {start_url}, depth={max_depth}, pages={max_pages}")

                # Create and run crawler
                crawler = WebCrawler(
                    start_url,
                    max_depth,
                    max_pages,
                    save_to_mongo=save_to_mongo,
                    mongo_client=mongo_client
                )

                # Run async crawler in event loop
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(crawler.crawl(ws))
                finally:
                    loop.close()

        except Exception as e:
            print(f"Crawl error: {e}")
            import traceback
            traceback.print_exc()
            ws.send(json.dumps({
                'type': 'error',
                'message': str(e)
            }))

    return sock
