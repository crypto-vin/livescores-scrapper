
from mozzart import Mozzart as mz

def get_scores():
    home_scores = []
    away_scores = []
    scores = mz.driver.find_elements_by_xpath("//*[@class='score total']")
    for score in scores:
        print(score)

mz().get_site()
get_scores()