#!/usr/bin/env python3
import requests
import time
import random
import datetime
from colorama import init, Fore, Style  # For colored terminal output
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

# Initialize colorama for colored output
init()

# Configuration parameters
max_iterations = 30       # Maximum number of attempts per URL
delay_between_requests = 3  # Seconds between requests to the same URL
delay_between_urls = 1      # Seconds between checking different URLs

# List of URLs to prime
urls_to_prime = [

]

# Track URLs that have been successfully cached
cached_urls = {url: False for url in urls_to_prime}

def add_cache_buster(url):
    """Add a cache-busting parameter to the URL"""
    cache_buster = random.randint(10000, 99999)
    parsed_url = urlparse(url)
    query_dict = parse_qs(parsed_url.query)
    query_dict['cache'] = [str(cache_buster)]
    
    # Rebuild the query string
    new_query = urlencode(query_dict, doseq=True)
    
    # Construct the new URL
    return urlunparse((
        parsed_url.scheme,
        parsed_url.netloc,
        parsed_url.path,
        parsed_url.params,
        new_query,
        parsed_url.fragment
    ))

def get_timestamp():
    """Get formatted current timestamp"""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Print header
print(f"{Fore.CYAN}Starting CDN cache priming for {len(urls_to_prime)} URLs...{Style.RESET_ALL}")
print(f"{Fore.CYAN}Press Ctrl+C to stop the script at any time.{Style.RESET_ALL}")
print(f"{Fore.CYAN}------------------------------------------------------------{Style.RESET_ALL}")

try:
    iteration = 1
    while (False in cached_urls.values()) and (iteration <= max_iterations):
        print(f"\n{Fore.CYAN}Iteration {iteration} of {max_iterations}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}------------------------------------------------------------{Style.RESET_ALL}")
        
        for url in urls_to_prime:
            # Skip already cached URLs
            if cached_urls[url]:
                continue
            
            try:
                # Add a cache-buster parameter
                priming_url = add_cache_buster(url)
                
                print(f"{Fore.LIGHTBLACK_EX}Priming - {url}{Style.RESET_ALL}")
                response = requests.head(priming_url, timeout=10)
                
                # Check if the URL is cached by Cloudflare
                is_cached = False
                status_message = "No cache indicators found"
                
                if "cf-cache-status" in response.headers:
                    cf_status = response.headers["cf-cache-status"]
                    status_message = f"Cloudflare cache - {cf_status}"
                    
                    if cf_status == "HIT":
                        is_cached = True
                
                # Display status
                timestamp = get_timestamp()
                iteration_info = f"[{iteration}/{max_iterations}]"
                
                if is_cached:
                    print(f"{Fore.GREEN}{timestamp} {iteration_info} ✓ {url} - {status_message}{Style.RESET_ALL}")
                    cached_urls[url] = True
                else:
                    print(f"{Fore.YELLOW}{timestamp} {iteration_info} ○ {url} - {status_message}{Style.RESET_ALL}")
            
            except Exception as e:
                print(f"{Fore.RED}Error when priming {url} - {str(e)}{Style.RESET_ALL}")
            
            # Pause between URLs
            time.sleep(delay_between_urls)
        
        # Count remaining uncached URLs
        remaining_urls = list(cached_urls.values()).count(False)
        print(f"\n{Fore.CYAN}Status - {len(urls_to_prime) - remaining_urls}/{len(urls_to_prime)} URLs cached{Style.RESET_ALL}")
        
        if remaining_urls == 0:
            print(f"{Fore.GREEN}All URLs are now cached! Priming successful.{Style.RESET_ALL}")
            break
        
        # Prepare for next iteration
        iteration += 1
        if iteration <= max_iterations:
            print(f"{Fore.LIGHTBLACK_EX}Waiting {delay_between_requests} seconds before next iteration...{Style.RESET_ALL}")
            time.sleep(delay_between_requests)
    
    # Final status report
    print(f"\n{Fore.CYAN}------------------------------------------------------------{Style.RESET_ALL}")
    print(f"{Fore.CYAN}CDN Cache Priming Results{Style.RESET_ALL}")
    print(f"{Fore.CYAN}------------------------------------------------------------{Style.RESET_ALL}")
    
    cached_count = 0
    for url, is_cached in sorted(cached_urls.items()):
        if is_cached:
            print(f"{Fore.GREEN}✓ {url} - Successfully cached{Style.RESET_ALL}")
            cached_count += 1
        else:
            print(f"{Fore.RED}✗ {url} - Not cached after {max_iterations} iterations{Style.RESET_ALL}")
    
    print(f"\n{Fore.CYAN}Summary - {cached_count} out of {len(urls_to_prime)} URLs cached successfully.{Style.RESET_ALL}")
    if iteration > max_iterations:
        print(f"{Fore.YELLOW}Reached maximum iterations ({max_iterations}) - some URLs remain uncached.{Style.RESET_ALL}")
    
    print(f"{Fore.CYAN}Script completed at {get_timestamp()}{Style.RESET_ALL}")

except KeyboardInterrupt:
    print(f"\n{Fore.YELLOW}Script interrupted by user.{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Script completed at {get_timestamp()}{Style.RESET_ALL}")

input(f"{Fore.CYAN}Press Enter to exit...{Style.RESET_ALL}")