import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # show browser window
        page = await browser.new_page()
        await page.goto("https://bbc.com", wait_until="domcontentloaded")
        await page.wait_for_selector("body")  # wait for a reliable element to appear
        print(await page.title())
        await page.screenshot(path="screenshot.png", full_page=True)
        await browser.close()

asyncio.run(main())
