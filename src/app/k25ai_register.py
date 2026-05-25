#!/usr/bin/env python3
"""
K25.AI EARLY ACCESS AUTOMATION v2
- Fixed: modal auto-opens
- Error handling & retry
"""

import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright

EMAILS = [
    "al7795927@gmail.com",
    "andrajaelani28@gmail.com",
    "herasyun@gmail.com",
    "herdinuralam7@gmail.com",
    "kadirapan2@gmail.com",
    "kindlykiun@gmail.com",
    "lanayusep8@gmail.com",
    "lemesbesti74@gmail.com",
    "linaabut4@gmail.com",
    "luluqiqi91@gmail.com",
    "lulurindu4@gmail.com",
    "nugrahadavid328@gmail.com",
]

OUTPUT = Path.home() / ".hermes" / "k25ai" / "registrations.json"

async def register(email, idx):
    print(f"\n[{idx+1}/12] {email}")
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            await page.goto("https://k25.ai/", timeout=30000)
            await page.wait_for_timeout(3000)
            
            # Fill email (modal auto-opens)
            await page.fill('input[placeholder*="email"], input[type="email"]', email, timeout=10000)
            await page.wait_for_timeout(500)
            
            # Submit
            await page.click('button:has-text("Join"), button:has-text("Waitlist")', timeout=10000)
            await page.wait_for_timeout(3000)
            
            # Check for error
            error = await page.locator('text=/something went wrong/i, text=/error/i').count()
            
            if error > 0:
                print(f"  ⚠️ Error detected")
                await page.screenshot(path=f"/tmp/k25_{idx}_error.png")
                await browser.close()
                return {"email": email, "status": "error", "message": "Something went wrong"}
            
            # Check for success
            success = await page.locator('text=/thank/i, text=/success/i, text=/joined/i').count()
            
            if success > 0:
                print(f"  ✅ Success!")
                await browser.close()
                return {"email": email, "status": "success"}
            
            # Unknown state
            await page.screenshot(path=f"/tmp/k25_{idx}_unknown.png")
            print(f"  ❓ Unknown state")
            await browser.close()
            return {"email": email, "status": "unknown"}
            
    except Exception as e:
        print(f"  ❌ Exception: {str(e)[:40]}")
        return {"email": email, "status": "error", "error": str(e)[:100]}

async def main():
    results = []
    
    for i, email in enumerate(EMAILS):
        result = await register(email, i)
        results.append(result)
        await asyncio.sleep(10)  # delay antar akun
    
    # Save
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(results, indent=2))
    
    success = sum(1 for r in results if r["status"] == "success")
    errors = sum(1 for r in results if r["status"] == "error")
    print(f"\n{'='*50}")
    print(f"✅ Success: {success}/12")
    print(f"❌ Errors: {errors}/12")
    print(f"📁 Saved: {OUTPUT}")
    print(f"{'='*50}")

if __name__ == "__main__":
    print("🚀 K25.AI EARLY ACCESS REGISTRATION v2")
    asyncio.run(main())
