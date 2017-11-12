from kivy.event import EventDispatcher
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty, NumericProperty


class TrackData(EventDispatcher):
    is_available = BooleanProperty(True)
    is_selected = BooleanProperty(False)
    track = ObjectProperty(None)
    play_time = StringProperty("")

    def __init__(self, track):
        super(TrackData, self).__init__()
        self.track = track

    def __lt__(self, other):
        # print 'cmp'
        if other is None:
            return False
        return self.track < other.track

    def __le__(self, other):
        # print 'cmpe'
        if other is None:
            return False
        return self.track <= other.track

    def __gt__(self, other):
        # print 'cmp'
        if other is None:
            return True
        return self.track > other.track

    def __ge__(self, other):
        # pint 'cmpe'
        if other is None:
            return True
        return self.track >= other.track

    def __eq__(self, other):
        # print 'cmpe'
        if other is None:
            return False
        return self.track == other.track
