import requests
import os
import xml.etree.ElementTree as ET
import time
import random

# Tentukan alamat IP modem
modem_ip = "192.168.8.1"

# Ambil kredensial dari environment variables
username = os.getenv("MODEM_USERNAME", "admin")
password = os.getenv("MODEM_PASSWORD", "adminpondok02")

# Buat sesi untuk mempertahankan cookie dan autentikasi
session = requests.Session()

# URL untuk xml_action.cgi
xml_action_url = f"http://{modem_ip}/xml_action.cgi?method=set"

def get_request():
    try:
        # URL untuk permintaan GET
        url = f"http://{modem_ip}/login.cgi?Action=Digest&username=admin&realm=Highwmg&nonce=1000&response=4ddfc51d2d2f09ee91b7780baa5cd11a&qop=auth&cnonce=07aeb4878b875882&nc=00000004&temp=marvell&_={int(time.time())}"

        response = session.get(url)
        response.raise_for_status()  # Memeriksa jika permintaan berhasil

        if response.status_code == 200:
            print("Permintaan GET berhasil dikirim.")
            print("Response Headers:")
            #print(response.headers)
            
            # Ambil header respons untuk digunakan dalam permintaan POST
            response_headers = {
                "Authorization": response.headers.get("Authorization"),
                "Cookie": response.headers.get("Set-Cookie"),
            }

            # Kirim permintaan POST dengan header yang diambil dari respons GET
            send_xml_request(response_headers)

        else:
            print(f"Terjadi kesalahan saat melakukan permintaan GET: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Terjadi kesalahan saat melakukan permintaan GET: {e}")

def send_xml_request(headers):
    try:
        # XML payload yang akan dikirim (contoh: mendapatkan info profil)
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
        response.raise_for_status()  # Memeriksa jika permintaan berhasil

        if response.status_code == 200:
            try:
                root = ET.fromstring(response.text)

                # Ekstraksi dan cetak informasi yang relevan dari XML
                setting_response = root.find(".//setting_response")
                if setting_response is not None and setting_response.text == "OK":
                    print("Profil berhasil diubah.")
                    return None

                active_profile = root.find(".//actived_profile1")
                profile_names = root.find(".//profile_names")

                if active_profile is not None:
                    active_profile = active_profile.text
                if profile_names is not None:
                    profile_names = profile_names.text

                print("\nInformasi Profil:")
                print(f"Profil Aktif: {active_profile}")
                print(f"Nama Profil: {profile_names}")

                # Cetak daftar profil
                print("\nDaftar Profil:")
                profiles = root.findall(".//profile_list/*")
                
                valid_profiles = [
                    profile for profile in profiles 
                    if profile.find("pdp_name").text != active_profile 
                    and profile.find("pdp_name").text.lower() != "default"
                ]
                
                if valid_profiles:
                    selected_profile = random.choice(valid_profiles)
                    pdp_name = selected_profile.find("pdp_name").text
                    print(f"Mengganti profil Active ke: {pdp_name}")
                    switch_profile(headers, active_profile, pdp_name)
                else:
                    print("Tidak ada profil yang tersedia untuk diganti.")

            except ET.ParseError as e:
                print(f"Kesalahan saat parsing XML: {e}")

        else:
            print(f"Terjadi kesalahan saat mengirim permintaan POST: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Terjadi kesalahan saat mengirim permintaan POST: {e}")

def switch_profile(headers, active_profile, profile_name):
    try:
        # XML payload untuk melakukan switch_profile
        xml_payload = f"""<?xml version="1.0" encoding="US-ASCII"?>
<RGW>
    <param>
        <method>call</method>
        <session>000</session>
        <obj_path>cm</obj_path>
        <obj_method>set_wan_info</obj_method>
    </param>
    <wan>
        <profile_name>{profile_name}</profile_name>
        <wan_type>wan1</wan_type>
    </wan>
</RGW>"""

        headers["Content-Length"] = str(len(xml_payload))

        response = session.post(xml_action_url, data=xml_payload, headers=headers)
        response.raise_for_status()  # Memeriksa jika permintaan berhasil

        if response.status_code == 200:
            try:
                root = ET.fromstring(response.text)

                # Ekstraksi dan cetak informasi yang relevan dari XML
                setting_response = root.find(".//setting_response")
                if setting_response is not None and setting_response.text == "OK":
                    print(f"Switch profil berhasil dari {active_profile} ke {profile_name}.")
                    return None

                print(f"Gagal melakukan switch profil dari {active_profile} ke {profile_name}.")

            except ET.ParseError as e:
                print(f"Kesalahan saat parsing XML: {e}")

        else:
            print(f"Terjadi kesalahan saat mengirim permintaan POST untuk switch profil: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Terjadi kesalahan saat mengirim permintaan POST untuk switch profil: {e}")

if __name__ == "__main__":
    # Kirim permintaan GET dan POST
    get_request()
