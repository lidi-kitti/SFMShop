import asyncio
import aiohttp
import time
import requests

async def fetch_url_async(url: str):
    """Асинхронный запрос к URL"""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                raise Exception(f"Failed to fetch URL: {response.status}")
            return await response.json()

async def main():
    url = "https://jsonplaceholder.typicode.com/posts/1"
    result = await fetch_url_async(url)
    print(result)

if __name__ == "__main__":
    asyncio.run(main())

async def fetch_multiple_urls_async(urls: list):
    """Параллельные запросы к нескольким URL"""
    # Твой код здесь
    tasks = [fetch_url_async(url) for url in urls]
    results = await asyncio.gather(*tasks)
    return results

def fetch_url_sync(url: str):
    """Синхронный запрос к URL"""
    with requests.get(url) as response:
        return response.json()

async def main():
    urls = [
        "https://jsonplaceholder.typicode.com/posts/1",
        "https://jsonplaceholder.typicode.com/posts/2",
        "https://jsonplaceholder.typicode.com/posts/3",
        "https://jsonplaceholder.typicode.com/posts/4",
        "https://jsonplaceholder.typicode.com/posts/5",
        "https://jsonplaceholder.typicode.com/posts/6",
        "https://jsonplaceholder.typicode.com/posts/7",
        "https://jsonplaceholder.typicode.com/posts/8",
        "https://jsonplaceholder.typicode.com/posts/9",
        "https://jsonplaceholder.typicode.com/posts/10"
        ]
    start_time_async = time.time()
    results_async = await fetch_multiple_urls_async(urls)
    end_time_async = time.time()
    start_time_sync = time.time()
    results_sync = [fetch_url_sync(url) for url in urls]
    end_time_sync = time.time()
    print(f"Time taken: {end_time_sync - start_time_sync} seconds")
    print(results_async)
    print(results_sync)
    if results_async == results_sync:
        print("Results are the same")
    else:
        print("Results are different")
        print("Difference: ", results_async/results_sync)
    print(f"Time taken async: {end_time_async - start_time_async} seconds")
    print(f"Time taken sync: {end_time_sync - start_time_sync} seconds")

if __name__ == "__main__":
    asyncio.run(main())