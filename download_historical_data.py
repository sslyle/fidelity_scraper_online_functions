import asyncio

async def download_historical_data(page, symbol):
    """
    Configures the chart table for a 6M/Daily view and downloads the CSV.
    """

    print(f"Navigating to Research Dashboard for {symbol}...")
    await page.goto(
        "https://digital.fidelity.com/prgw/digital/research/quote/dashboard/summary?symbol={symbol}"
        , wait_until="domcontentloaded"
    )

    # Enable Table View if not active
    table_toggle = page.locator("#table-view-item")
    if await table_toggle.get_attribute("aria-checked") == "false":
        print("Enabling Table View...")
        await table_toggle.click()

    # Configure 6M/Daily settings
    print("Setting Timeframe to 6 Months...")
    await page.locator("#tf_6M").click()
    print("Ensuring Frequency is set to Daily...")
    freq_dropdown = page.locator('.ace-frequency .ace-dropdown-menu[aria-label="Frequency"]')
    await freq_dropdown.click()
    await page.locator('.ace-frequency .ace-dropdown-items li:has-text("Daily")').click()

    print("Triggering Download...")
    try:
        async with page.expect_download(timeout=10000) as download_info:
            await page.locator("#table-download").click()
        
        download = await download_info.value
        save_path = f"{symbol}_6M_Daily_Historical.csv"
        await download.save_as(save_path)
        print(f"SUCCESS: {symbol} data saved to {save_path}")
        return True
    except Exception:
        return False