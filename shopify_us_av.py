import requests
import json
import csv

#Enter your Shopify hostname, Shopify Private app API key and Password, and your Lob Live Environment API Key.
shopify_hostname = "example.myshopify.com"
shopify_api_key = "Shopify_Private_app_API_key"
shopify_password = "Shopify_Private_app_Password"
lob_api_key = "Lob_Live_Environment_API_Key"

shopify_url = "https://" + shopify_api_key + ":" + shopify_password + "@" + shopify_hostname + "/admin/api/2019-07/orders.json?limit=250&fulfillment_status=unshipped"
shopify_response = requests.request("GET", shopify_url).json()
lob_url = "https://" + lob_api_key + ":@api.lob.com/v1/us_verifications"

def deliverability_analysis(response):
    dpv_confirmation = response["deliverability_analysis"]["dpv_confirmation"]
    if dpv_confirmation == "Y":
        return "The address is deliverable by the USPS."
    elif dpv_confirmation == "S":
        return "The address is deliverable by removing the provided secondary unit designator. This information may be incorrect or unnecessary."
    elif dpv_confirmation == "D":
        return "The address is deliverable to the building's default address but is missing a secondary unit designator and/or number. There is a chance the mail will not reach the intended recipient."
    elif dpv_confirmation == "N":
        return "The address is not deliverable according to the USPS, but parts of the address are valid (such as the street and ZIP code)."
    elif dpv_confirmation == "":
        return "This address is not deliverable. No matching street could be found within the city or ZIP code."

deliverability_list = [["created_at", "order_id", "deliverability", "recipient", "primary_line", "last_line", "deliverability_analysis"]]

for i in range(0, len(shopify_response["orders"])):
    order_id = shopify_response["orders"][i]["id"]
    created_at = shopify_response["orders"][i]["created_at"]
    recipient = shopify_response["orders"][i]["shipping_address"]["name"]
    primary_line = shopify_response["orders"][i]["shipping_address"]["address1"]
    secondary_line = shopify_response["orders"][i]["shipping_address"]["address2"]
    city = shopify_response["orders"][i]["shipping_address"]["city"]
    state = shopify_response["orders"][i]["shipping_address"]["province"]
    zip_code = shopify_response["orders"][i]["shipping_address"]["zip"]

    address = {
        "recipient": recipient,
        "primary_line": primary_line,
        "secondary_line": secondary_line,
        "city": city,
        "state": state,
        "zip_code": zip_code
    }

    try:
        lob_response_status = requests.request("POST", lob_url, data = json.dumps(address), headers = {"Content-Type": "application/json"})
        lob_response = lob_response_status.json()
        if lob_response["deliverability"] != "deliverable":
            tmp_list = [created_at, order_id, lob_response["deliverability"], lob_response["recipient"], lob_response["primary_line"], lob_response["last_line"], deliverability_analysis(lob_response)]
            deliverability_list.append(tmp_list)
    except:
        print(lob_response_status)

with open('lob_address_verification.csv', 'w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    for row in deliverability_list:
        csv_writer.writerow(row)
