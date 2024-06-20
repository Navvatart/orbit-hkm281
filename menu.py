import requests
from bs4 import BeautifulSoup
import os
import subprocess


#developmet by Navvatart
#version 0.1

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

# Header untuk permintaan HTTP
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, seperti Gecko) Chrome/91.0.4472.124 Safari/537.36",
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
        response = session.post(xml_action_url, data=xml_payload, headers={'Content-Type': 'application/xml', **headers})
        response.raise_for_status()  # Memeriksa jika permintaan berhasil

        if response.status_code == 200:
            # Parsing XML response
            soup = BeautifulSoup(response.content, 'xml')
            return soup
        else:
            print(f"Terjadi kesalahan saat mengirim permintaan XML: {response.status_code}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Terjadi kesalahan saat mengirim permintaan XML: {e}")
        return None

def get_cellular_info():
    xml_payload = """<?xml version="1.0" encoding="US-ASCII"?>
<RGW>
    <param>
        <method>call</method>
        <session>000</session>
        <obj_path>cm</obj_path>
        <obj_method>get_link_context</obj_method>
    </param>
</RGW>"""
    soup = post_xml_action(xml_payload)
    if soup:
        basic_info = soup.find("celluar_basic_info")
        if basic_info:
            print("Informasi Dasar Seluler:")
            sys_mode = basic_info.find("sys_mode").text if basic_info.find("sys_mode") else "N/A"
            data_mode = basic_info.find("data_mode").text if basic_info.find("data_mode") else "N/A"
            rssi = basic_info.find("rssi").text if basic_info.find("rssi") else "N/A"
            reg_status = basic_info.find("RegStatus").text if basic_info.find("RegStatus") else "N/A"
            imei = basic_info.find("IMEI").text if basic_info.find("IMEI") else "N/A"
            imsi = basic_info.find("IMSI").text if basic_info.find("IMSI") else "N/A"
            network_name = basic_info.find("network_name").text if basic_info.find("network_name") else "N/A"
            roaming_status = basic_info.find("roaming_status").text if basic_info.find("roaming_status") else "N/A"

            print(f"Sistem Mode: {sys_mode}")
            print(f"Mode Data: {data_mode}")
            print(f"RSSI: {rssi}")
            print(f"Status Registrasi: {reg_status}")
            print(f"IMEI: {imei}")
            print(f"IMSI: {imsi}")
            print(f"Nama Jaringan: {network_name}")
            print(f"Status Roaming: {roaming_status}")
        else:
            print("Informasi Dasar Seluler tidak ditemukan.")
    else:
        print("Gagal mendapatkan informasi seluler.")

def get_band_info():
    xml_payload = """<?xml version="1.0" encoding="US-ASCII"?>
<RGW>
    <param>
        <method>call</method>
        <session>000</session>
        <obj_path>util_wan</obj_path>
        <obj_method>get_currentband_info</obj_method>
    </param>
</RGW>"""
    soup = post_xml_action(xml_payload)
    if soup:
        band_info = soup.find("response")
        if band_info:
            print("\nInformasi Band Saat Ini:")
            ril_mode = band_info.find("ril_mode").text if band_info.find("ril_mode") else "N/A"
            gsm_band = band_info.find("gsm_band").text if band_info.find("gsm_band") else "N/A"
            umts_band = band_info.find("umts_band").text if band_info.find("umts_band") else "N/A"
            lte_band_h = band_info.find("lte_band_h").text if band_info.find("lte_band_h") else "N/A"
            lte_band_l = band_info.find("lte_band_l").text if band_info.find("lte_band_l") else "N/A"
            band_priority_1 = band_info.find("band_Priority_1").text if band_info.find("band_Priority_1") else "N/A"
            srv_domain = band_info.find("srv_domain").text if band_info.find("srv_domain") else "N/A"
            band_priority_2 = band_info.find("band_Priority_2").text if band_info.find("band_Priority_2") else "N/A"
            lte_band_e = band_info.find("lte_band_e").text if band_info.find("lte_band_e") else "N/A"

            print(f"Mode RIL: {ril_mode}")
            print(f"GSM Band: {gsm_band}")
            print(f"UMTS Band: {umts_band}")
            print(f"LTE Band High: {lte_band_h}")
            print(f"LTE Band Low: {lte_band_l}")
            print(f"Prioritas Band 1: {band_priority_1}")
            print(f"Domain Layanan: {srv_domain}")
            print(f"Prioritas Band 2: {band_priority_2}")
            print(f"LTE Band E: {lte_band_e}")
        else:
            print("Informasi Band Saat Ini tidak ditemukan.")
    else:
        print("Gagal mendapatkan informasi band.")

def get_context_info():
    xml_payload = """<?xml version="1.0" encoding="US-ASCII"?>
<RGW>
    <param>
        <method>call</method>
        <session>000</session>
        <obj_path>cm</obj_path>
        <obj_method>get_link_context</obj_method>
    </param>
</RGW>"""
    soup = post_xml_action(xml_payload)
    if soup:
        context_list = soup.find("contextlist")
        if context_list:
            items = context_list.find_all("Item")
            print("\nDaftar Konteks:")
            for item in items:
                index = item.get("index", "N/A")
                wan_type = item.find("wan_type").text if item.find("wan_type") else "N/A"
                connection_status = item.find("connection_status").text if item.find("connection_status") else "N/A"
                pdp_type = item.find("pdp_type").text if item.find("pdp_type") else "N/A"
                ip_type = item.find("ip_type").text if item.find("ip_type") else "N/A"
                apn = item.find("apn").text if item.find("apn") else "N/A"
                ipv4_ip = item.find("ipv4_ip").text if item.find("ipv4_ip") else "N/A"
                ipv4_dns1 = item.find("ipv4_dns1").text if item.find("ipv4_dns1") else "N/A"
                ipv4_dns2 = item.find("ipv4_dns2").text if item.find("ipv4_dns2") else "N/A"

                print(f"Index: {index}")
                print(f"WAN Type: {wan_type}")
                print(f"Status Koneksi: {connection_status}")
                print(f"Tipe PDP: {pdp_type}")
                print(f"Tipe IP: {ip_type}")
                print(f"APN: {apn}")
                print(f"IP: {ipv4_ip}")
                print(f"DNS1: {ipv4_dns1}")
                print(f"DNS2: {ipv4_dns2}")
                print("-" * 20)
        else:
            print("Daftar Konteks tidak ditemukan.")
    else:
        print("Gagal mendapatkan informasi konteks.")

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
    response = post_xml_action(xml_payload_switch_profile)
    if response:
        print(f"Profil berhasil diubah ke {profile_name}.")
    else:
        print(f"Gagal mengubah profil ke {profile_name}.")


def ambil_profil():
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
            print(f"Mengganti profil ke: {profile_name_to_switch}")
            switch_profile(profile_name_to_switch)
        else:
            print("Tidak ada profil yang dapat diganti selain profil yang sedang aktif.")

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def main_menu():
    while True:
        clear_screen()
        print("\nMenu:")
        print("1. Informasi Seluler")
        print("2. Informasi Band")
        print("3. Informasi IP")
        print("4. Ubah Profil/APN")
        print("5. Keluar")

        choice = input("Pilih opsi (1-5): ")

        if choice == "1":
            clear_screen()
            get_cellular_info()
            input("Tekan Enter untuk kembali ke menu utama...")
        elif choice == "2":
            clear_screen()
            get_band_info()
            input("Tekan Enter untuk kembali ke menu utama...")
        elif choice == "3":
            clear_screen()
            get_context_info()
            input("Tekan Enter untuk kembali ke menu utama...")
        elif choice == "4":
           clear_screen()
           
           subprocess.run(["python3", "/usr/bin/orbithkm281s.py"])
           input("Tekan Enter untuk kembali ke menu utama...")
        elif choice == "5":
            print("Keluar dari program.")
            break
        else:
            print("Opsi tidak valid. Silakan pilih lagi.")

# Logika utama skrip
if login():
    main_menu()
else:
    print("Login gagal. Tidak dapat melanjutkan.")
