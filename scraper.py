'''
Song Information Web Scraper

Piero Orderique
STS.005 Data and Society
25 Feb 2022
'''
from collections import defaultdict
from colorama import Fore
import time

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

DEBUG_MODE = True

def log_print(*message, color=Fore.CYAN):
    if not DEBUG_MODE: return
    print(color + "[SongInfoScraper]:", *message, end="")
    print(Fore.WHITE + "")

class SongInfoScraper():

    WEBSITE = "https://www.chosic.com/music-genre-finder/"
    DRIVER_TIMEOUT = 10
    PAUSE_TIME = 1.2 # needed to avoid checking elements before page load

    def __init__(self) -> None:
        self._restart_driver()
        self._open()

    def get_song_info(self, title, artist):
        self._search_song(title, artist)

        # get album name
        year = (self.driver.find_element(By.CLASS_NAME, "album-data")
                .get_attribute("innerHTML")[-5:-1])
        log_print(year, color=Fore.GREEN)

        # get list of genre tags
        tag_containers = self.driver.find_elements(By.XPATH, '//div[@class="pl-tags tagcloud"]')
        tag_elems = [] 
        [tag_elems.extend(tag_container.find_elements(By.TAG_NAME, "a")) \
            for tag_container in tag_containers]
        genre_tags = list({tag.get_attribute('innerHTML') for tag in tag_elems})
        log_print(genre_tags, color=Fore.GREEN)

        # get tempo
        tempo = int(self.driver.find_element(By.CLASS_NAME, "tempo-duration-first")
                    .find_elements(By.TAG_NAME, "span")[1]
                    .get_attribute("innerHTML")
                    .split(" ")[1])
        log_print(tempo, color=Fore.GREEN)

        # get metrics
        raw_metrics = (self.driver.find_element(By.CLASS_NAME, "progressbars-div")
                    .get_attribute("textContent")
                    .split(" "))
        raw_metrics = list(filter(lambda x: x != "", raw_metrics))
        assert len(raw_metrics) % 2 == 0, "you got something else bro"

        metrics = {}
        for idx in range(0, len(raw_metrics), 2):
            category, score = (
                raw_metrics[idx][:-1],
                raw_metrics[idx+1][:-4]
            )
            metrics[category] = score

        log_print(metrics, color=Fore.GREEN)

        return {
            "Date Released": year,
            "Genres": ",".join(genre_tags),
            "Tempo": tempo,
            **metrics
        }

    def _search_song(self, title, artist):
        search_box = self.driver.find_element(By.ID, "search-word")
        search_box.send_keys(title + " - " + artist)

        log_print("song typed into input")
        
        try:
            song_dropdown = self.driver.find_element(By.CLASS_NAME, "span-class")
            song_id = song_dropdown.get_attribute("data-song-id")
            log_print("Song id is", song_id)

            self.driver.get(SongInfoScraper.WEBSITE + f"?track={song_id}")
            log_print("song clicked on dropdown")
            time.sleep(SongInfoScraper.PAUSE_TIME)

        except Exception as e:
            log_print("Did not find element. Restarting...", color=Fore.RED)
            self._restart()
            self.get_song_info(title, artist)

    def _restart_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--window-size=1000,800")
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        self.driver.implicitly_wait(SongInfoScraper.DRIVER_TIMEOUT)

    def _restart(self):
        self._close()
        self._restart_driver()
        self._open()

    def _open(self):
        self.driver.get(SongInfoScraper.WEBSITE)
        log_print(f"OPENED {SongInfoScraper.WEBSITE}")
        time.sleep(SongInfoScraper.PAUSE_TIME)

    def _close(self):
        log_print(f"Exiting driver.")
        self.driver.close()


def create_full_dataset(dataset_path, output_path="./data/complete_dataset.csv"):
    """ 
    Given a CLEANED (no weird characters, no null entries in title or artist)
    dataset containing a 'Title' and 'Artist' column, creates a NEW dataset 
    containing all columns in input dataset plus those produced by `get_song_info`
    method in SongInfoScraper
    """
    cleaned_dataset = pd.read_csv(dataset_path)
    scraper = SongInfoScraper()

    new_columns = defaultdict(lambda: [])
    total_songs = len(cleaned_dataset)

    # fill in new columns
    for (idx, row) in cleaned_dataset.iterrows():
        song_title, song_artist = row['Title'], row['Artist']
        log_print(f"On song {idx + 1}/{total_songs}: {song_title}, {song_artist}")

        try:
            for (metric, value) in scraper.get_song_info(song_title, song_artist).items():
                new_columns[metric].append(value)

        except Exception as e:
            log_print(f"Received an error on song {idx}: {song_title}\n{e}", color=Fore.YELLOW)

    log_print(f"new columns created!", color=Fore.LIGHTGREEN_EX)

    # save results just in case!
    import json
    with open('./data/generated_columns.json', 'w') as fp:
        json.dump(new_columns, fp)


    # append columns to dataframe
    for (column_name, column_data) in new_columns.items():
        cleaned_dataset[column_name] = column_data

    cleaned_dataset.to_csv(output_path)
    log_print(f"COMPLETE DATASET CREATED.", color=Fore.LIGHTGREEN_EX)


def main():
    CLEAN_DATA_PATH = './data/cleaned_dataset.csv'
    # CLEAN_DATA_PATH = './data/test_cleaned.csv'
    create_full_dataset(dataset_path=CLEAN_DATA_PATH)


if __name__ == "__main__":
    main()