from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd


# Setup Chrome options
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Headless mode
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Initialize driver and data frame
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 20)
data = [] 

# Helper function
def get_text_by_xpath(xpath):
    try:
        element = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
        return element.text.strip() if element.text.strip() else "N/A"
    except:
        return "N/A"

# Define XPaths
xpaths = {
    "rera_regd_no": '//*[@id="mainContent"]/div/div/app-project-overview/div/div[1]/div/div[2]/div/div[1]/div[4]/div[2]/strong',
    "project_name": '//*[@id="mainContent"]/div/div/app-project-overview/div/div[1]/div/div[2]/div/div[1]/div[1]/div[2]/strong',
    "promoter_name": '//*[@id="mainContent"]/div/div/app-promoter-details/div[1]/div/div[2]/div/div[1]/div/div[2]/strong',
    "promoter_address": '//*[@id="mainContent"]/div/div/app-promoter-details/div[1]/div/div[2]/div/div[6]/div/div[2]/strong',
    "gst_no": '//*[@id="mainContent"]/div/div/app-promoter-details/div[1]/div/div[2]/div/div[11]/div/div[2]/strong'
}

# Visit the URL
driver.get("https://rera.odisha.gov.in/projects/project-list")
time.sleep(2)

# Scroll down multiple times to load more projects
scroll_pause_time = 2
for _ in range(4):  # Increase scrolls to load more projects
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(scroll_pause_time)

# Wait for all projects to load
wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "app-project-card")))
time.sleep(2)

# Get all view buttons
view_buttons = driver.find_elements(By.XPATH, "//a[text()='View Details']")
print(f"Total projects found: {len(view_buttons)}")

# Process first 5 projects
for i in range(min(5, len(view_buttons))):
    try:
        # Re-load project list page
        driver.get("https://rera.odisha.gov.in/projects/project-list")
        time.sleep(3)

        # Scroll again
        for _ in range(4):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause_time)

        # Re-fetch buttons
        view_buttons = driver.find_elements(By.XPATH, "//a[text()='View Details']")
        view_button = view_buttons[i]
        driver.execute_script("arguments[0].scrollIntoView(true);", view_button)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", view_button)

        # Wait for content
        wait.until(EC.presence_of_element_located((By.ID, "mainContent")))
        time.sleep(2)
        
        #extrace data from Project Overview
        rera_regd_no = get_text_by_xpath(xpaths["rera_regd_no"])
        project_name = get_text_by_xpath(xpaths["project_name"])

        # Click promoter tab
        try:
            promoter_tab = wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Promoter")))
            driver.execute_script("arguments[0].click();", promoter_tab)
            time.sleep(1)
        except:
            print(f"Promoter tab not found for project {i+1}")

        # Extract values
        promoter_name = get_text_by_xpath(xpaths["promoter_name"])
        promoter_address = get_text_by_xpath(xpaths["promoter_address"])
        gst_no = get_text_by_xpath(xpaths["gst_no"])

        data.append({
            "Project No": i + 1,
            "RERA Regd. No": rera_regd_no,
            "Project Name": project_name,
            "Promoter Name": promoter_name,
            "Promoter Address": promoter_address,
            "GST No": gst_no
            })

    except Exception as e:
        print(f"Error with project {i+1}: {e}")

df = pd.DataFrame(data)
df.to_csv("projects.csv", index=False, encoding='utf-8')

# Quit
driver.quit()


# tip --> when GST NO is N/A then it means they don't provide GST Number or they provide pdf file for GST number.