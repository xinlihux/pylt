#!/usr/bin/env python

#    Copyright (c) 2007 Corey Goldberg (corey@goldb.org)
#    License: GNU GPLv2
#
#    This file is part of PyLT.
#
#    PyLT is free software; you can redistribute it and/or modify it 
#    under the terms of the GNU General Public License as published 
#    by the Free Software Foundation; either version 2 of the License,
#    or (at your option) any later version.



import time
import sys
import wx
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin
from threading import Thread
import xml.etree.ElementTree as etree
from pylt_engine import *

 

    
class Application(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, 'PyLT - Web Performance', size=(680, 710))
        
        self.runtime_stats = {}  # shared dictionary for storing runtime stats
        self.error_queue = []  # shared list for storing errors
        
        self.SetIcon(wx.Icon('ui/icon.ico', wx.BITMAP_TYPE_ICO))
        self.CreateStatusBar()
        
        menuBar = wx.MenuBar()
        file_menu = wx.Menu()
        file_menu.Append(101, '&About', 'About PyLT')
        file_menu.Append(102, '&Exit', 'Exit PyLT')
        wx.EVT_MENU(self, 101, self.on_about)
        wx.EVT_MENU(self, 102, self.on_exit)
        menuBar.Append(file_menu, '&File')
        self.SetMenuBar(menuBar)
        
        panel = wx.Panel(self)
        
        self.run_btn = wx.Button(panel, -1, 'Run')
        self.stop_btn = wx.Button(panel, -1, 'Stop')
        self.pause_btn = wx.Button(panel, -1, 'Pause Monitoring')
        self.resume_btn = wx.Button(panel, -1, 'Resume Monitoring')
        self.busy_gauge = wx.Gauge(panel, -1, 0, size=(60, 12))
        self.busy_timer = wx.Timer(self)  # timer for gauge pulsing

        self.num_agents_spin = wx.SpinCtrl(panel, -1, size=(55, -1))
        self.num_agents_spin.SetRange(1, 1000000)
        self.num_agents_spin.SetValue(1)
        self.interval_spin = wx.SpinCtrl(panel, -1, size=(75, -1))
        self.interval_spin.SetRange(0, 1000000)
        self.interval_spin.SetValue(1000)
        self.rampup_spin = wx.SpinCtrl(panel, -1, size=(55, -1))
        self.rampup_spin.SetRange(0, 1000000)
        self.rampup_spin.SetValue(0)
        
        # workload controls
        controls_sizer = wx.GridSizer(0, 4, 0, 0)
        controls_sizer.Add(wx.StaticText(panel, -1, 'Agents (count)'), 0, wx.TOP, 5)
        controls_sizer.Add(self.num_agents_spin, 0, wx.ALL, 2)
        controls_sizer.Add(wx.StaticText(panel, -1, 'Interval (ms)'), 0, wx.TOP, 5)
        controls_sizer.Add(self.interval_spin, 0, wx.ALL, 2)
        controls_sizer.Add(wx.StaticText(panel, -1, 'Rampup (s)'), 0, wx.TOP, 5)
        controls_sizer.Add(self.rampup_spin, 0, wx.ALL, 2)
        
        # run controls
        runcontrols_sizer = wx.BoxSizer(wx.HORIZONTAL)
        runcontrols_sizer.Add(self.run_btn, 0, wx.ALL, 3)
        runcontrols_sizer.Add(self.stop_btn, 0, wx.ALL, 3)
        runcontrols_sizer.Add(controls_sizer, 0, wx.LEFT, 55)
        runcontrols_sizer.Add(self.busy_gauge, 0, wx.LEFT, 65)
        
        summary_monitor_text = wx.StaticText(panel, -1, 'Summary')
        summary_monitor_text.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
        
        agent_monitor_text = wx.StaticText(panel, -1, 'Agent Monitor')
        agent_monitor_text.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
        
        error_text = wx.StaticText(panel, -1, 'Errors')
        error_text.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
        
        self.total_statlist = AutoWidthListCtrl(panel, height=45)
        self.total_statlist.InsertColumn(0, 'Run Time', width=100)
        self.total_statlist.InsertColumn(1, 'Requests', width=100)
        self.total_statlist.InsertColumn(2, 'Errors', width=100)
        self.total_statlist.InsertColumn(3, 'Avg Resp Time', width=100)
        self.total_statlist.InsertColumn(4, 'Avg Throughput', width=100)
        self.total_statlist.InsertColumn(5, 'Cur Throughput', width=100)
        
        self.agents_statlist = AutoWidthListCtrl(panel, height=300)
        self.agents_statlist.InsertColumn(0, 'Agent Num', width=100)
        self.agents_statlist.InsertColumn(1, 'Status', width=100)
        self.agents_statlist.InsertColumn(2, 'Requests', width=100)
        self.agents_statlist.InsertColumn(3, 'Last Resp Code', width=100)
        self.agents_statlist.InsertColumn(4, 'Last Resp Time', width=100)
        self.agents_statlist.InsertColumn(5, 'Avg Resp Time', width=100)
        
        self.error_list = wx.TextCtrl(panel, -1, style=wx.TE_MULTILINE, size=(500, 100))
        self.error_list.SetOwnForegroundColour(wx.RED)
        
        pause_resume_sizer = wx.BoxSizer(wx.HORIZONTAL)
        pause_resume_sizer.Add(self.pause_btn, 0, wx.ALL, 3)
        pause_resume_sizer.Add(self.resume_btn, 0, wx.ALL, 3)
        
        monitor_sizer = wx.BoxSizer(wx.VERTICAL)
        monitor_sizer.Add(summary_monitor_text, 0, wx.ALL, 3)
        monitor_sizer.Add(self.total_statlist, 0, wx.EXPAND, 0)
        monitor_sizer.Add(agent_monitor_text, 0, wx.ALL, 3)
        monitor_sizer.Add(self.agents_statlist, 0, wx.EXPAND, 0)
        monitor_sizer.Add(error_text, 0, wx.ALL, 3)
        monitor_sizer.Add(self.error_list, 0, wx.EXPAND, 0)
        monitor_sizer.Add(pause_resume_sizer, 0, wx.ALL, 3)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(runcontrols_sizer, 0, wx.ALL, 3)
        sizer.Add(monitor_sizer, 0, wx.LEFT, 33)
        
        # bind the events to handlers
        self.Bind(wx.EVT_BUTTON, self.on_run, self.run_btn)
        self.Bind(wx.EVT_BUTTON, self.on_stop, self.stop_btn)
        self.Bind(wx.EVT_BUTTON, self.on_pause, self.pause_btn)
        self.Bind(wx.EVT_BUTTON, self.on_resume, self.resume_btn)
        self.Bind(wx.EVT_TIMER, self.timer_handler)
                
        self.switch_status(False)
        panel.SetSizer(sizer)        
        self.Centre()
        self.Show(True)
        

    def on_about(self, evt):
        info = wx.AboutDialogInfo()
        info.SetName('PyLT')
        info.SetCopyright('Copyright %s 2007 Corey Goldberg' % u'\u00A9')
        info.SetDescription('\nPyLT is Free Open Source Software\nLicense:  GNU GPL')
        wx.AboutBox(info)

    
    def on_exit(self, evt):    
        sys.exit(0)
        
        
    def timer_handler(self, evt):
        self.busy_gauge.Pulse()
        
        
    def on_run(self, evt):
        # reset stats and errors in case there was a previous run since startup
        self.runtime_stats = {}
        self.error_queue = []
        
        # get values from UI controls
        num_agents = self.num_agents_spin.GetValue()
        interval = self.interval_spin.GetValue() / 1000.0  # converted from millisecs to secs
        rampup = self.rampup_spin.GetValue()
        lm = LoadManager(num_agents, interval, rampup, 10, self.runtime_stats, self.error_queue)
        self.lm = lm

        try:
            cases, config = self.load_xml_cases()
            for req in cases:
                lm.add_req(req)
        except:
            # there was a problem getting cases from the xml file
            dial = wx.MessageDialog(None, 'create a valid testcases.xml', 'Error', wx.OK | wx.ICON_ERROR)
            dial.ShowModal()
            cases = None
        
        if cases != None:  # only run if we have valid cases
            self.start_time = time.time()    
            
            lm.setDaemon(True)
            lm.start()
            
            self.rt_mon = RTMonitor(self.start_time, self.runtime_stats, self.error_queue, self.agents_statlist, self.total_statlist, self.error_list)
            self.rt_mon.error_list.Clear()
            
            self.rt_mon.setDaemon(True)
            self.rt_mon.start()
            
            self.switch_status(True)
        
        
    def on_stop(self, evt):
        self.lm.stop()
        self.rt_mon.stop()
        self.switch_status(False)
        
        
    def on_pause(self, evt):
        self.pause_btn.Disable()
        self.resume_btn.Enable()
        self.rt_mon.stop()
        
        
    def on_resume(self, evt):
        self.pause_btn.Enable()
        self.resume_btn.Disable()
        
        self.rt_mon = RTMonitor(self.start_time, self.runtime_stats, self.error_queue, self.agents_statlist, self.total_statlist, self.error_list)
        self.rt_mon.setDaemon(True)
        self.rt_mon.start()
        

    def load_xml_cases(self):
        # parse xml and load request queue
        dom = etree.parse('testcases.xml')
        cases = []
        for child in dom.getiterator():
            if child.tag != dom.getroot().tag and child.tag =='case':
                for element in child:
                    if element.tag == 'url':
                        req = Request()                
                        req.url = element.text
                    if element.tag == 'method': 
                        req.method = element.text
                    if element.tag == 'body': 
                        req.body = element.text
                    if element.tag == 'headers': 
                        req.headers = element.text
                cases.append(req)
            if child.tag != dom.getroot().tag and child.tag == 'config':
                for element in child:
                    if element.tag == 'agents':
                        cfg = Config()                
                        cfg.agents = element.text
                    if element.tag == 'interval':
                        cfg.interval = element.text
                    if element.tag == 'rampup':
                        cfg.rampup = element.text
        return (cases, cfg)
   
        
    def switch_status(self, is_on):
        # change the status gauge and swap run/stop buttons
        if is_on:
            self.run_btn.Disable()
            self.stop_btn.Enable()
            self.pause_btn.Enable()
            self.resume_btn.Disable()
            self.num_agents_spin.Disable()
            self.interval_spin.Disable()
            self.rampup_spin.Disable()
            self.busy_timer.Start(75)
        else:
            self.run_btn.Enable()
            self.stop_btn.Disable()
            self.pause_btn.Disable()
            self.resume_btn.Disable()
            self.num_agents_spin.Enable()
            self.interval_spin.Enable()
            self.rampup_spin.Enable()
            self.busy_timer.Stop()




class AutoWidthListCtrl(wx.ListCtrl, ListCtrlAutoWidthMixin):
    def __init__(self, parent, height=100, width=605):
        wx.ListCtrl.__init__(self, parent, -1, size=(width, height), style=wx.LC_REPORT|wx.LC_HRULES)
        ListCtrlAutoWidthMixin.__init__(self)
        


class RTMonitor(Thread):  # real time monitor.  runs in its own thread so we don't block UI events      
    def __init__(self, start_time, runtime_stats, error_queue, agents_statlist, total_statlist, error_list):
        Thread.__init__(self)
        
        # references to shared data stores         
        self.runtime_stats = runtime_stats
        self.error_queue = error_queue
        
        # references to list widgets
        self.agents_statlist = agents_statlist  
        self.total_statlist = total_statlist
        self.error_list = error_list
        
        self.start_time = start_time
        self.refresh_rate = 3.0
        
        
    def run(self):
        self.running = True
        last_count = 0  # to calc current throughput
        while self.running:
            # refresh total monitor
            elapsed_secs = int(time.time() - self.start_time)  # running time in secs
            ids = self.runtime_stats.keys()
            agg_count = sum([self.runtime_stats[id].count for id in ids])  # total req count
            agg_total_latency = sum([self.runtime_stats[id].total_latency for id in ids])
            agg_error_count = sum([self.runtime_stats[id].error_count for id in ids])
            if agg_count > 0 and elapsed_secs > 0:
                agg_avg = agg_total_latency / agg_count  # total avg response time
                throughput = float(agg_count) / elapsed_secs  # avg throughput since start
                interval_count = agg_count - last_count  # requests since last refresh
                cur_throughput = float(interval_count) / self.refresh_rate  # throughput since last refresh
                last_count = agg_count  # reset for next time
            else: 
                agg_avg = 0
                throughput = 0
                cur_throughput = 0
            self.total_statlist.DeleteAllItems()       
            index = self.total_statlist.InsertStringItem(sys.maxint, self.humanize_time(elapsed_secs))
            self.total_statlist.SetStringItem(index, 1, '%d' % agg_count)
            self.total_statlist.SetStringItem(index, 2, '%d' % agg_error_count)
            self.total_statlist.SetStringItem(index, 3, '%.3f' % agg_avg)
            self.total_statlist.SetStringItem(index, 4, '%.3f' % throughput)
            self.total_statlist.SetStringItem(index, 5, '%.3f' % cur_throughput)
            
            # refresh agents monitor
            self.agents_statlist.DeleteAllItems()       
            for id in self.runtime_stats.keys():
                count = self.runtime_stats[id].count
                index = self.agents_statlist.InsertStringItem(sys.maxint, '%d' % (id + 1))
                self.agents_statlist.SetStringItem(index, 2, '%d' % count)
                if count == 0:
                    self.agents_statlist.SetStringItem(index, 1, 'waiting')
                    self.agents_statlist.SetStringItem(index, 3, '-')
                    self.agents_statlist.SetStringItem(index, 4, '-')
                    self.agents_statlist.SetStringItem(index, 5, '-')
                else:
                    self.agents_statlist.SetStringItem(index, 1, 'running')
                    self.agents_statlist.SetStringItem(index, 3, '%d' % self.runtime_stats[id].status)
                    self.agents_statlist.SetStringItem(index, 4, '%.3f' % self.runtime_stats[id].latency)
                    self.agents_statlist.SetStringItem(index, 5, '%.3f' % self.runtime_stats[id].avg_latency)
            
            # refresh error monitor            
            for error in self.error_queue:
                # pop error strings off the queue and render them in the monitor
                self.error_list.AppendText('%s\n' % self.error_queue.pop(0))
            self.error_list.ShowPosition(self.error_list.GetLastPosition()) # scroll to end 
                
            # sleep until next refresh    
            time.sleep(self.refresh_rate)
    
    
    def stop(self):
        self.running = False
    
    
    def humanize_time(self, secs):
        # convert secs (int) into a human readable time string:  hh:mm:ss
        mins, secs = divmod(secs, 60)
        hours, mins = divmod(mins, 60)
        if hours < 10:
            hours = '0%d' % hours
        else:
            hours = str(hours)
        if mins < 10:
            mins = '0%d' % mins
        else:
            mins = str(mins)
        if secs < 10:
            secs = '0%d' % secs
        else:
            secs = str(secs)
        return '%s:%s:%s' % (hours, mins, secs)
            
        
        
class AboutFrame(wx.Frame):
    def __init__(self, parent, ID, title):
        wx.Frame.__init__(self, parent, -1, title, pos=(0, 0), size=(320, 240))
        self.SetIcon(wx.Icon('ui/icon.ico', wx.BITMAP_TYPE_ICO))
        panel = wx.Panel(self, -1)
        
        content = """\
PyLT - Web Performance
Copyright (c) 2007 Corey Goldberg
PyLT is Free Open Source Software
License:  GNU GPL
        """
        text = wx.StaticText(panel, -1, content, wx.Point(10, 10))
        text.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
        
        


class Config():
    def __init__(self, agents=1, interval=1, rampup=0):
        self.agents = agents
        self.interval = interval
        self.rampup = rampup
            
            

def main():
    app = wx.App(0)
    Application(None)
    app.MainLoop()            

if __name__ == '__main__':
    main()
