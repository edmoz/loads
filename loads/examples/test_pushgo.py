from loads.case import TestCase
import string
import random
import json
class TestPushgo(TestCase):

    def _str_gen(self, size=6, chars=string.ascii_uppercase + string.digits):
        #generate rand string
        return ''.join(random.choice(chars) for x in range(size))

    def _get_uaid(self, chan_str):
        """uniquify our channels so there's no collision"""
        return "%s%s" % (chan_str, self._str_gen(16))

    def test_reg(self):
        uaid =  self._get_uaid("")
        def callback(m):
            data = json.loads(m.data)
            self.assertIn('status', data.keys())
            self.assertIn(200, data.values())
            
        ws = self.create_ws('ws://localhost:8080',
                            callback=callback)
        ws.send('{"messageType":"hello", "channelIDs":[], "uaid":"%s"}' % uaid)
        ws.receive()
        ws.send('{"messageType":"register", "channelID":"abc", "uaid":"%s"}' % uaid)
        ws.receive()