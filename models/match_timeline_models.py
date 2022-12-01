class TimelineElement:
    def __init__(self, log, events, participantFrames, timestamp, player_mappings, match_id):
        self.log = log
        self.events = events
        self.participantFrames = participantFrames
        self.timestamp = timestamp
        self.player_mappings = player_mappings
        self.timestamp_minutes_round = int(timestamp/60000)
        self.match_timeline_id = f"{match_id}_{timestamp}"
        self.timeline_column_list = ['match_time', 'match_time_seconds', 'match_timeline_id']
        self.timeline_data_list = [self.timestamp_minutes_round, self.timestamp/1000, self.match_timeline_id]
        self.get_participant_statistics()
        

    def get_participant_statistics(self):
        self.statistics_dict = {}
        for player_index in self.participantFrames.keys():
            
            gold = self.participantFrames.get(player_index).get('totalGold')
            xp = self.participantFrames.get(player_index).get('xp')
            farm = self.participantFrames.get(player_index).get('minionsKilled')

            gold_attr = f'{self.player_mappings.get(int(player_index))}_total_gold'
            xp_attr = f'{self.player_mappings.get(int(player_index))}_total_xp'
            farm_attr = f'{self.player_mappings.get(int(player_index))}_total_farm'

            attr_name_list = [gold_attr, xp_attr, farm_attr]
            attr_value_list = [gold, xp, farm]

            self.timeline_column_list.extend(attr_name_list)
            self.timeline_data_list.extend(attr_value_list)
        



class MatchTimeLine:
    def __init__(self, log, timeline_dict, player_mappings):
        self.log = log
        self.player_mappings = player_mappings
        
        for key, value in timeline_dict.items():
            setattr(self, key, value)
        self.match_id = self.metadata.get('matchId')

        self.get_timeline_elements()

    def get_timeline_elements(self):
        self.recorded_frames = []
        for frame in self.info.get('frames'):
            element = TimelineElement(self.log,
                                      frame.get('events'),
                                      frame.get('participantFrames'),
                                      frame.get('timestamp'),
                                      self.player_mappings,
                                      self.match_id)
            self.recorded_frames.append(element)
