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

import xbmc
import xbmcgui

import utils
import sabnzbd

SABNZBD = sabnzbd.Sabnzbd().init_api

class NzoAction:
    def __init__ (self, **kwargs):
        utils.log("NzoAction: kwargs: %s" % kwargs)
        for key, value in kwargs.items():
            setattr(self, key, value)

    def nzo_pause(self):
        message = SABNZBD.nzo_pause(self.nzo_id)
        utils.container_refresh()
        utils.notification("Jobb paused: %s" % message)

    def nzo_resume(self):
        message = SABNZBD.nzo_resume(self.nzo_id)
        utils.container_refresh()
        utils.notification("Jobb resumed: %s" % message)

    def nzo_up(self):
        self._switch(-1)

    def nzo_down(self):
        self._switch(1)

    def _switch(self, value):
        sab = SabAction()
        sab.sab_kwargs['mode'] = 'switch'
        sab.sab_kwargs['value'] = self.nzo_id
        sab.sab_kwargs['value2'] = int(self.index) + value
        sab.sab_action()
        utils.container_refresh()

    def nzo_category(self):
        dialog = xbmcgui.Dialog()
        category_list = SABNZBD.category_list()
        utils.log("nzo_category: category_list: %s" % category_list)
        category_list.remove('*')
        category_list.insert(0, 'Default')
        ret = dialog.select('Select SABnzbd category', category_list)
        if ret <= 0:
            return
        else:
            category = category_list[ret]
            utils.log("nzo_category: category: %s" % category)
            sab = SabAction()
            sab.sab_kwargs['mode'] = 'change_cat'
            sab.sab_kwargs['value'] = self.nzo_id
            sab.sab_kwargs['value2'] = category
            sab.sab_action()
            utils.container_refresh()

    def nzo_pp(self):
        dialog = xbmcgui.Dialog()
        pp_list = ['Download', '+Repair', '+Unpack', '+Delete']
        ret = dialog.select('SABnzbd Post process', pp_list)
        print ret
        if ret == -1:
            return
        else:
            utils.log("nzo_pp: pp: %s" % ret)
            sab = SabAction()
            sab.sab_kwargs['mode'] = 'change_opts'
            sab.sab_kwargs['value'] = self.nzo_id
            sab.sab_kwargs['value2'] = ret
            sab.sab_action()
            utils.container_refresh()

class NzfAction:
    def __init__ (self, **kwargs):
        utils.log("NzfAction: kwargs: %s" % kwargs)
        for key, value in kwargs.items():
            setattr(self, key, value)

    def nzf_delete(self):
        self._file_list_position(-1)

    def nzf_top(self):
        self._file_list_position(0)

    def nzf_up(self):
        self._file_list_position(1)

    def nzf_down(self):
        self._file_list_position(2)

    def nzf_bottom(self):
        self._file_list_position(3)

    def _file_list_position(self, pos):
        SABNZBD.file_list_position(self.nzo_id, [self.nzf_id], pos)
        utils.container_refresh()

class SabAction:
    def __init__ (self, **kwargs):
        utils.log("SabAction: kwargs: %s" % kwargs)
        self.sab_kwargs = dict()
        for key, value in kwargs.items():
            if key.startswith('sab_'):
                key = key.replace('sab_', '')
                self.sab_kwargs[key] = value
            else:
                setattr(self, key, value)

    def sab_add_nzb(self):
        dialog = xbmcgui.Dialog()
        nzb_file = dialog.browse(1, 'Add a nzb', 'files', '.nzb|.zip|.gz|.rar')
        path = nzb_file
        if utils.exists(path):
            message = SABNZBD.add_file(path)
            utils.notification("SAB File added")
            utils.container_refresh()

    def sab_max_speed(self):
        dialog = xbmcgui.Dialog()
        ret = dialog.numeric(0, 'SABnzbd Max speed  in KB/s')
        if ret is not "":
            self.sab_kwargs['mode'] = 'config'
            self.sab_kwargs['name'] = 'speedlimit'
            self.sab_kwargs['value'] = int(ret)
            message = self.sab_action()
            utils.container_refresh()

    def sab_reset_speed(self):
        self.sab_kwargs['mode'] = 'config'
        self.sab_kwargs['name'] = 'speedlimit'
        self.sab_kwargs['value'] = ''
        message = self.sab_action()
        utils.container_refresh()

    def sab_pause(self):
        message = SABNZBD.pause()
        utils.container_refresh()
        utils.notification("SAB paused: %s" % message)

    def sab_resume(self):
        message = SABNZBD.resume()
        utils.container_refresh()
        utils.notification("Queue resumed: %s" % message)

    def sab_queue_delete_files(self):
        # nzo_queue_delete_files
        self.sab_kwargs['value'] = self.nzo_id
        self.sab_kwargs['mode'] = 'queue'
        self.sab_kwargs['name'] = 'delete'
        self.sab_kwargs['del_files'] = '1'
        message = self.sab_action()
        utils.container_refresh()
        utils.notification("Delete: %s" % message)

    def sab_history_delete(self):
        if 'value' not in self.sab_kwargs:
            self.sab_kwargs['value'] = self.nzo_id
        self.sab_kwargs['mode'] = 'history'
        self.sab_kwargs['name'] = 'delete'
        message = self.sab_action()
        utils.container_refresh()
        utils.notification("Remove: %s" % message)

    def sab_history_delete_all(self):
        dialog = xbmcgui.Dialog()
        ret = dialog.yesno('SABnzbd History', 'Remove whole history', 'Are you sure?')
        if ret:
            self.sab_kwargs['value'] = 'all'
            self.sab_history_delete()

    def sab_history_delete_files(self):
        self.sab_kwargs['del_files'] = '1'
        self.sab_kwargs['failed_only'] = '1'
        self.sab_history_delete()

    def sab_history_delete_files_all(self):
        dialog = xbmcgui.Dialog()
        ret = dialog.yesno('SABnzbd History', 'Remove all failed + delete files', 'Are you sure?')
        if ret:
            self.sab_kwargs['value'] = 'all'
            self.sab_kwargs['del_files'] = '1'
            self.sab_kwargs['failed_only'] = '1'
            self.sab_history_delete()

    def sab_retry(self):
        # TODO
        # dialog = xbmcgui.Dialog()
        # ret = dialog.yesno('SABnzbd Retry', 'Add optional supplemental NZB?', '# TODO')
        # if ret:
            # dialog = xbmcgui.Dialog()
            # nzb_file = dialog.browse(0, 'Pick a folder', 'files')
            # # XBMC outputs utf-8
            # path = unicode(nzb_file, 'utf-8')
        # else:
        self.sab_kwargs['mode'] = 'retry'
        self.sab_kwargs['value'] = self.nzo_id
        message = self.sab_action()
        utils.container_refresh()
        utils.notification("Retry: %s" % message)

    def sab_restart(self):
        self.sab_kwargs['mode'] = 'restart'
        message = self.sab_action()
        utils.parent_dir()

    def sab_shutdown(self):
        self.sab_kwargs['mode'] = 'shutdown'
        message = self.sab_action()
        utils.parent_dir()

    def sab_action(self):
        return SABNZBD.action(**self.sab_kwargs)

    def sab_clear_warnings(self):
        sabnzbd.Warnings(SABNZBD).clear()
        utils.parent_dir()
