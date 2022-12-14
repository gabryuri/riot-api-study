import json
import logging
import time
from datetime import datetime, timedelta

import pandas as pd

from models.match_models import Match, MatchTimeLine
from utils.gsheet import gsheets_data_dump, get_dataset, list_write
from utils.api_utils import generate_url, retrieve_data, url_base_americas, url_base



logging.basicConfig(
    format="[%(levelname)s] [%(asctime)s][%(filename)-15s][%(lineno)4d] : %(message)s",
    level=logging.INFO,
    force=True,
)
log = logging.getLogger()


def main(player, sheet_plan, sheet_id):
    

    match_sheet_range = get_matches(playername=player,
                          sheet_plan=sheet_plan,
                          sheet_id=sheet_id,
                          log=log)
    #match_sheet_range = 'gabrinho_2021-12-01_2022-12-01_Q420'
    matches = get_dataset(logger=log, spreadsheet_id=sheet_id, range=match_sheet_range, raw_list=True)

    for match in matches:
        time.sleep(2)
        match_info_suffix = f"lol/match/v5/matches/{match}"
        match_timeline_suffix = f"lol/match/v5/matches/{match}/timeline"

        match_info_url = generate_url(url_base_americas, match_info_suffix)
        match_data = retrieve_data(log=log, url=match_info_url)

        match_timeline_url = generate_url(url_base_americas, match_timeline_suffix)
        match_timeline_data = retrieve_data(log=log, url=match_timeline_url)
        

        # with open('timeline.json') as file:
        #     match_timeline_data = json.load(file)

        # with open('match.json') as file:
        #     match_data = json.load(file)

        match = Match(log, player, match_data, match_timeline_data)
        parsed_data, cols = match.get_data_as_list()
        

        df = pd.DataFrame(parsed_data, columns=cols)

        gsheets_data_dump(
        df=df,
        spreadsheet_id=sheet_id,
        range_sheet=f"{sheet_plan}!A1",
        logger=log,
        title=True,
        mode='append'
    )
   


def get_puuid_from_playername(playername, log):
    player_info_url = generate_url(
        url_base, f"lol/summoner/v4/summoners/by-name/{playername}"
    )
    response_json = retrieve_data(log=log, url=player_info_url)
    return response_json.get("puuid")
    

def get_matches(playername=None,
                end_date=None,
                interval_in_days=1300,
                sheet_plan=None,
                sheet_id=None,
                log=None,
                queue='420'):

    puuid = get_puuid_from_playername(playername, log)

    if end_date:
        end_time = datetime.strptime(end_date,"%Y-%m-%d")
    else:
        end_time = datetime.now()

    start_time = end_time - timedelta(days=interval_in_days)

    unix_end = int(datetime.timestamp(end_time))
    unix_start = int(datetime.timestamp(start_time))
    log.info(f'Querying from {start_time} to {end_time}')

    match_id_list = []
    offset = 0
    while True:
        matches_suffix = f"/lol/match/v5/matches/by-puuid/{puuid}/ids?startTime={unix_start}&endTime={unix_end}&start={offset}&count=100&queue={queue}"
        
        matches_url = generate_url(url_base_americas, matches_suffix)
        matches = retrieve_data(log=log, url=matches_url, is_list=True)
        log.info(f"matches returned {len(matches)}")
        match_id_list.extend(matches)
        offset += 100
        if len(matches) < 100: 
            break
    player_range = f"gabrinho_{str(start_time)[0:10]}_{str(end_time)[0:10]}_Q{queue}"
    list_write(match_id_list, sheet_id, player_range, log)
    return player_range



if __name__ == "__main__":

    main(
        player="gabrinho",
        sheet_plan="gabrilo_01_dez",
        sheet_id="1X0HhoMvn0YvVX2wQoKw-wHt7HGm2bEBVY6C-pfqsK5o",
    )
