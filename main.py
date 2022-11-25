import json 
from models.match_models import Match
from utils.gsheet import gsheets_data_dump, get_dataset
from utils.api_utils import generate_url, retrieve_data, url_base_americas, url_base
import pandas as pd 
import logging 
import time 

logging.basicConfig(format= "[%(levelname)s] [%(asctime)s][%(filename)-15s][%(lineno)4d] : %(message)s", level=logging.INFO, force=True)
log = logging.getLogger()

sheet_plan = 'marte'
sheet_id = '1X0HhoMvn0YvVX2wQoKw-wHt7HGm2bEBVY6C-pfqsK5o'

def main():
    time.sleep(1)
    player = 'Mr Brightside'
    matches = get_matches(player)

    cols = ['player_of_interest','match_id','amount_of_known_players',
        'known_players','win','queue','timestamp',
        'ally_top','enemy_top','ally_jng','enemy_jng','ally_mid',
        'enemy_mid','ally_adc','enemy_adc','ally_sup','enemy_sup',
        'time_in_seconds','time_in_minutes_decimal','remake']
    final_data = []

    for match in matches: 
        match_info_suffix = f"lol/match/v5/matches/{match}"
        match_info_url = generate_url(url_base_americas, match_info_suffix)
        match_data = retrieve_data(log=log, url=match_info_url)
        match = Match(log, player, match_data)
        parsed_data = match.get_data_as_list(columns=cols)
        final_data.append(parsed_data)
        

    df = pd.DataFrame(final_data, columns=cols)
    offset = find_starting_offset(sheet_plan)
    log.info(f'offset: {offset}')
    
    title = True
    offset_to_insert = 1 
    if offset > 0:
        title = False 
        offset_to_insert = offset + 2 

    gsheets_data_dump(df=df,spreadsheet_id=sheet_id,range_sheet=f'{sheet_plan}!A{offset_to_insert}',create_sheet=True, title=title, clear=False)





def get_matches(playername):
    player_info_url = generate_url(url_base, f'lol/summoner/v4/summoners/by-name/{playername}')
    response_json = retrieve_data(log=log, url=player_info_url)
    main_puuid = response_json.get('puuid')


    offset = find_starting_offset(sheet_plan)
    log.info(f'offset: {offset}')

    matches_suffix = f"/lol/match/v5/matches/by-puuid/{main_puuid}/ids?start={offset}&count=15&queue=420"
    matches_url = generate_url(url_base_americas, matches_suffix)
    matches = retrieve_data(log=log, url=matches_url, is_list=True)
    log.info(f'matches returned {len(matches)}')

    return matches#['BR1_2619338540']#matches


def find_starting_offset(sheet_page):
    try:
        df = get_dataset(logger=log,spreadsheet_id=sheet_id,range=sheet_page)
        offset = df.shape[0]
    except Exception as e:
        offset = 0
        log.info(e)
    return offset

main()
