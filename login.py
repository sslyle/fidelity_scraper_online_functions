import asyncio

async def login_to_fidelity(page, username, password) -> bool:
    """
    Handles navigation to the login page and waits for the user 
    to manually complete the login and MFA process.
    """
    try:
        # 1. Attempt to bypass if session is already alive
        print("Checking for existing session...")
        await page.goto(
            "https://digital.fidelity.com/ftgw/digital/portfolio/summary"
            , wait_until="domcontentloaded"
        )
        
        if "portfolio/summary" in page.url:
            print("Successfully restored session from cookies.")
            #return True

        # 2. Redirect to Login Page for manual entry
        print("\n" + "="*50)
        print("ACTION REQUIRED: Manual Login & MFA")
        print("Please enter your credentials and MFA code in the browser window.")
        print("="*50 + "\n")
        
        await page.goto("https://digital.fidelity.com/prgw/digital/login/full-page")

        # 3. Wait for the 'Summary' page to appear (indicates success)
        # We give you 2 minutes (120000ms) to find your phone and type the code
        try:
            await page.wait_for_url(
                "**/portfolio/summary"
                , timeout=120000 
            )
            print("Login success detected! Proceeding with automation...")
            return True
        except Exception:
            print("Timed out waiting for manual login.")
            return False
            
    except Exception as e:
        print(f"Navigation error: {e}")
        return False