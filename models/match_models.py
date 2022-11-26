import json
from datetime import datetime
import json


class Match:
    def __init__(self, log, player_of_interest, match_dict):
        self.player_of_interest = player_of_interest
        self.log = log
        for key, value in match_dict.items():
            setattr(self, key, value)

        self.friends_dict = {
            "DfSSu4EsE4ztxtTbLjiGRqTv1HVbO9bD9UeKVCyJnfnTPy7P_44SOzafM36wugh09nsGLVHaUtvb7A": "Azeros",
            "G1rqK5LK-CViiRQKAzqGsbtcoSSG_Qneu_hX9fzH2Cys1xMdjzgnUl09i1gqxVdpv0NLCF5jm7DypA": "gabrinho",
            "FYwItsH522cx0I4TxsOR15WOdvJEPI9uoWLblJ3EN99-FZ4p9lJtEv6tJ55o19_zZRlCw6-XovvAVA": "gabrilogotsauce",
            "9CYNhNvRP9DzLm8AYXbe1e07nrXasYDbztkTORw5vcwSRkMhxKlzWblSC-Mwb-kh96ZZ5zDtCAgMAA": "Mr Brightside",
            "fY6s0bdCNtxUU3ZGhl2iDGC6SmLI0H-3Fk1NeeNuPiwwIoiXC6QbI7XH8Xygx5M_iTJGQF_z_Fdj5Q": "5150",
            "QYS7RQuhj7QhGXGTowHZLl3a4L61K8vI9WnOA95z_ITLnjl7elK3wqsopGHKEuFp-GnKrbAz65mLZw": "Nicles",
            "9WiHA-Fe9faeWDb7SDYTkn3RO5CjUMb-_tiOWWaAzg2dBZLXW-hzUVdYVPj5MRqlpkIuiPHA_tsH7A": "jaja dif",
            "KUp3XyetkO3H7ogtd51aR1h03JWySsq-LNd1X8fXYGTg8migwWbWY4vsqrCOwcSC3GxWtxmKe4-Nww": "jpark",
            "YrGcQe6crLrcGSU2IpPGFX3yxbT2NUdmLoFbHLDef7sE7P0TQQmMDZ-7eYuFeKs3cR7vGyaBoW5BQg": "leowoke",
            "LIVXg9GE4dmjq0kwUaTEQXWlTAdv_pO7Ydh06G_0uUB_SakTjg4n3Rye18_zWLHGEDSF9Zm-9Lnnaw": "schloser",
            "ITIE-1IqY8Ms0PadoOQ0w2sLZfCDLmMlRS7fnnR2nfiXuststlR4Jcerwkkgu7ZZPozFQW6pIlSMig": "Boxes",
        }

        self.queues_dict = {
            450: "All Random games",
            400: "5v5 Draft Pick games",
            410: "5v5 Ranked Dynamic games",
            420: "5v5 Ranked Solo games",
            430: "5v5 Blind Pick games",
            440: "5v5 Ranked Flex games",
        }

        self.log.info("calculating metrics")

        self.get_player_info_of_interest()
        self.calculate_basic_attributes()
        self.get_teams_info()
        self.get_teams_info_as_cols()
        self.get_known_players()

    def get_data_as_list(
        self,
        columns=[
            "player_of_interest",
            "win",
            "queue",
            "ally_position_of_interest",
            "ally_matchup_of_interest",
            "enemy_matchup_of_interest",
        ],
    ):
        data = []
        for column in columns:
            column_data = self.__dict__.get(column)
            if isinstance(column_data, dict):
                data.append(json.dumps(column_data))
            elif isinstance(column_data, bool):
                data.append(str(column_data))
            else:
                data.append(column_data)
        return data

    def calculate_basic_attributes(self):
        self.timestamp = datetime.fromtimestamp(
            self.info.get("gameCreation") / 1000
        ).strftime("%Y-%m-%d %H:%M:%S")
        self.queue = self.queues_dict.get(self.info.get("queueId"))
        self.win = self.player_of_interest_info.get("win")
        self.match_id = self.metadata.get("matchId")
        self.time_in_seconds = self.info.get("gameDuration")
        self.time_in_minutes_decimal = self.time_in_seconds / 60
        self.remake = str(self.time_in_minutes_decimal < 5)

    def get_player_info_of_interest(self):
        self.player_of_interest_info = [
            participant
            for participant in self.info.get("participants")
            if participant.get("summonerName") == self.player_of_interest
        ][0]

    def get_teams_info(self):
        team_info_dict = {self.teams[0]: {}, self.teams[1]: {}}

        for participant in self.info.get("participants"):
            player_dict = {}
            player_dict["name"] = participant.get("summonerName")
            player_dict["champion"] = participant.get("championName")
            player_dict["turretPlatesTaken"] = participant.get("challenges").get(
                "turretPlatesTaken"
            )
            player_dict["soloKills"] = participant.get("challenges").get("soloKills")

            team_info_dict[participant.get("teamId")][
                participant.get("teamPosition")
            ] = player_dict

        team_info_dict["ally"] = team_info_dict.pop(self.teams_processed.get("ally"))
        team_info_dict["enemy"] = team_info_dict.pop(self.teams_processed.get("enemy"))
        self.teams_info = team_info_dict

    def get_teams_info_as_cols(self):
        # self.log.info(f'attributes {self.teams_info}')
        if self.info.get('gameMode') == 'CLASSIC':
            roles = ['TOP', 'JUNGLE', 'MIDDLE', 'BOTTOM', 'UTILITY']
            teams = list(self.teams_info.keys())
            for team in teams:
                for role in roles:
                    attribute_name = f"{team.lower()}_{role.lower()}"
                    try:
                        attribute_value = self.teams_info.get(team).get(role).get("champion")
                    except: 
                        attribute_value = self.teams_info.get(team).get('').get("champion")
                    self.log.info(f'setting attribute {attribute_name} with value {attribute_value}')
                    setattr(self, attribute_name, attribute_value)
            


    def get_known_players(self):
        players = self.metadata.get("participants")
        known_players = [
            self.friends_dict.get(puuid)
            for puuid in players
            if self.friends_dict.get(puuid) is not None
        ]
        sorted_players = sorted(known_players)
        self.known_players = sorted_players

    @property
    def amount_of_known_players(self):
        return len(known_players)

    @property
    def teams(self):
        teams = [team.get("teamId") for team in self.info.get("teams")]
        return teams

    @property
    def teams_processed(self):
        team_of_interest = self.player_of_interest_info.get("teamId")
        teams_temp = self.teams
        teams_temp.remove(team_of_interest)
        opposing_team = teams_temp[0]
        return {"ally": team_of_interest, "enemy": opposing_team}

    @property
    def ally_position_of_interest(self):
        return self.player_of_interest_info.get("teamPosition")

    @property
    def ally_matchup_of_interest(self):
        return (
            self.teams_info.get("ally")
            .get(self.ally_position_of_interest)
            .get("champion")
        )

    @property
    def enemy_matchup_of_interest(self):
        return (
            self.teams_info.get("enemy")
            .get(self.ally_position_of_interest)
            .get("champion")
        )
