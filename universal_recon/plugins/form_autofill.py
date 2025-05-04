# universal_recon/plugins/form_autofill.py

import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select


def smart_fill_and_submit_forms(driver, config, logger, dry_run=False):
    forms = driver.find_elements(By.TAG_NAME, "form")
    logger(f"[FormHandler] Found {len(forms)} form(s)")

    filled_any = False

    for idx, form in enumerate(forms):
        logger(f"[FormHandler] Processing form #{idx}")
        try:
            inputs = form.find_elements(By.TAG_NAME, "input")
            selects = form.find_elements(By.TAG_NAME, "select")

            for inp in inputs:
                in_type = (inp.get_attribute("type") or "text").lower()
                in_name = (inp.get_attribute("name") or "").lower()
                in_placeholder = (inp.get_attribute("placeholder") or "").lower()

                fill_value = None
                if "name" in in_name or "name" in in_placeholder:
                    fill_value = "Test Name"
                elif "email" in in_name:
                    fill_value = "test@example.com"
                elif "city" in in_name:
                    fill_value = "Salt Lake City"
                elif "state" in in_name:
                    fill_value = "UT"
                elif in_type in ["text", "search"]:
                    fill_value = "TestValue"

                if fill_value and not dry_run:
                    try:
                        inp.clear()
                        inp.send_keys(fill_value)
                    except Exception as e:
                        logger(
                            f"[FormHandler] Could not type into input: {in_name} - {str(e)}",
                            "WARN",
                        )

            for sel in selects:
                try:
                    select_obj = Select(sel)
                    if len(select_obj.options) > 1 and not dry_run:
                        select_obj.select_by_index(1)
                except Exception as e:
                    logger(f"[FormHandler] Could not select dropdown option: {str(e)}", "WARN")

            if not dry_run:
                form.submit()
                logger(f"[FormHandler] Submitted form #{idx}")
                time.sleep(config.get("form_submission.form_wait_timeout", 3))

            filled_any = True

        except Exception as e:
            logger(f"[FormHandler] Error processing form #{idx}: {str(e)}", "ERROR")

    return filled_any
