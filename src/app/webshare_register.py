#!/usr/bin/env python3
"""
WEBSHARE BULK REGISTRATION
- Daftar via Google OAuth
- 12 email = 120 proxy
"""

import asyncio
import json
import subprocess
from pathlib import Path
from playwright.async_api import async_playwright

EMAILS = [
    "al7795927",
    "andrajaelani28", 
    "herasyun",
    "herdinuralam7",
    "kadirapan2",
    "kindlykiun",
    # "lanayusep8",  # sudah terdaftar
    "lemesbesti74",
    "linaabut4",
    "luluqiqi91",
    "lulurindu4",
    "nugrahadavid328",
    "yusupanugrah147",
]

OUTPUT_FILE = Path.home() / ".hermes" / "webshare_accounts.json"

async def register_with_google(email_name):
    """Register 1 akun Webshare via Google OAuth"""
    print(f"\n📧 [{email_name}] Starting...")
    
    # Switch Google account
    subprocess.run(["google-switch", email_name], capture_output=True)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={"width": 1280, "height": 800})
        page = await context.new_page()
        
        try:
            # Go to Webshare signup
            await page.goto("https://proxy2.webshare.io/register", timeout=30000)
            await page.wait_for_timeout(3000)
            
            # Click "Sign up with Google"
            google_btn = page.locator('button:has-text("Google"), a:has-text("Google")').first
            await google_btn.click(timeout=10000)
            await page.wait_for_timeout(5000)
            
            # Handle Google OAuth popup/redirect
            # Wait for redirect back to Webshare dashboard
            await page.wait_for_url("**/dashboard**", timeout=60000)
            
            print(f"  ✅ [{email_name}] Registered!")
            
            # Go to proxy list to get credentials
            await page.goto("https://proxy2.webshare.io/proxy/list", timeout=30000)
            await page.wait_for_timeout(3000)
            
            # Extract credentials from page
            # (akan di-screenshot untuk manual extract)
            await page.screenshot(path=f"/tmp/webshare_{email_name}.png")
            print(f"  📸 Screenshot saved: /tmp/webshare_{email_name}.png")
            
            result = {
                "email": f"{email_name}@gmail.com",
                "status": "registered",
                "screenshot": f"/tmp/webshare_{email_name}.png"
            }
            
            await browser.close()
            return result
            
        except Exception as e:
            print(f"  ❌ [{email_name}] Error: {str(e)[:50]}")
            await page.screenshot(path=f"/tmp/webshare_{email_name}_error.png")
            await browser.close()
            return {"email": f"{email_name}@gmail.com", "status": "error", "error": str(e)[:100]}

async def register_all():
    """Register semua email"""
    results = []
    
    for email in EMAILS:
        result = await register_with_google(email)
        results.append(result)
        await asyncio.sleep(10)  # delay antar registrasi
    
    # Save results
    OUTPUT_FILE.write_text(json.dumps(results, indent=2))
    
    # Summary
    success = sum(1 for r in results if r["status"] == "registered")
    print(f"\n{'='*50}")
    print(f"✅ Registered: {success}/{len(EMAILS)}")
    print(f"📁 Results: {OUTPUT_FILE}")
    print(f"{'='*50}")

if __name__ == "__main__":
    print("🚀 WEBSHARE BULK REGISTRATION")
    print(f"📧 Emails: {len(EMAILS)}")
    asyncio.run(register_all())
