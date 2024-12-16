import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

def save_cookies_as_txt(driver, output_file):
    """Saves the cookies from a Selenium WebDriver session to a cookies.txt file."""
    cookies = driver.get_cookies()
    with open(output_file, "w") as f:
        for cookie in cookies:
            f.write(f"{cookie.get('domain')}\t")
            f.write(f"{'TRUE' if cookie.get('httpOnly') else 'FALSE'}\t")
            f.write(f"{cookie.get('path')}\t")
            f.write(f"{'TRUE' if cookie.get('secure') else 'FALSE'}\t")
            f.write(f"{cookie.get('expiry') if 'expiry' in cookie else ''}\t")
            f.write(f"{cookie.get('name')}\t")
            f.write(f"{cookie.get('value')}\n")

def fetch_youtube_cookies():
    """Fetch cookies from YouTube using ChromeDriver."""

    # Path to ChromeDriver
    chromedriver_path = "/Users/mjx/Downloads/chromedriver-mac-arm64/chromedriver"

    # Remove quarantine attribute on macOS
    try:
        os.system(f"xattr -d com.apple.quarantine {chromedriver_path}")
        print(f"Quarantine attribute removed from {chromedriver_path}")
    except Exception as e:
        print(f"Failed to remove quarantine attribute: {e}")
        return

    # Set up WebDriver
    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service)

    try:
        # Open YouTube and log in manually if necessary
        driver.get("https://www.youtube.com")
        print("Please log in to YouTube in the opened browser window.")
        input("Press Enter after logging in...")

        # Save cookies to a file
        output_file = "cookies.txt"
        save_cookies_as_txt(driver, output_file)
        print(f"Cookies saved to {output_file}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    fetch_youtube_cookies()
