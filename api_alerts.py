import asyncio
from datetime import datetime
import json
import os
from _utils import navigate_and_validate, switch_and_validate_panel




async def update_alert_details(page, form_container):

    has_edits = False
    print('Inf/Processing alert form modifications...')
    defTimeOut = os.getenv('DEFAULT_TIMEOUT')

    note_input = form_container.locator('input[aria-label="note"]')
    try:
        await note_input.click()
        await page.keyboard.press('Control+A')
        current_note = await note_input.input_value()
        if current_note and current_note.strip():
            await page.keyboard.press('Backspace')
            await note_input.fill('')
            print('Inf/`Note` needed to be cleared.')
            has_edits = True
        else:
            print("Inf/`Note` didn't needed to be cleared.")
    except Exception as e:
        print(f'WRN/Could not clear note: {e}')



    # # 2. Checkboxes to un-set
    # # We use partial text matching to handle the Shadow DOM labels
    # checkbox_labels = [
    #     "s****e@yahoo.com", 
    #     "Active trader pro", 
    #     "Fidelity app"
    # ]

    # for label in checkbox_labels:
    #     # Locate the checkbox component by the text in its label slot
    #     cb_host = page.locator('ap110932-checkbox, [fds-checkbox-control]').filter(has_text=label).first
    #     cb_input = cb_host.locator("input")

    #     # Check internal 'checked' state
    #     is_checked = await cb_input.is_checked()
        
    #     if is_checked:
    #         print(f"Inf/Un-setting checkbox: {label}")
    #         # Clicking the host component ensures internal Angular events fire
    #         await cb_host.click()
    #         has_edits = True
    #     else:
    #         print(f"Inf/Checkbox '{label}' is already un-set.")


    if not has_edits:
        print('Inf/No edits necessary, clicking `Cancel`...')
        save_button = form_container.locator('[fds-variant="primary"]').filter(has_text='Cancel')
        await save_button.first.click()
        await page.wait_for_timeout(defTimeOut)
        return True

    print('Inf/Clicking Save...')
    save_button = form_container.locator('[fds-variant="primary"]').filter(has_text='Save')    
    await page.wait_for_timeout(2000)
    await save_button.first.click()
    await page.wait_for_timeout(defTimeOut)
    await page.wait_for_timeout(2000)

    try:
        await page.locator('app-price-triggers-create').wait_for(state='hidden', timeout=defTimeOut)
        print('Inf/Alert saved successfully.')
        return True
    
    except Exception:
        print("ERR/Save failed or form timed out. Check for on-screen errors.")
        return False
##  update_alert_details()




async def modify_filtered_alerts(page, kwargs):

    search_button_selector = 'button[aria-label="Save"]'
    if not await navigate_and_validate(page, os.getenv("FIDELITY_ALERTS_PG"), search_button_selector):
        print("ERR/Aborting: Could not reach the Price Triggers page.")
        return

    search_box = 'input[aria-label="search for stock symbol"]'
    if not await switch_and_validate_panel(page, "Active alerts", search_box):
        print("ERR/Could not activate the `Active alerts` panel.")
        return

    print("Inf/Beginning alert modification loop...")
    symbol = kwargs.get("symbl")
    print(f"Inf/Filtering for symbol: {symbol}...")
    search_text_input_selector = 'input[aria-label="search for stock symbol"]'
    search_input = page.locator(search_text_input_selector).first
    await search_input.fill(symbol)
    search_button = page.locator('[fds-variant="secondary"]').filter(has_text="Search").first
    await search_button.click()
    print(f"Inf/Waiting for table to show results for {symbol}...")
    try:
        table_body = page.locator("tbody.fds-table__body")
        await table_body.get_by_text(symbol).first.wait_for(state="visible", timeout=10000)
    except Exception:
        print(f"WRN/Symbol {symbol} not found in table after search.")
        return
    print(f"Inf/awaiting filtered results.")


    data_rows = page.locator("tbody.fds-table__body tr.fds-table__row")
    try:
        await data_rows.first.wait_for(state="visible", timeout=10000)
    except:
        print(f"ERR/Timed out. No data rows found in the body for {symbol}.")
        return

    count = await data_rows.count()
    print(f"Inf/Confirmed {count} data row(s) for {symbol}.")

    for i in range(count):

        row_text = await data_rows.nth(i).inner_text()
        print(f"Inf/Row {i+1} content: {' | '.join(row_text.splitlines())}")

        edit_link = data_rows.nth(i).locator("ap110932-link").filter(has_text="Edit")
        
        print(f"Inf/Clicking Edit on row {i+1}...")
        await edit_link.click()
        
        print("Inf/Waiting for Edit Form to render...")
        edit_form_container = page.locator('app-price-triggers-create:visible').first

        try:
            await edit_form_container.wait_for(state="visible", timeout=10000)
            note_field = edit_form_container.locator('[formcontrolname="note"]')
            await note_field.wait_for(state="attached", timeout=5000)
            
            print("Inf/Edit form is open and visible.")
            await update_alert_details(page, edit_form_container)

        except Exception as e:
            print(f"ERR/Form failed to transition to visible: {e}")
        break #######################################################################################################################################

##  modify_filtered_alerts()






async def get_active_alerts(page):
    """
    Registers a network listener and triggers the 'Active Alerts' API call.
    """

    print("Inf/__GET_ACTIVE_ALERTS__")
    captured_alerts = []

    async def intercept_alerts(response):
        url = response.url
        # Target the specific AlertsCenter API
        if "AlertsCenter/getTriggers" in url and response.status == 200:
            try:
                data = await response.json()
                captured_alerts.append({
                    "url": url
                    , "payload": data
                })
                print(f"Inf/>>> SUCCESS: Captured {url.split('status=')[1].split('&')[0]} alerts.")
            except Exception as e:
                print(f"ERR/!!! JSON Parse Error: {e}")

    page.on("response", intercept_alerts)

    print("Inf/Navigating to Price Triggers...")
    await page.goto(
        os.getenv("FIDELITY_ALERTS_PG")
        , wait_until="domcontentloaded"
    )

    try:
        active_tab = page.locator("#ACTIVE")
        await active_tab.wait_for(state="visible", timeout=os.getenv("DEFAULT_TIMEOUT"))
        await active_tab.click()
    except Exception:
        print("ERR/Active tab already selected or not found.")
    
    await asyncio.sleep(5)
    page.remove_listener("response", intercept_alerts)

    dtNow= datetime.now()
    fil= f'{os.getenv("DATA_OUTPUT_DIR")}/alerts_{dtNow.strftime("%Y%m%d")}_{dtNow.strftime("%H%M%S")}.json'
    if captured_alerts:
        with open(fil, "w") as f:
            json.dump(captured_alerts, f, indent=4)
        print(f"Inf/Done. Saved to active_alerts.json")

        page.remove_listener("response", intercept_alerts)
        return len(captured_alerts) > 0

    return -1

## get_active_alerts()

