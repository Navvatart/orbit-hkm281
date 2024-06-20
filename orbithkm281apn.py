import requests
import os
import xml.etree.ElementTree as ET
import time

#developmet by Navvatart
#version 0.1

# Define modem IP address
modem_ip = "192.168.8.1"

# Fetch credentials from environment variables
username = os.getenv("MODEM_USERNAME", "admin")
password = os.getenv("MODEM_PASSWORD", "adminpondok02")

# Create a session to maintain cookies and authentication
session = requests.Session()

# URL for xml_action.cgi
xml_action_url = f"http://{modem_ip}/xml_action.cgi?method=set"

def get_request():
    try:
        # URL for the GET request
        url = f"http://{modem_ip}/login.cgi?Action=Digest&username=admin&realm=Highwmg&nonce=1000&response=4ddfc51d2d2f09ee91b7780baa5cd11a&qop=auth&cnonce=07aeb4878b875882&nc=00000004&temp=marvell&_={int(time.time())}"

        response = session.get(url)
        response.raise_for_status()  # Check if request was successful

        if response.status_code == 200:
            print("GET request successfully sent.")
            
            # Get response headers to use in the POST request
            response_headers = {
                "Authorization": response.headers.get("Authorization"),
                "Cookie": response.headers.get("Set-Cookie"),
            }

            # Send POST request with headers obtained from the GET response
            send_xml_request(response_headers)

        else:
            print(f"Error sending GET request: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Error sending GET request: {e}")

def send_xml_request(headers):
    try:
        # XML payload to be sent (example: retrieving profile info)
        xml_payload = """<?xml version="1.0" encoding="US-ASCII"?>
<RGW>
    <param>
        <method>call</method>
        <session>000</session>
        <obj_path>cm</obj_path>
        <obj_method>get_profile_info</obj_method>
    </param>
</RGW>"""

        headers["Content-Length"] = str(len(xml_payload))

        response = session.post(xml_action_url, data=xml_payload, headers=headers)
        response.raise_for_status()  # Check if request was successful

        if response.status_code == 200:
            try:
                root = ET.fromstring(response.text)

                # Extract and print relevant information from XML
                setting_response = root.find(".//setting_response")
                if setting_response is not None and setting_response.text == "OK":
                    print("Profile info retrieved successfully.")
                    return None

                active_profile = root.find(".//actived_profile1")
                profile_names = root.find(".//profile_names")

                if active_profile is not None:
                    active_profile = active_profile.text
                if profile_names is not None:
                    profile_names = profile_names.text

                print("\nProfile Information:")
                print(f"Active Profile: {active_profile}")
                print(f"Profile Names: {profile_names}")

                # Print list of profiles
                print("\nProfile List:")
                profiles = root.findall(".//profile_list/*")
                for profile in profiles:
                    profile_info = {child.tag: child.text for child in profile}
                    pdp_name = profile_info.get("pdp_name")
                    if pdp_name:
                        print(f"Profile Name: {pdp_name}")
                        print(f"APN: {profile_info.get('apn')}")
                        print(f"Dial Number: {profile_info.get('dial_number')}")
                        print(f"Username: {profile_info.get('username')}")
                        print(f"Password: {profile_info.get('password')}")
                        print(f"Authentication Type: {profile_info.get('authentication_type')}")
                        print("-----------------")

            except ET.ParseError as e:
                print(f"Error parsing XML: {e}")

        else:
            print(f"Error sending POST request: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Error sending POST request: {e}")

if __name__ == "__main__":
    # Send GET and POST requests
    get_request()
