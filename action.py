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

    def nzo_delete(self):
        message = SABNZBD.nzo_delete(self.nzo_id)
        utils.container_refresh()
        utils.notification("Delete: %s" % message)

    def nzo_delete_files(self):
        message = SABNZBD.nzo_delete_files(self.nzo_id)
        utils.container_refresh()
        utils.notification("Delete: %s" % message)

    def nzo_delete_history(self):
        message = SABNZBD.nzo_delete_history(self.nzo_id)
        utils.container_refresh()
        utils.notification("Remove: %s" % message)

    def nzo_delete_history_files(self):
        message = SABNZBD.nzo_delete_history_files(self.nzo_id)
        utils.container_refresh()
        utils.notification("Remove: %s" % message)

    def nzo_up(self):
        self._switch(-1)

    def nzo_down(self):
        self._switch(1)

    def _switch(self, value):
        message = SABNZBD.nzo_switch(self.nzo_id, (int(self.index) + value))
        utils.container_refresh()

    def nzo_category(self):
        dialog = xbmcgui.Dialog()
        category_list = sabnzbd.Queue(SABNZBD).categories
        utils.log("nzo_category: category_list: %s" % category_list)
        category_list.remove('*')
        category_list.insert(0, 'Default')
        ret = dialog.select('Select SABnzbd category', category_list)
        category_list.remove('Default')
        category_list.insert(0, '*')
        if ret == -1:
            return
        else:
            category = category_list[ret]
            utils.log("nzo_category: category: %s" % category)
            message = SABNZBD.nzo_category(self.nzo_id, category)
            utils.container_refresh()

    def nzo_pp(self):
        dialog = xbmcgui.Dialog()
        pp_list = ['Download', '+Repair', '+Unpack', '+Delete']
        ret = dialog.select('SABnzbd Post process', pp_list)
        utils.log("nzo_pp: pp: %s" % ret)
        if ret == -1:
            return
        else:
            message = SABNZBD.nzo_pp(self.nzo_id, ret)
            utils.container_refresh()

    def nzo_retry(self):
        # TODO
        # dialog = xbmcgui.Dialog()
        # ret = dialog.yesno('SABnzbd Retry', 'Add optional supplemental NZB?', '# TODO')
        # if ret:
            # dialog = xbmcgui.Dialog()
            # nzb_file = dialog.browse(0, 'Pick a folder', 'files')
            # # XBMC outputs utf-8
            # path = unicode(nzb_file, 'utf-8')
        # else:
        message = SABNZBD.nzo_retry(self.nzo_id)
        utils.container_refresh()
        utils.notification("Retry: %s" % message)

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
            message = SABNZBD.max_speed(int(ret))
            utils.container_refresh()

    def sab_reset_speed(self):
        message = SABNZBD.reset_speed()
        utils.container_refresh()

    def sab_pause(self):
        message = SABNZBD.pause()
        utils.container_refresh()
        utils.notification("SAB paused: %s" % message)

    def sab_resume(self):
        message = SABNZBD.resume()
        utils.container_refresh()
        utils.notification("Queue resumed: %s" % message)

    def sab_delete_history_all(self):
        dialog = xbmcgui.Dialog()
        ret = dialog.yesno('SABnzbd History', 'Remove whole history', 'Are you sure?')
        if ret:
            message = SABNZBD.nzo_delete_history_all(self.nzo_id)
            utils.container_refresh()
            utils.notification("Remove: %s" % message)

    def sab_delete_history_files_all(self):
        dialog = xbmcgui.Dialog()
        ret = dialog.yesno('SABnzbd History', 'Remove all failed + delete files', 'Are you sure?')
        if ret:
            message = SABNZBD.nzo_delete_history_files_all(self.nzo_id)
            utils.container_refresh()
            utils.notification("Remove: %s" % message)

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
