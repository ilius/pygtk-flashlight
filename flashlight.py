#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Copyright (C) 2012 Saeed Rasooli <saeed.gnu@gmail.com> (ilius)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License,    or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/gpl.txt>.
# Also avalable in /usr/share/common-licenses/GPL on Debian systems
# or /usr/share/licenses/common/GPL3/license.txt on ArchLinux


import os
import sys
from os.path import join, isfile

import gobject

import gtk
from gtk import gdk

def myRaise(File=None):
    i = sys.exc_info()
    (typ, value, tback) = sys.exc_info()
    text = 'line %s: %s: %s\n'%(tback.tb_lineno, typ.__name__, value)
    if File:
        text = 'File "%s", '%File + text
    sys.stderr.write(text)

color = (255,255,255)

homeDir = os.getenv('HOME')
confPath = join(homeDir, '.flashlight')
if isfile(confPath):
    try:
        exec(open(confPath).read())
    except:
        myRaise(__file__)

def saveConf():
    text = '\n'.join([
        'color = %r'%(color,),
    ])
    open(confPath, 'w').write(text)

## r, g, b in range(256)
rgbToGdkColor = lambda r, g, b, a=None: gdk.Color(int(r*257), int(g*257), int(b*257))
gdkColorToRgb = lambda gc: (gc.red//257, gc.green//257, gc.blue//257)

class FlashLightWidget(gtk.Widget):
    def __init__(self):
        gtk.Widget.__init__(self)
        self.connect('expose-event', self.onExposeEvent)
        self.connect('key-press-event', self.onKeyPress)
        self.connect('button-press-event', self.onButtonPress)
    def do_realize(self):
        self.set_flags(self.flags() | gtk.REALIZED)
        self.window = gdk.Window(
            self.get_parent_window(),
            width=self.allocation.width,
            height=self.allocation.height,
            window_type=gdk.WINDOW_CHILD,
            wclass=gdk.INPUT_OUTPUT,
            event_mask=self.get_events()
             | gdk.EXPOSURE_MASK | gtk.gdk.KEY_PRESS_MASK
             | gdk.BUTTON1_MOTION_MASK | gdk.BUTTON_PRESS_MASK
             | gdk.POINTER_MOTION_MASK | gdk.POINTER_MOTION_HINT_MASK
            #colormap=self.get_screen().get_rgba_colormap(),
        )
        self.window.set_user_data(self)
        self.style.attach(self.window)#?????? Needed??
        self.style.set_background(self.window, gtk.STATE_NORMAL)
        self.window.move_resize(*self.allocation)
    def onExposeEvent(self, widget=None, event=None):
        w = self.allocation.width
        h = self.allocation.height
        cr = self.window.cairo_create()
        cr.rectangle(0, 0, w, h)
        r, g, b = color
        cr.set_source_rgb(
            r / 255.0,
            g / 255.0,
            b / 255.0,
        )
        cr.fill()
    def onKeyPress(self, obj, event):
        kname = gdk.keyval_name(event.keyval).lower()
        if kname == 'escape':
            gtk.main_quit()
    def onButtonPress(self, obj, event):
        global color
        print event.button
        if event.button == 1:
            dialog = gtk.ColorSelectionDialog('Flashlight Color')
            if dialog.run()==gtk.RESPONSE_OK:
                color = gdkColorToRgb(dialog.get_color_selection().get_current_color())
                saveConf()
                self.queue_draw()
            dialog.destroy()


class FlashLightWindow(gtk.Window):
    def __init__(self):
        gtk.Window.__init__(self)
        self.widget = FlashLightWidget()
        self.widget.show()
        self.add(self.widget)
        self.connect('delete-event', self.onDeleteEvent)
        self.connect('key-press-event', self.onKeyPress)
    def onDeleteEvent(self, obj, event):
        gtk.main_quit()
    def onKeyPress(self, obj, event):
        kname = gdk.keyval_name(event.keyval).lower()
        if kname == 'escape':
            gtk.main_quit()


gobject.type_register(FlashLightWidget)

if __name__=='__main__':
    win = FlashLightWindow()
    win.present()
    win.fullscreen()
    gtk.main()




