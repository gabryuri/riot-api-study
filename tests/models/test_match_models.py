import os 
from unittest.mock import Mock, patch 
import json 
import pytest 
from models.match_models import Match



def __build_path():
    return "/".join(os.path.dirname(os.path.realpath(__file__)).split("/")[0:-2])

def test_complete_match():
    path = __build_path()
    print(path)
    match_path = path + '/tests/fixtures/match.json'
    timeline_path = path + '/tests/fixtures/timeline.json'

    with open(match_path) as f:
        match_dict = json.load(f)

    with open(timeline_path) as f2:
        timeline_dict = json.load(f2)

    log = Mock()
    mytestmatch = Match(log,'gabrinho',match_dict, timeline_dict)

    assert mytestmatch.ally_top == 'Camille'
    assert mytestmatch.enemy_top == 'KSante'
    assert mytestmatch.ally_jungle == 'Belveth'
    # assert mytestmatch.enemy_jungle
    # assert mytestmatch.ally_middle
    # assert mytestmatch.enemy_middle
    # assert mytestmatch.ally_bottom
    # assert mytestmatch.enemy_bottom
    # assert mytestmatch.ally_utility
    # assert mytestmatch.enemy_utility

    parsed_data, cols = mytestmatch.get_data_as_list()
    assert len(cols) == 53


def test_match_remake():
    path = __build_path()
    print(path)
    match_path = path + '/tests/fixtures/match_remake.json'
    timeline_path = path + '/tests/fixtures/timeline.json'

    with open(match_path) as f:
        match_dict = json.load(f)

    with open(timeline_path) as f2:
        timeline_dict = json.load(f2)

    log = Mock()
    mytestmatch = Match(log,'gabrinho',match_dict, timeline_dict)

    assert mytestmatch.ally_top == 'Camille'
    assert mytestmatch.enemy_top == 'Aatrox'
    assert mytestmatch.ally_utility == 'Soraka'
    assert mytestmatch.enemy_utility == 'Zyra'

