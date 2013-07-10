from loads.case import TestCase
import string
import random
import json
import time
import gevent
import urllib2

class TestPushgo(TestCase):

    def _str_gen(self, size=6, chars=string.ascii_uppercase + string.digits):
        #generate rand string
        return ''.join(random.choice(chars) for x in range(size))

    def _get_uaid(self, chan_str):
        """uniquify our channels so there's no collision"""
        return "%s%s" % (chan_str, self._str_gen(16))

    def _send_http_put(self, update_path, args='version=123',
                       ct='application/x-www-form-urlencoded',
                       exit_on_assert=False):
        """ executes an HTTP PUT with version"""
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        request = urllib2.Request(update_path, args)
        request.add_header('Content-Type', ct)
        request.get_method = lambda: 'PUT'
        try:
            url = opener.open(request)
        except Exception, e:
            if exit_on_assert:
                import pdb; pdb.set_trace()
                exit('Exception in HTTP PUT: %s' % (e))
            raise e
        url.close()
        return url.getcode()

    def test_reg(self):
        uaid =  self._get_uaid("")
        chan = self._str_gen(16)
        version = self._str_gen(8)
        results = []
        #server = 'ws://ec2-54-244-98-201.us-west-2.compute.amazonaws.com:8080'
        server = 'ws://localhost:8080'
        def callback(m):
            data = json.loads(m.data)
            print 'RECV:', data
            results.append(data)
            
            if "status" in data.keys():
                self.assertEqual(data['status'], 200)
            if "pushEndpoint" in data.keys():
                ret = self._send_http_put(data['pushEndpoint'], version)
            elif "notification" in data.keys():
                self.assertEqual(data['updates'][0]['version'], version)
                ws.send('{"messageType":"ack",  "updates": [{"channelID": "%s", "version": %s}]}'
                        % (chan, version))
    
        ws = self.create_ws(server, callback=callback)
        ws.send('{"messageType":"hello", "channelIDs":[], "uaid":"%s"}' % uaid)
        ws.receive()
        
        ws.send('{"messageType":"register", "channelID":"%s", "uaid":"%s"}' % (chan, uaid))
        ws.receive()
        
        start = time.time()
        while len(results) < 3:
            gevent.sleep(0)
            if time.time() - start > 10:
                raise AssertionError('Too slow')