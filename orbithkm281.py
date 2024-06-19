import requests
import os
import xml.etree.ElementTree as ET

# Tentukan alamat IP modem
modem_ip = "192.168.8.1"

# Ambil kredensial dari environment variables
username = os.getenv("MODEM_USERNAME", "admin")
password = os.getenv("MODEM_PASSWORD", "adminpondok02")

# Buat sesi untuk mempertahankan cookie dan autentikasi
session = requests.Session()

# URL untuk login
login_url = f"http://{modem_ip}/login.cgi"

# URL untuk xml_action.cgi
xml_action_url = f"http://{modem_ip}/xml_action.cgi?method=set"

# Headers untuk permintaan HTTP
headers = {
    "Accept": "application/xml, text/xml, */*; q=0.01",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en-US,en;q=0.9,id;q=0.8",
    "Authorization": 'Digest username="", realm="undefined", nonce="undefined", uri="/cgi/xml_action.cgi", response="d5717734796dde8e89333b24391b8b7c", qop=undefined, nc=00000074, cnonce="9131e3918bf474e1"',
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Content-Length": "175",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Cookie": "CGISID=Vgtpyq5SFpWpdEOjT6e5iqaQYZt1jyaeRuvhLr9iG8wUE; username=YWRtaW4=; password=YWRtaW5wb25kb2swMg==; projectConfig=%5Bobject%20Object%5D",
    "Host": "192.168.8.1",
    "Origin": "http://192.168.8.1",
    "Pragma": "no-cache",
    "Referer": "http://192.168.8.1/index.html",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",
    "X-Requested-With": "XMLHttpRequest",
    "csrftoken": "hfiehifejfklihefiuehflejhfueihfeuihfeui"
}

def login():
    login_payload = {
        "username": username,
        "password": password,
    }

    try:
        response = session.post(login_url, data=login_payload, headers=headers)
        response.raise_for_status()  # Memeriksa jika permintaan berhasil

        if "Login failed" not in response.text:
            print("Login berhasil")
            return True
        else:
            print("Login gagal. Periksa kembali kredensial Anda.")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Terjadi kesalahan saat melakukan login: {e}")
        return False

def post_xml_action(xml_payload):
    try:
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

               # print("\nDaftar Profil:")
                profiles = root.findall(".//profile_list/*")
                profile_info_list = []
                for profile in profiles:
                    profile_info = {child.tag: child.text for child in profile}
                    profile_info_list.append(profile_info)
                   # print(f"\nProfil {profile_info.get('profile_index', 'Unknown')}:")
                   # for key, value in profile_info.items():
                       # print(f"{key}: {value}")

                return profile_info_list, active_profile  # Mengembalikan daftar profil dan profil aktif untuk referensi

            except ET.ParseError as e:
                print(f"Kesalahan saat parsing XML: {e}")
        else:
            print(f"Terjadi kesalahan saat mengirim permintaan XML: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Terjadi kesalahan saat mengirim permintaan XML: {e}")

def switch_profile(profile_name, wan_type="wan1"):
    if not profile_name:
        print("Nama profil kosong, tidak dapat mengubah profil.")
        return

    xml_payload_switch_profile = f"""<?xml version="1.0" encoding="US-ASCII"?>
<RGW>
    <param>
        <method>call</method>
        <session>000</session>
        <obj_path>cm</obj_path>
        <obj_method>set_wan_info</obj_method>
    </param>
    <wan>
        <profile_name>{profile_name}</profile_name>
        <wan_type>{wan_type}</wan_type>
    </wan>
</RGW>"""
    post_xml_action(xml_payload_switch_profile)

# Logika utama skrip
if login():
    # Permintaan XML untuk mendapatkan info profil
    xml_payload_profile_info = """<?xml version="1.0" encoding="US-ASCII"?>
<RGW>
    <param>
        <method>call</method>
        <session>000</session>
        <obj_path>cm</obj_path>
        <obj_method>get_profile_info</obj_method>
    </param>
</RGW>"""
    profile_info_list, active_profile = post_xml_action(xml_payload_profile_info)  # Kirim permintaan XML untuk info profil

    if profile_info_list:
        # Pilih profil pertama yang tidak aktif
        profile_name_to_switch = None
        for profile in profile_info_list:
            if profile.get('pdp_name') != active_profile:
                profile_name_to_switch = profile.get('pdp_name')
                break

        if profile_name_to_switch:
            print(f"Mengganti profil Active ke: {profile_name_to_switch}")
            switch_profile(profile_name_to_switch)
        else:
            print("Tidak ada profil yang dapat diganti selain profil yang sedang aktif.")
else:
    print("Login gagal. Periksa kembali kredensial Anda.")
