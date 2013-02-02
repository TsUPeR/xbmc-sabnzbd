"""
 Copyright (c) 2013 Popeye

 Permission is hereby granted, free of charge, to any person
 obtaining a copy of this software and associated documentation
 files (the "Software"), to deal in the Software without
 restriction, including without limitation the rights to use,
 copy, modify, merge, publish, distribute, sublicense, and/or sell
 copies of the Software, and to permit persons to whom the
 Software is furnished to do so, subject to the following
 conditions:

 The above copyright notice and this permission notice shall be
 included in all copies or substantial portions of the Software.

 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
 OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
 HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
 WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
 OTHER DEALINGS IN THE SOFTWARE.
"""

import urllib
import urllib2
import xbmc
import xbmcaddon
from xml.dom.minidom import parse, parseString
#
try: import simplejson as json
except ImportError: import json
#
import post_form

import utils

class Sabnzbd:
    def __init__ (self):
        __settings__ = xbmcaddon.Addon(id='plugin.program.sabnzbd')
        self.init_api = SabnzbdApi(__settings__.getSetting("sabnzbd_ip"),
        __settings__.getSetting("sabnzbd_port"),__settings__.getSetting("sabnzbd_key"),
        __settings__.getSetting("sabnzbd_user"), __settings__.getSetting("sabnzbd_pass"),
        __settings__.getSetting("sabnzbd_cat"))


class SabnzbdApi:
    def __init__ (self, ip, port, apikey, username = None, password = None, category = None):
        self.ip = ip
        self.port = port
        self.apikey = apikey
        self.baseurl = "http://" + self.ip + ":" + self.port + "/api?apikey=" + apikey
        if username and password:
            password_manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
            url = "http://" + self.ip + ":" + self.port
            password_manager.add_password(None, url, username, password)
            authhandler = urllib2.HTTPBasicAuthHandler(password_manager)
            opener = urllib2.build_opener(authhandler)
            urllib2.install_opener(opener)
        self.category = category
        self.kwargs = dict()

    def action(self, **kwargs):
        self.kwargs.update(**kwargs)
        url = "%s&%s" % (self.baseurl, urllib.urlencode(self.kwargs))
        responseMessage = self._sabResponse(url)
        return responseMessage

    def addurl(self, nzb, nzbname, **kwargs):
        category = kwargs.get('category', None)
        priority = kwargs.get('priority', None)
        url = "%s&mode=addurl&name=%s&nzbname=%s" % \
              (self.baseurl, urllib.quote_plus(nzb),urllib.quote_plus(nzbname))
        if priority:
            url = "%s&priority=%s" % (url, priority)
        if category:
            url = "%s&cat=%s" % (url, category)
        elif self.category:
            url = "%s&cat=%s" % (url, self.category)
        responseMessage = self._sabResponse(url)
        return responseMessage

    def add_local(self, path, **kwargs):
        category = kwargs.get('category', None)
        priority = kwargs.get('priority', None)
        url = "%s&mode=addlocalfile&name=%s" % \
              (self.baseurl, urllib.quote_plus(path))
        if priority:
            url = "%s&priority=%s" % (url, priority)
        if category:
            url = "%s&cat=%s" % (url, category)
        elif self.category:
            url = "%s&cat=%s" % (url, self.category)
        responseMessage = self._sabResponse(url)
        return responseMessage
        
    def add_file(self, path, **kwargs):
        url = "%s&mode=addfile" % self.baseurl
        responseMessage = post_form.post(path, self.apikey, url, **kwargs)
        return responseMessage

    def max_speed(self, speed):
        self.kwargs['mode'] = 'config'
        self.kwargs['name'] = 'speedlimit'
        self.kwargs['value'] = speed
        return self.action()

    def reset_speed(self):
        return self.max_speed('')

    def pause(self):
        self.kwargs['mode'] = 'pause'
        return self.action()

    def nzo_pause(self, nzo_id):
        self.kwargs['mode'] = 'queue'
        self.kwargs['name'] = 'pause'
        self.kwargs['value'] = nzo_id
        return self.action()

    def resume(self):
        self.kwargs['mode'] = 'resume'
        return self.action()

    def nzo_resume(self, nzo_id):
        self.kwargs['mode'] = 'queue'
        self.kwargs['name'] = 'resume'
        self.kwargs['value'] = nzo_id
        return self.action()

    def nzo_delete(self, nzo_id):
        # will leave data in the incomplete dir
        self.kwargs['mode'] = 'queue'
        self.kwargs['name'] = 'delete'
        self.kwargs['value'] = nzo_id
        return self.action()

    def nzo_delete_files(self, nzo_id):
        self.kwargs['mode'] = 'queue'
        self.kwargs['name'] = 'delete'
        self.kwargs['value'] = nzo_id
        self.kwargs['del_files'] = '1'
        return self.action()

    def nzo_delete_history(self, nzo_id):
        self.kwargs['mode'] = 'history'
        self.kwargs['name'] = 'delete'
        self.kwargs['value'] = nzo_id
        return self.action()

    def nzo_delete_history_files(self, nzo_id):
        self.kwargs['mode'] = 'history'
        self.kwargs['name'] = 'delete'
        self.kwargs['value'] = nzo_id
        self.kwargs['del_files'] = '1'
        return self.action()

    def delete_history_all(self):
        self.kwargs['mode'] = 'history'
        self.kwargs['name'] = 'delete'
        self.kwargs['value'] = 'all'
        return self.action()

    def delete_history_files_all(self):
        self.kwargs['mode'] = 'history'
        self.kwargs['name'] = 'delete'
        self.kwargs['value'] = 'all'
        self.kwargs['del_files'] = '1'
        self.kwargs['failed_only'] = '1'
        return self.action() 

    def nzo_pp(self, nzo_id, value=0):
        self.kwargs['mode'] = 'change_opts'
        self.kwargs['value'] = nzo_id
        self.kwargs['value2'] = value
        return self.action()

    def switch(self, value=0, nzbname='',id=''):
        if not value in range(0,100):
            value = 0
        if nzbname:
            sab_nzo_id = self.nzo_id(nzbname)
            url = self.baseurl + "&mode=switch&value=" + str(sab_nzo_id) + "&value2=" + str(value)
            responseMessage = self._sabResponse(url)
        elif id:
            url = self.baseurl + "&mode=switch&value=" + str(id) + "&value2=" + str(value)
            responseMessage = self._sabResponse(url)
        else:
            responseMessage = "no name or id for job switch provided"
        if "0" or "-1 1" in responseMessage:
            responseMessage = "ok"
        return responseMessage

    def repair(self, nzbname='',id=''):
        if nzbname:
            sab_nzo_id = self.nzo_id(nzbname)
            url = self.baseurl + "&mode=retry&value=" + str(sab_nzo_id)
            responseMessage = self._sabResponse(url)
        elif id:
            url = self.baseurl + "&mode=retry&value=" + str(id)
            responseMessage = self._sabResponse(url)
        else:
            responseMessage = "no name or id for repair provided"
        return responseMessage 
        
    def setStreaming(self, nzbname='',id=''):
        if (not id) and nzbname:
            id = self.nzo_id(nzbname)
        if id:
            ppMessage = self.nzo_pp(id,0)
            switchMessage = self.switch(0,'',id)
            if "ok" in (ppMessage and switchMessage):
                responseMessage = "ok"
            else:
                responseMessage = "failed setStreaming"
        else:
            responseMessage = "no name or id for setStreaming provided"
        return responseMessage

    def set_category(self, **kwargs):
        category = kwargs.get('category', None)
        nzbname = kwargs.get('nzbname', None)
        id = kwargs.get('id', None)
        url = "%s&mode=change_cat" % (self.baseurl)
        if category is None:
            if self.category is None or self.category == '':
                category = '*'
            else:
                category = self.category
        if nzbname is not None:
            id = self.nzo_id(nzbname)
        if id is not None:
            url = "%s&value=%s&value2=%s" % (url, str(id), str(category))
            responseMessage = self._sabResponse(url)
        else:
            responseMessage = "no name or id for setCategory provided"
        return responseMessage

    def _sabResponse(self, url):
        try:
            req = urllib2.Request(url)
            response = urllib2.urlopen(req)
        except:
            responseMessage = "unable to load url: " + url
        else:
            log_msg = response.read()
            response.close()
            if "ok" in log_msg:
                responseMessage = 'ok'
            else:
                responseMessage = log_msg
            utils.log("SABnzbd: _sabResponse message: %s" % log_msg)
            utils.log("SABnzbd: _sabResponse from url: %s" % url)
        return responseMessage

    def nzo_id(self, nzbname, nzb = None):
        url = self.baseurl + "&mode=queue&start=0&limit=50&output=xml"
        doc = _load_xml(url)
        nzbname = nzbname.lower().replace('.', ' ').replace('_', ' ')
        if doc:
            if doc.getElementsByTagName("slot"):
                for slot in doc.getElementsByTagName("slot"):
                    status = get_node_value(slot, "status").lower()
                    filename = get_node_value(slot, "filename").lower()
                    if nzb is not None and "grabbing" in status:
                        if nzb.lower() in filename:
                            return get_node_value(slot, "nzo_id")
                    elif not "grabbing" in status:
                        filename = filename.replace('.', ' ').replace('_', ' ')
                        if nzbname == filename:
                            return get_node_value(slot, "nzo_id")
        return None

    def nzf_id(self, sab_nzo_id, name):
        url = self.baseurl + "&mode=get_files&output=xml&value=" + str(sab_nzo_id)
        doc = _load_xml(url)
        sab_nzf_id = None
        if doc:
            if doc.getElementsByTagName("file"):
                for file in doc.getElementsByTagName("file"):
                    filename = get_node_value(file, "filename")
                    status = get_node_value(file, "status")
                    if filename.lower() == name.lower() and status == "active":
                        sab_nzf_id  = get_node_value(file, "nzf_id")
        return sab_nzf_id

    def nzf_id_list(self, sab_nzo_id, file_list):
        url = self.baseurl + "&mode=get_files&output=xml&value=" + str(sab_nzo_id)
        doc = _load_xml(url)
        sab_nzf_id_list = []
        file_nzf = dict()
        if doc:
            if doc.getElementsByTagName("file"):
                for file in doc.getElementsByTagName("file"):
                    filename = get_node_value(file, "filename")
                    status = get_node_value(file, "status")
                    if status == "active":
                        file_nzf[filename] = get_node_value(file, "nzf_id")
        for filename in file_list:
            try:
                sab_nzf_id_list.append(file_nzf[filename])
            except:
                utils.log("SABnzbd: nzf_id_list: unable to find sab_nzf_id for: %s" % filename)
        return sab_nzf_id_list

    def nzo_id_history(self, nzbname):
        start = 0
        limit = 20
        noofslots = 21
        nzbname = nzbname.lower().replace('.', ' ').replace('_', ' ')
        while limit <= noofslots:
            url = self.baseurl + "&mode=history&start=" +str(start) + "&limit=" + str(limit) + "&failed_only=1&output=xml"
            doc = _load_xml(url)
            if doc:
                history = doc.getElementsByTagName("history")
                noofslots = int(get_node_value(history[0], "noofslots"))
                if doc.getElementsByTagName("slot"):
                    for slot in doc.getElementsByTagName("slot"):
                        filename = get_node_value(slot, "name").lower().replace('.', ' ').replace('_', ' ')
                        if filename == nzbname:
                            return get_node_value(slot, "nzo_id")
                start = limit + 1
                limit = limit + 20
            else:
                limit = 1
                noofslots = 0
        return None

    def nzo_id_history_list(self, nzbname_list):
        start = 0
        limit = 20
        noofslots = 21
        sab_nzo_id = None
        while limit <= noofslots and not sab_nzo_id:
            url = self.baseurl + "&mode=history&start=" +str(start) + "&limit=" + str(limit) + "&failed_only=1&output=xml"
            doc = _load_xml(url)
            if doc:
                history = doc.getElementsByTagName("history")
                noofslots = int(get_node_value(history[0], "noofslots"))
                if doc.getElementsByTagName("slot"):
                    for slot in doc.getElementsByTagName("slot"):
                        filename = get_node_value(slot, "name").lower().replace('.', ' ').replace('_', ' ')
                        for row in nzbname_list:
                            if filename == row[0].lower().replace('.', ' ').replace('_', ' '):
                                row[1] = get_node_value(slot, "nzo_id")
                start = limit + 1
                limit = limit + 20
            else:
                limit = 1
                noofslots = 0
        return nzbname_list

    def file_list(self, id=''):
        url = self.baseurl + "&mode=get_files&output=xml&value=" + str(id)
        doc = _load_xml(url)
        file_list = []
        if doc:
            if doc.getElementsByTagName("file"):
                for file in doc.getElementsByTagName("file"):
                    status = get_node_value(file, "status")
                    if status == "active":
                        row = []
                        filename = get_node_value(file, "filename")
                        row.append(filename)
                        bytes = get_node_value(file, "bytes")
                        bytes = int(bytes.replace(".00",""))
                        row.append(bytes)
                        file_list.append(row)
        return file_list

    def file_list_position(self, sab_nzo_id, sab_nzf_id, position):
        action = { -1 : 'Delete',
                    0 : 'Top',
                    1 : 'Up',
                    2 : 'Down',
                    3 : 'Bottom'}
        url = "http://" + self.ip + ":" + self.port + "/sabnzbd/nzb/" + sab_nzo_id + "/bulk_operation?session=" \
              + self.apikey + "&action_key=" + action[position]
        for nzf_id in sab_nzf_id:
            url = url + "&" + nzf_id + "=on"
        try:
            req = urllib2.Request(url)
            response = urllib2.urlopen(req)
        except:
            utils.log("SABnzbd: file_list_position: unable to load url: %s" % url)
            utils.notification("SABnzbd failed moving file to top of queue")
            return None
        response.close()
        return

    def category_list(self):
        url = self.baseurl + "&mode=get_config&section=categories&output=xml"
        doc = _load_xml(url)
        category_list = []
        if doc:
            if doc.getElementsByTagName("category"):
                for category in doc.getElementsByTagName("category"):
                    category = get_node_value(category, "name")
                    category_list.append(category)
        return category_list

    def misc_settings_dict(self):
        url = self.baseurl + "&mode=get_config&section=misc&output=xml"
        doc = _load_xml(url)
        settings_dict = dict()
        if doc:
            if doc.getElementsByTagName("misc"):
                for misc in doc.getElementsByTagName("misc")[0].childNodes:
                    try:
                        settings_dict[misc.tagName] = misc.firstChild.data
                    except:
                        pass
        return settings_dict

    def setup_streaming(self):
        # 1. test the connection
        # 2. check allow_streaming
        # 3. set allow streaming if missing
        url = self.baseurl + "&mode=version&output=xml"
        try:
            req = urllib2.Request(url)
            response = urllib2.urlopen(req)
        except:
            utils.log("SABnzbd: setup_streaming: unable to conncet to SABnzbd: %s" % url)
            return "ip"
        xml = response.read()
        response.close()
        url = self.baseurl + "&mode=get_config&section=misc&keyword=allow_streaming&output=xml"
        doc = _load_xml(url)
        if doc.getElementsByTagName("result"):
            return "apikey"
        allow_streaming = "0"
        if doc.getElementsByTagName("misc"):
            allow_streaming = get_node_value(doc.getElementsByTagName("misc")[0], "allow_streaming")
        if not allow_streaming == "1":
            url = self.baseurl + "&mode=set_config&section=misc&keyword=allow_streaming&value=1"
            _load_xml(url)
            return "restart"
        return "ok"

def get_node_value(parent, name, ns=""):
    if ns:
        return unicode(parent.getElementsByTagNameNS(ns, name)[0].childNodes[0].data.encode('utf-8'), 'utf-8')
    else:
        return unicode(parent.getElementsByTagName(name)[0].childNodes[0].data.encode('utf-8'), 'utf-8')

def _load_url(url):
        utils.log("SABnzbd: _load_url: url: %s" % url)
        headers = { 'User-Agent' : 'Xbmc/12.0 (Addon; plugin.program.sabnzbd)' }
        req = urllib2.Request(url, None, headers)
        try:
            response = urllib2.urlopen(req)
        except urllib2.URLError, ex:
            if hasattr(ex, 'reason'):
                utils.log("SABnzbd: _load_url: reason: %s unable to load url: %s" % \
                          (ex.reason, url))
                return None
            elif hasattr(ex, 'code'):
                utils.log("SABnzbd: _load_url: reason: %s unable to load url: %s" % \
                          (ex.code, url))
                return None
        else:
            doc = response.read()
            response.close()
            return doc

def _load_xml(url):
    utils.log("SABnzbd: _load_xml: url: %s" % url)
    try:
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
    except:
        utils.log("SABnzbd: _load_xml: unable to load url: %s" % url)
        utils.notification("SABnzbd down")
        return None
    xml = response.read()
    response.close()
    try:
        out = parseString(xml)
    except:
        utils.log("SABnzbd: _load_xml: malformed xml from url: %s" % url)
        utils.notification("SABnzbd malformed xml")
        return None
    return out

def _load_json(url):
    utils.log("SABnzbd: _load_json: url: %s" % url)
    try:
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
    except:
        utils.log("SABnzbd: _load_json: unable to load url: %s" % url)
        utils.notification("SABnzbd down")
        return None
    resp = response.read()
    response.close()
    try:
     out = json.loads(resp)
    except:
        utils.log("SABnzbd: _load_json: malformed json from url: %s" % url)
        utils.notification("SABnzbd malformed json")
        return None
    return out

class Queue:
    def __init__(self, sabnzbd, start=0, limit=50):
        self.sabnzbd = sabnzbd
        self.nzo_list = []
        url = "%s&mode=queue&start=%s&limit=%s&output=json" % \
              (self.sabnzbd.baseurl, start, limit)
        doc = _load_json(url)
        if doc:
            for key, value in doc["queue"].items():
                setattr(self, key, value)
            if self.slots:
                for slot in self.slots:
                    nzo = NzoObject(slot)
                    self.nzo_list.append(nzo)

    def nzo(self, nzo_id):
        for m_nzo in self.nzo_list:
            if nzo_id == m_nzo.nzo_id:
                return m_nzo
            else:
                pass
        return None

class NzoObject:
    def __init__(self, slot):
        for key, value in slot.items():
            setattr(self, key, value)

class History:
    def __init__(self, sabnzbd, start=0, limit=50):
        self.sabnzbd = sabnzbd
        self.failed_only = 0
        self.nzo_list = []
        url = "%s&mode=history&start=%s&limit=%s&failed_only=%s&output=json" % \
              (self.sabnzbd.baseurl, start, limit, self.failed_only)
        doc = _load_json(url)
        if doc:
            for key, value in doc["history"].items():
                setattr(self, key, value)
            if self.slots:
                for slot in self.slots:
                    nzo = NzoObject(slot)
                    self.nzo_list.append(nzo)
        self.len_slots = len(self.nzo_list)

    def nzo(self, nzo_id):
        for m_nzo in self.nzo_list:
            if nzo_id == m_nzo.nzo_id:
                return m_nzo
            else:
                pass
        return None

class Nzo(Queue):
    # legacy class present due to pneumatic
    def __init__(self, sabnzbd, nzo_id):
        self.is_in_queue = False
        Queue.__init__(self, sabnzbd)
        import inspect
        for n, v in inspect.getmembers(self.nzo(nzo_id)):
            setattr(self, n, v)
    
    def _get_nzf_list(self):
        out_list = []
        out_dict = dict()
        url = "%s&mode=get_files&output=json&value=%s" % (self.sabnzbd.baseurl, str(self.nzo_id))
        doc = _load_json(url)
        if doc:
            files = doc["files"]
            if files:
                i = 0
                for file in files:
                    nzf = Nzf(**file)
                    out_list.append(nzf)
                    out_dict[file['filename']] = i
                    i+= 1
        return out_list, out_dict

    def nzf_list(self):
        try:
            nzf_list, nzf_dict = self._get_nzf_list()
            return nzf_list
        except:
            return None

    def get_nzf(self, name):
        try:
            nzf_list, nzf_dict = self._get_nzf_list()
            return nzf_list[nzf_dict[name]]
        except:
            return None

    def get_nzf_id(self, nzf_id):
        nzf_list, nzf_dict = self._get_nzf_list()
        out = None
        for nzf in nzf_list:
            if nzf_id == nzf.nzf_id:
                out = nzf
                break
        return out

class Nzf:
    def __init__(self, **kwargs):
        self.status = kwargs.get('status')
        self.mb = kwargs.get('mb', 0)
        self.age = kwargs.get('age')
        self.bytes = kwargs.get('bytes', 0)
        self.filename = kwargs.get('filename')
        self.subject = kwargs.get('subject', self.filename)
        self.mbleft = kwargs.get('mbleft', 0)
        self.nzf_id = kwargs.get('nzf_id', None)
        self.id = kwargs.get('id')

class Warnings:
    def __init__(self, sabnzbd):
        self.sabnzbd = sabnzbd

    def warnings(self):
        url = "%s&mode=warnings&output=json" % self.sabnzbd.baseurl
        doc = _load_json(url)
        if doc:
            out = []
            for i in range(len(doc['warnings'])):
                out.append(doc['warnings'][i].replace('\n', ' '))
                i+=1
            return out
        else:
            return []

    def clear(self):
        url = "http://%s:%s/status/clearwarnings?session=%s" % \
              (self.sabnzbd.ip, self.sabnzbd.port, self.sabnzbd.apikey)
        _load_url(url)
