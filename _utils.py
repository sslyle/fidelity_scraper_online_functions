import os
from dotenv import load_dotenv

load_dotenv()


async def switch_and_validate_panel(page, panel_substring, validation_selector):
    """
    Clicks a panel tab using a partial match (ignoring dynamic counts) 
    and validates the panel change.
    
    :param panel_substring: e.g., "Active alerts" (will match "Active alerts (158)")
    """
    print(f"Inf/Checking status of panel containing `{panel_substring}`...")


    if await page.locator(validation_selector).first.is_visible():
        print(f"Inf/Panel for `{panel_substring}` is already active.")
        return True

    try:
        tab = page.get_by_text(panel_substring, exact=False).first    
        print(f"Inf/Clicking tab matching `{panel_substring}`...")
        await tab.click()

        locator = page.locator(validation_selector).first
        try:
            await locator.wait_for(state="attached", timeout=10000)
            await locator.wait_for(state="visible", timeout=5000)
            
            print("Inf/Validation element found and visible.")
            await page.wait_for_timeout(500)
    
            print(f"Inf/Panel `{panel_substring}` is now active.")
            return True
        except Exception as e:
            print(f"ERR/Validation failed after click: {e}")
            return False
        
    except Exception as e:
        print(f"ERR/Failed to switch to `{panel_substring}`: {e}")
        return False

##  switch_and_validate_panel()
    



async def navigate_and_validate(page, target_url, validation_selector):
    """
    Navigates to a URL and waits for a specific element to ensure the page is ready.

    :param page: The Playwright page object
    :param target_url: The destination URL (e.g., FIDELITY_ALERTS_PG)
    :param validation_selector: A CSS/Aria selector unique to the target page
    """

    if target_url in page.url:
        print(f"Inf/Already on target page: {page.url}")
        
        # Verify the validation element is actually visible before skipping
        if await page.locator(validation_selector).first.is_visible():
            print(f"Inf/Validation element '{validation_selector}' is visible. Skipping navigation.")
            return True
        else:
            print("Inf/Target URL matches but validation element missing. Proceeding with navigation.")

    print(f"Inf/Initiating navigation to: {target_url}")
    
    try:
        await page.evaluate(lambda url: exec(f"window.location.href = '{url}'"), target_url)
        # If lambda exec fails, use this more standard anonymous function:
        # await page.evaluate("url => { window.location.href = url }", target_url)
        print("Inf/Waiting for browser to acknowledge URL change...")
        await page.wait_for_function("() => window.location.href.includes('fidelity.com')")

        print(f"Inf/Waiting for validation element: {validation_selector}")
        locator = page.locator(validation_selector).first
        await locator.wait_for(state="visible", timeout=int(os.getenv("DEFAULT_TIMEOUT", 30000)))
        print("Inf/Navigation and validation successful.")
        return True
        
    except Exception as e:
        print(f"ERR/Navigation failed: {e}")
        # Fallback to standard navigation if JS injection is completely blocked by CSP
        try:
            print("Inf/Attempting fallback standard navigation...")
            await page.goto(target_url, wait_until="load", timeout=15000)
            return True
        except:
            print(f"ERR/Navigation failed: {e}")
            return False
##  navigate_and_validate()        



async def connect_to_browser(p):
        print("Inf/Connecting to your existing Chrome instance...")
        try:
            browser = await p.chromium.connect_over_cdp(os.getenv("CHROME_DEBUG_URL"))
            context = browser.contexts[0]
            page = context.pages[0]
            print(f"Inf/Connected to Chrome. Current page URL: {page.url}")
            return page
        except Exception as e:
            print(f"ERR/Error occurred while connecting to Chrome: {e}")
            exit(1)
            
##  connect_to_browser()
