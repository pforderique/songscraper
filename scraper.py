'''
Quick Web Scraper

Piero Orderique
20 Jan 2021

Quick Web Scraper returns a list of everything on a website
that is associated with an id or class. Very simple and 
straight forward program for the "quick webscraper" who 
just wants a list of all Xs included on one site.
'''
from colorama import Fore
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

DEBUG_MODE = True

def log_print(*message, color=Fore.CYAN):
    if not DEBUG_MODE: return
    print(color + "[SongGenreScraper]:", *message, end="")
    print(Fore.WHITE + "")

class SongGenreScraper():

    WEBSITE = "https://www.chosic.com/music-genre-finder/"
    DRIVER_PATH = "C:\\Users\\fabri\\Downloads\\chromedriver_win32\\chromedriver.exe"
    DRIVER_TIMEOUT = 10
    PAUSE_TIME = 2 # needed to avoid checking elements before page load

    def __init__(self, all_songs) -> None:
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")

        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        self.driver.implicitly_wait(SongGenreScraper.DRIVER_TIMEOUT)
        self.all_songs = all_songs
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
        genre_tags = [tag.get_attribute('innerHTML') for tag in tag_elems]
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

            self.driver.get(SongGenreScraper.WEBSITE + f"?track={song_id}")
            log_print("song clicked on dropdown")
            time.sleep(SongGenreScraper.PAUSE_TIME)

        except Exception as e:
            log_print("Did not find element. Restarting...", color=Fore.RED)
            self._restart()
            self.get_song_info(title, artist)

    def _restart(self):
        self._close()
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        self._open()
        self.driver.get(SongGenreScraper.WEBSITE)

    def _open(self):
        self.driver.get(SongGenreScraper.WEBSITE)
        log_print(f"OPENED {SongGenreScraper.WEBSITE}")
        time.sleep(SongGenreScraper.PAUSE_TIME)

    def _close(self):
        log_print(f"Exiting driver.")
        self.driver.close()


def main():
    # mock data
    songs = [
        ('Beyond the Sea', "Bobby Darin"),
        ('Vienna', "Billy Joel"),
    ]

    scraper = SongGenreScraper(songs)
    s = scraper.get_song_info(songs[0][0], songs[0][1])
    log_print(s)



if __name__ == "__main__":
    main()