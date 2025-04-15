# made for pyscript 
# depends on MFP website. If changes happen to the wpage structure, this will break
# you will need to update the cookie but I do not know how often 
# call the script from an automation to update the sensors

import datetime as dt
import requests
from bs4 import BeautifulSoup
# if you cant pip intall this, dependancies can be imported by adding "requirements.txt" in your pyscript folder. 
# each import should get its own line e.g.,
# beautifulsoup4
# requests
# but without the hashtag


@service
def fetch_myfitnesspal_data(): 
  # alternatively add an arguement to pass dates from the automation yaml (passed_date):
    log.info("Fetching MyFitnessPal data...")


    # Paste your current valid cookie here
    session_cookie = "YOUR COOKIE STRING HERE" # get this from devtools-storage while browsing a diary page after logging in. Any diary page will do. I do not know how long the ccookie will last.
    username = "YOUR USER NAME HERE" # your MFP username
    today = dt.date.today() # script only looks for the current date. you can use it to look for any date by reconfiguring the script to accept a date as an arguement passed from your automation yaml
    # today = passed_date
    date_string = f"{today.year},{today.month},{today.day}" 

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Cookie": session_cookie
    }

    food_url = f"https://www.myfitnesspal.com/food/diary/{username}?date={date_string}"
    exercise_url = f"https://www.myfitnesspal.com/exercise/diary/{username}?date={date_string}"
  # add any other diary pages you want to scrape from

  # these two functions follow the same basic structure. you can add more functions if you want to bring in data from other pages
    def get_food_info():
        results = {"Calories": 0, "Protein": 0} # add data headings as needed
        try:
            r = task.executor(requests.get, food_url, headers=headers)
            if r.ok:
                soup = BeautifulSoup(r.text, "html.parser")
                row = soup.find("tr", class_="total")
                if row:
                    columns = row.find_all("td")
                    if len(columns) >= 5:
                        results["Calories"] = int(columns[1].text.strip())
                        protein_raw = columns[4].get_text(" ", strip=True).split()[0]
                        results["Protein"] = int(protein_raw)
                      # add the headings from the tabel on the diary page or look it up in devtools-source to be safe
        except Exception as e:
            log.error(f"Failed to fetch food info: {e}")
        return results

    def get_exercise_info(): 
        calories = 0
        try:
            r = task.executor(requests.get, exercise_url, headers=headers)
            if r.ok:
                soup = BeautifulSoup(r.text, "html.parser")
                for row in soup.find_all("tr"):
                    if "Health Connect calorie adjustment" in row.text:
                        for td in row.find_all("td"):
                            text = td.text.strip()
                            if text.isdigit():
                                calories = int(text)
                                return calories
                               # add the headings from the tabel on the diary page or look it up in devtools-source to be safe
                              # you may need to gather more than one number and sum them, as there is no "totals" row on the excersise page
   
        except Exception as e:
            log.error(f"Failed to fetch exercise info: {e}")
        return 0
    
  food = get_food_info()
    exercise = get_exercise_info()

    # Set sensors in Home Assistant. These need to be created in either your configuration.yaml or through the UI under "helpers"
    state.set("sensor.mfp_calories", food["Calories"], {"unit_of_measurement": "kcal", "friendly_name": "MFP Calories"})
    state.set("sensor.mfp_protein", food["Protein"], {"unit_of_measurement": "g", "friendly_name": "MFP Protein"})
    state.set("sensor.mfp_exercise", exercise, {"unit_of_measurement": "kcal", "friendly_name": "MFP Exercise"})

    log.info(f"MFP Updated: {food['Calories']} kcal, {food['Protein (g)']} g protein, {exercise} kcal burned")
