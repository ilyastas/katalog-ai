#!/usr/bin/env python3
"""
IndexNow submission script for ALIE Platform
Automatically submits updated URLs to IndexNow API
Author: ALIE Platform
Date: 2026-03-05
"""

import json
import requests
import logging
from datetime import datetime
from pathlib import Path
import xml.etree.ElementTree as ET
import hashlib

# ============================================================================
# Configuration
# ============================================================================

INDEXNOW_API_URL = "https://api.indexnow.org/indexnow"
DOMAIN = "ilyastas.github.io"
DOMAIN_CATALOG = "ilyastas.github.io/katalog-ai"
SITEMAP_PATH = Path(__file__).parent.parent / "sitemap.xml"
INDEXNOW_KEY_FILE = Path(__file__).parent.parent / "indexnow.txt"
LOG_FILE = Path(__file__).parent.parent / "logs" / "indexnow_submissions.log"

# ============================================================================
# Logging Setup
# ============================================================================

LOG_FILE.parent.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# ============================================================================
# Functions
# ============================================================================

def read_indexnow_key() -> str:
    """Read IndexNow key from indexnow.txt file"""
    try:
        with open(INDEXNOW_KEY_FILE, 'r', encoding='utf-8') as f:
            key = f.read().strip()
        if not key or len(key) < 32:
            raise ValueError("Invalid IndexNow key format")
        logger.info(f"✓ IndexNow key loaded: {key[:8]}...")
        return key
    except FileNotFoundError:
        logger.error(f"✗ IndexNow key file not found: {INDEXNOW_KEY_FILE}")
        raise
    except Exception as e:
        logger.error(f"✗ Error reading IndexNow key: {e}")
        raise

def parse_sitemap() -> list:
    """Parse sitemap.xml and extract all URLs"""
    urls = []
    try:
        tree = ET.parse(SITEMAP_PATH)
        root = tree.getroot()
        
        # Handle XML namespace
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        
        for url_elem in root.findall('ns:url', namespace):
            loc = url_elem.find('ns:loc', namespace)
            if loc is not None and loc.text:
                urls.append(loc.text)
        
        logger.info(f"✓ Parsed {len(urls)} URLs from sitemap.xml")
        return urls
    except Exception as e:
        logger.error(f"✗ Error parsing sitemap.xml: {e}")
        raise

def submit_to_indexnow(key: str, urls: list) -> dict:
    """Submit URLs to IndexNow API"""
    
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "ALIE-Platform/1.0"
    }
    
    payload = {
        "host": DOMAIN,
        "key": key,
        "keyLocation": f"https://{DOMAIN_CATALOG}/indexnow.txt",
        "urlList": urls[:10000]  # IndexNow limit is 10,000 URLs per request
    }
    
    try:
        logger.info(f"→ Submitting {len(payload['urlList'])} URLs to IndexNow...")
        response = requests.post(
            INDEXNOW_API_URL,
            json=payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code in [200, 202]:
            logger.info(f"✓ SUCCESS: IndexNow API accepted submission (HTTP {response.status_code})")
            return {
                "status": "success",
                "code": response.status_code,
                "urls_submitted": len(payload['urlList']),
                "timestamp": datetime.now().isoformat()
            }
        else:
            logger.warning(f"⚠ API returned HTTP {response.status_code}")
            logger.warning(f"Response: {response.text[:200]}")
            return {
                "status": "warning",
                "code": response.status_code,
                "urls_submitted": len(payload['urlList']),
                "error": response.text[:200],
                "timestamp": datetime.now().isoformat()
            }
    
    except requests.exceptions.RequestException as e:
        logger.error(f"✗ Network error submitting to IndexNow: {e}")
        return {
            "status": "error",
            "error": str(e),
            "urls_submitted": 0,
            "timestamp": datetime.now().isoformat()
        }

def submit_incremental(key: str, urls: list) -> dict:
    """
    Submit URLs in batches (for large sitemaps)
    IndexNow allows up to 10,000 URLs per request
    """
    
    batch_size = 10000
    results = []
    
    for i in range(0, len(urls), batch_size):
        batch = urls[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (len(urls) + batch_size - 1) // batch_size
        
        logger.info(f"\n→ Batch {batch_num}/{total_batches} ({len(batch)} URLs)")
        result = submit_to_indexnow(key, batch)
        results.append(result)
        
        if result["status"] != "success":
            logger.warning(f"⚠ Batch {batch_num} had issues, continuing...")
    
    # Summary
    total_submitted = sum(r.get("urls_submitted", 0) for r in results)
    return {
        "status": "completed",
        "batches": len(results),
        "total_urls_submitted": total_submitted,
        "results": results,
        "timestamp": datetime.now().isoformat()
    }

def generate_report(result: dict) -> str:
    """Generate submission report"""
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    report = f"""
╔══════════════════════════════════════════════════════════════╗
║          IndexNow Submission Report                          ║
╚══════════════════════════════════════════════════════════════╝

📅 Timestamp: {timestamp}
🔗 Domain: {DOMAIN_CATALOG}
📍 API: {INDEXNOW_API_URL}

Results:
────────────────────────────────────────────────────────────────
"""
    
    if result.get("batches"):
        report += f"Batches processed: {result['batches']}\n"
        report += f"Total URLs submitted: {result['total_urls_submitted']}\n"
        
        for i, batch_result in enumerate(result.get("results", []), 1):
            report += f"\n  Batch {i}:\n"
            report += f"    Status: {batch_result.get('status', 'unknown')}\n"
            report += f"    HTTP Code: {batch_result.get('code', 'N/A')}\n"
            report += f"    URLs: {batch_result.get('urls_submitted', 0)}\n"
    else:
        report += f"Status: {result.get('status', 'unknown')}\n"
        report += f"URLs submitted: {result.get('urls_submitted', 0)}\n"
        report += f"HTTP Code: {result.get('code', 'N/A')}\n"
    
    if result.get("error"):
        report += f"\n⚠ Error: {result['error']}\n"
    
    report += "\n" + "="*62 + "\n"
    
    return report

# ============================================================================
# Main
# ============================================================================

def main():
    """Main execution function"""
    
    logger.info("="*62)
    logger.info("IndexNow Submission Script Started")
    logger.info("="*62)
    
    try:
        # Step 1: Read IndexNow key
        key = read_indexnow_key()
        
        # Step 2: Parse sitemap
        urls = parse_sitemap()
        
        if not urls:
            logger.warning("⚠ No URLs found in sitemap!")
            return
        
        # Step 3: Submit to IndexNow
        logger.info(f"\n→ Starting IndexNow submission for {len(urls)} URLs...")
        result = submit_incremental(key, urls)
        
        # Step 4: Generate and display report
        report = generate_report(result)
        logger.info(report)
        
        # Step 5: Save report
        report_file = Path(__file__).parent.parent / "logs" / f"indexnow_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        report_file.parent.mkdir(exist_ok=True)
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        logger.info(f"📄 Report saved to: {report_file}")
        
    except Exception as e:
        logger.error(f"\n✗ FATAL ERROR: {e}")
        logger.error("Script execution failed!")
        raise

if __name__ == "__main__":
    main()
