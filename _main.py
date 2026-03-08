import asyncio
import os
import sys
from dotenv import load_dotenv
from playwright.async_api import async_playwright
from _utils import connect_to_browser
from api_alerts import get_active_alerts, modify_filtered_alerts

load_dotenv()


async def run(cmd, kwargs):

    async with async_playwright() as p:

        page= await connect_to_browser(p)    

        print(f"Inf/Running command `{cmd}`")
        if cmd == 'FETCH_ALERTS':
            await get_active_alerts(page)
            print("Inf/__end__GET_ACTIVE_ALERTS__")

        if cmd == 'EDIT_ALERT':
            await modify_filtered_alerts(page, kwargs)
            print("Inf/__end__EDIT_ALERT__")

        symbols = ["ORCL"]
        for ticker in symbols:
            #await download_historical_data(page, ticker)
            pass

        # IMPORTANT: Do NOT call context.close() or you will kill your manual browser
        print("Inf/Automation complete. Disconnecting...")
## run()


 


if __name__ == "__main__":

    #print('CHROME_DEBUG_URL', os.getenv('CHROME_DEBUG_URL'))
    #print('CHROME_USER_DATA', os.getenv('CHROME_USER_DATA'))
    #print('DATA_OUTPUT_DIR', os.getenv('DATA_OUTPUT_DIR'))
    #print('DEFAULT_TIMEOUT', os.getenv('DEFAULT_TIMEOUT'))
    #print('EXECUTION_MODE', os.getenv('EXECUTION_MODE'))

    if len(sys.argv) < 2:
        print("Usage: python _main.py <command> [<k1=v1 k2=v2 ...>]")
        sys.exit(1)

    cmd = sys.argv[1]
    kwargs = {}

    for arg in sys.argv[2:]:
        if '=' in arg:
            key, value = arg.lstrip('-').split('=', 1)
            kwargs[key] = value
    
    asyncio.run(run(cmd, kwargs)) ## asyncio.run() calls a FUNCTION which it is going to run.