# File name: update_exclusion_in_rules.py

# Python Version: 3.11.4
# Version: 2.0.0
# Description: Updates the exclusion parameter in a rulesets and their rules
#  Get the rule and ruleset hrefs from a csv file along with the href that needs the exclusion href that needs to be changed.
# It changes the exclusion value from false to true. 
# Stores when the update happens in updated_rules_and_rulesets.log
# Input name of file in variable filename.

import illumio
import getpass 

import datetime
from pandas import *

def update_rulesets():
    # Create a dictionary where each ruleset_href maps to a list of exclusion hrefs
    ruleset_to_exclusion_hrefs = {}

    # Add exclusion hrefs to each ruleset href 
    for ruleset_href, exclusion_href in zip(ruleset_data['href'], ruleset_data['exclude']):
        if ruleset_href not in ruleset_to_exclusion_hrefs:
            ruleset_to_exclusion_hrefs[ruleset_href] = []
        ruleset_to_exclusion_hrefs[ruleset_href].append(exclusion_href)

    # Process each ruleset_href and its associated exclusion hrefs
    for ruleset_href, exclusion_hrefs in ruleset_to_exclusion_hrefs.items():
        ruleset_response = pce.get(ruleset_href)

        if ruleset_response.status_code == 200:
            ruleset = ruleset_response.json()

            for scope in ruleset.get("scopes", []):
                for label_item in scope:
                    # Check if either label_group or label href matches any exclusion href
                    if label_item.get("label_group", {}).get("href") in exclusion_hrefs or label_item.get("label", {}).get("href") in exclusion_hrefs:
                        label_item["exclusion"] = True

            # Update the ruleset_request_body and log the changes
            ruleset_request_body = {"scopes": ruleset["scopes"]}

            with open(log_filename, "a") as log_file:
                try:
                    pce.put(ruleset_href, json=ruleset_request_body)
                    print(f"Ruleset {ruleset_href} updated successfully.")

                    # Write to log file
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    log_entry = f"{timestamp}: Updated ruleset: {ruleset_href} to set it to True.\n"
                    log_file.write(log_entry)
                except Exception as e:
                    print(f"Failed to update ruleset {ruleset_href}. Error: {e}")

# update exclusion parameter in rules
def update_rules():
    draft_rules_to_update = rule_data['rule_href'].tolist()

    # Extract the relevant part of the URL
    updated_rule_hrefs = [
        '/'.join(rule.split('/')[:1] + rule.split('/')[3:])
        for rule in draft_rules_to_update
    ]

    # Create a dictionary
    rules_to_exclusion_hrefs = {}

    # Add exclusion hrefs to each ruleset href 
    for rule_href, exclusion_hrefs in zip(updated_rule_hrefs, rule_data['exclude']):
        if rule_href not in rules_to_exclusion_hrefs:
            rules_to_exclusion_hrefs[rule_href] = []
        rules_to_exclusion_hrefs[rule_href].append(exclusion_hrefs)

    # Process each ruleset_href and its associated exclusion hrefs
    for rule_href, exclusion_hrefs in rules_to_exclusion_hrefs.items():
        rule_response = pce.get(rule_href)

        if rule_response.status_code == 200:
            rule = rule_response.json()

            for label_item in rule.get("consumers", []):
                # Check if either label_group or label href matches exclusion_href
                if label_item.get("label_group", {}).get("href") in exclusion_hrefs or label_item.get("label", {}).get("href") in exclusion_hrefs:
                    label_item["exclusion"] = True

            rule_request_body = {"consumers": rule["consumers"]}

            with open(log_filename, "a") as log_file:
                try:
                    pce.put(rule_href, json=rule_request_body)
                    print(f"Rule {rule_href} updated successfully.")

                    # Write to log file
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    log_entry = f"{timestamp}: Updated rule: {rule_href} to set it to True.\n"
                    log_file.write(log_entry)
                except Exception as e:
                    print(f"Failed to update rule {rule_href}. Error: {e}")


if __name__ == '__main__':

    # Change filename based on whether you want to update rulesets or rules
    filename = "testtest-rulesets 1.csv"

    pce = illumio.PolicyComputeEngine('pce-px07.cmhs.tmo', port=9443, org_id=1)

    api_key = getpass.getpass('API Key:')
    api_secret = getpass.getpass('API Secret:')

    pce.set_credentials(api_key, api_secret)
    pce.set_tls_settings(verify="C:\\Users\APrasad29\IllumioAutomation\cert\ca-bundle.pem")

    print("Check connection:", pce.check_connection())

    # Log file name
    log_filename = "updated_rules_and_rulesets.log"

    if "-rulesets" in filename:
        # Read the CSV file containing ruleset hrefs
        ruleset_data = read_csv(filename,usecols=['href', 'exclude'])
        print("Updating rulesets from", filename)
        update_rulesets()
    
    elif "-rules" in filename:
        # Read the CSV file containing rule hrefs
        rule_data = read_csv(filename,usecols=['rule_href', 'exclude'])
        print("Updating rules from", filename)
        update_rules()

    else:
        print("Please input a filename that has either has -rules or -rulesets in the name.")
