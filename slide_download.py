from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor
import threading
from tqdm import tqdm
import time
import requests
import os
import re
import json
import img2pdf

def download_slide(args, max_retries=3, retry_delay=1):
    """Download a single slide with retry mechanism"""
    url, file_path = args
    for attempt in range(max_retries):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                return file_path
            elif response.status_code != 404:  # No retry for 404 errors
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            print(f"Download failed {url}: {e}")
    return None

def download_with_retry(tasks, max_workers=10):
    """Download using thread pool with retry mechanism"""
    successful_downloads = []
    failed_tasks = []
    
    # First round of downloads
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        print("\nFirst download round...")
        futures = list(tqdm(
            executor.map(download_slide, tasks),
            total=len(tasks),
            desc="Download Progress"
        ))
        
        # Collect results
        for i, result in enumerate(futures):
            if result:
                successful_downloads.append(result)
            else:
                failed_tasks.append(tasks[i])
    
    # Second round for failed tasks
    if failed_tasks:
        print(f"\n{len(failed_tasks)} files failed, starting second round...")
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = list(tqdm(
                executor.map(lambda x: download_slide(x, max_retries=5, retry_delay=2), 
                           failed_tasks),
                total=len(failed_tasks),
                desc="Retry Progress"
            ))
            
            successful_downloads.extend([f for f in futures if f is not None])
    
    return successful_downloads

def extract_presentation_id(url):
    """Extract presentation ID from URL"""
    match = re.search(r'/(\d+)/?', url)
    if match:
        return match.group(1)
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            match = re.search(r'https://s\.slideslive\.com/(\d+)/v3/slides\.json', response.text)
            if match:
                return match.group(1)
            
            match = re.search(r'https://ben\.slideslive\.com/player/(\d+)', response.text)
            if match:
                return match.group(1)
    except Exception as e:
        print(f"Error getting page content: {e}")
    
    return None

def download_slideslive_slides(url, output_dir=None):
    """
    Download SlidesLive presentation slides
    
    Args:
        url: SlidesLive URL
        output_dir: Output directory path, defaults to current directory
    """
    # Set output directory
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    else:
        output_dir = os.getcwd()
    
    print(f"Output directory: {output_dir}")
    
    # Extract presentation ID
    presentation_id = extract_presentation_id(url)
    if not presentation_id:
        print("Could not extract presentation ID")
        return False
    
    print(f"Presentation ID: {presentation_id}")
    
    # Build slides.json API URL
    api_url = f"https://s.slideslive.com/{presentation_id}/v3/slides.json"
    print(f"Accessing API: {api_url}")
    
    # Set headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'Referer': f'https://slideslive.com/{presentation_id}',
        'Origin': 'https://slideslive.com'
    }
    
    try:
        # Get slides information
        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            
            # Extract all slide information
            slides = []
            for item in data['slides']:
                if item['type'] == 'image' and 'image' in item:
                    slides.append({
                        'name': item['image']['name'],
                        'ext': item['image']['extname'],
                        'time': item['time']
                    })
            
            print(f"\nFound {len(slides)} slides")
            
            # Create temp directory
            temp_dir = os.path.join(output_dir, 'slides_temp')
            os.makedirs(temp_dir, exist_ok=True)
            
            # Prepare download tasks
            download_tasks = []
            for i, slide in enumerate(slides, 1):
                slide_url = f"https://rs.slideslive.com/{presentation_id}/slides/{slide['name']}{slide['ext']}?h=1080&f=webp"
                file_path = os.path.join(temp_dir, f'slide_{i:03d}.webp')
                download_tasks.append((slide_url, file_path))
            
            # Download with retry mechanism
            downloaded_slides = download_with_retry(download_tasks)
            
            print(f"\nSuccessfully downloaded {len(downloaded_slides)}/{len(slides)} slides")
            
            # Generate PDF
            if downloaded_slides:
                try:
                    print("\nGenerating PDF...")
                    pdf_path = os.path.join(output_dir, f'slides_{presentation_id}.pdf')
                    with open(pdf_path, 'wb') as f:
                        f.write(img2pdf.convert(sorted(downloaded_slides)))
                    print(f"PDF saved to: {pdf_path}")
                    
                    # Clean up temp files
                    for slide in downloaded_slides:
                        os.remove(slide)
                    os.rmdir(temp_dir)
                    print("Temporary files cleaned up")
                    
                except Exception as e:
                    print(f"Error generating PDF: {e}")
            
            return True
                
        else:
            print(f"API request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Error occurred: {e}")
        return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python slide_download.py <slideslive_url> [output_dir]")
        sys.exit(1)
    
    url = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    download_slideslive_slides(url, output_dir)