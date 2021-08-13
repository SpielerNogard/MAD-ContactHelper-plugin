import os

from flask import Blueprint, render_template

import mapadroid.utils.pluginBase
from mapadroid.madmin.functions import auth_required

import requests
import shutil
import sched, time
from threading import Thread
import cv2 as cv
import numpy as np
from datetime import datetime
from mapadroid.utils.logging import LoggerEnums, get_logger, get_origin_logger
class ContactHelper(mapadroid.utils.pluginBase.Plugin):
    """This plugin is just the identity function: it returns the argument
    """
    def __init__(self, mad):
        super().__init__(mad)

        self._rootdir = os.path.dirname(os.path.abspath(__file__))

        self._mad = mad

        self._pluginconfig.read(self._rootdir + "/plugin.ini")
        self._versionconfig.read(self._rootdir + "/version.mpl")
        self.author = self._versionconfig.get("plugin", "author", fallback="unknown")
        self.url = self._versionconfig.get("plugin", "url", fallback="https://www.maddev.eu")
        self.description = self._versionconfig.get("plugin", "description", fallback="unknown")
        self.version = self._versionconfig.get("plugin", "version", fallback="unknown")
        self.pluginname = self._versionconfig.get("plugin", "pluginname", fallback="https://www.maddev.eu")
        self.staticpath = self._rootdir + "/static/"
        self.templatepath = self._rootdir + "/template/"

        self._routes = [
            ("/example", self.example_route),
            ("/pluginfaq", self.pluginfaq),
        ]

        self._hotlink = [
            ("Plugin faq", "pluginfaq", "Create own plugin"),
            ("Plugin Example", "example", "Testpage"),
        ]

        if self._pluginconfig.getboolean("plugin", "active", fallback=False):
            self._plugin = Blueprint(str(self.pluginname), __name__, static_folder=self.staticpath,
                                     template_folder=self.templatepath)

            for route, view_func in self._routes:
                self._plugin.add_url_rule(route, route.replace("/", ""), view_func=view_func)

            for name, link, description in self._hotlink:
                self._mad['madmin'].add_plugin_hotlink(name, self._plugin.name + "." + link.replace("/", ""),
                                                       self.pluginname, self.description, self.author, self.url,
                                                       description, self.version)

    def log(self,info,origin):
        try:
            origin_logger = get_origin_logger(self._madcontrol._logger, origin=origin)
            origin_logger.info("ContactHelper: "+str(info))

            #self._mad['logger'].info("[ContactHelper]: "+str(info))
        except:
            print("Nothing")

    def take_screen(self,origin):
        try:
            self.log("creating screen",origin)
            self._madcontrol.generate_screenshot(origin)
            currentDirectory = os.getcwd()
            temp_directory = currentDirectory+"/temp/"
            image_directory = currentDirectory+"/plugins/ContactHelper/Bilder/"
            device_image ="screenshot_"+ origin +".jpg"
            originscreen = image_directory+device_image
            try:
                shutil.copy2(temp_directory+device_image, image_directory+device_image)
                self.log(originscreen+" copied",origin)
            except:
                self.log("Cant copy file",origin)
        except:
            print("Nothing")


    def swipe(self,origin):
        try:
            real_click_x = 616
            real_click_xe = 169
            real_click_y = 658
            real_click_ye = 658
            self.log("Input Swipe",origin)
            temp_comm = self._madcontrol._ws_server.get_origin_communicator(origin)
            temp_comm.touch_and_hold(int(real_click_x), int(real_click_y), int(real_click_xe), int(real_click_ye))
        except:
            print("Nothing")

    def click_on_screen(self,origin,real_x,real_y):
        try:
            self.log("Clicking on "+origin,origin)
            temp_comm = self._madcontrol._ws_server.get_origin_communicator(origin)
            temp_comm.click(int(real_x), int(real_y))
        except:
            print("Nothing")
        
    def ContactHelper(self):
        time.sleep(60)
        while True:
            try:
                devices = ["Leveln1"]
                currentDirectory = os.getcwd()
                image_directory = currentDirectory+"/plugins/ContactHelper/Bilder/"
                for device in self._devices:
                    self.take_screen(device)
                    device_image ="screenshot_"+ device +".jpg"
                    originscreen = image_directory+device_image
                    pos = self.Watcher.find_pos("contact",originscreen)
                    if pos != None:
                        name = pos[0]
                        coords = pos[1]
                        val = pos[2]
                        x = coords[0]
                        y = coords[1]
                        if val >= 0.8:
                            self.log("Found Contact Screen",device)
                            self.swipe(device)
                            #self.swipe_screen(device)
                            self.take_screen(device)
                            #self.handle_next_screen(device)
                            
                        else:
                            self.log("Contact Screen not found",device)

                    self.handle_contact_screen(device)

            except:
                print("Fehler")




    def handle_next_screen(self,device):
        currentDirectory = os.getcwd()
        image_directory = currentDirectory+"/plugins/ContactHelper/Bilder/"
        self.take_screen(device)
        device_image ="screenshot_"+ device +".jpg"
        originscreen = image_directory+device_image
        pos = self.Watcher.find_pos("next",originscreen)
        name = pos[0]
        coords = pos[1]
        val = pos[2]
        x = coords[0]
        y = coords[1]
        if val >= 0.8:
            self.click_on_screen(device,x,y)
            

        self.take_screen(device)


    def handle_contact_screen(self,device):
        currentDirectory = os.getcwd()
        image_directory = currentDirectory+"/plugins/ContactHelper/Bilder/"
        self.take_screen(device)
        device_image ="screenshot_"+ device +".jpg"
        originscreen = image_directory+device_image
        pos = self.Watcher.find_pos("maybelater",originscreen)
        name = pos[0]
        coords = pos[1]
        val = pos[2]
        x = coords[0]
        y = coords[1]
        if val >= 0.8:
            self.click_on_screen(device,x,y)
            

        self.take_screen(device)


    def mswThread(self):
        msw_worker = Thread(name="ContactHelper", target=self.ContactHelper)
        msw_worker.daemon = True
        msw_worker.start()

    def perform_operation(self):
        """The actual implementation of the identity plugin is to just return the
        argument
        """

        # do not change this part ▽▽▽▽▽▽▽▽▽▽▽▽▽▽▽
        if not self._pluginconfig.getboolean("plugin", "active", fallback=False):
            return False
        self._mad['madmin'].register_plugin(self._plugin)
        # do not change this part △△△△△△△△△△△△△△△

        # load your stuff now
        
        #shutil.copy2('/src/dir/file.ext', '/dst/dir/newname.ext') # complete target filename given
        
        self._madcontrol = self._mad["madmin"]
        self._madcontrol = self._madcontrol.control

       
        self._devices = self._pluginconfig.get("plugin", "devices", fallback='')
        
        self._devices = self._devices.replace(", ",",")
        self._devices = self._devices.split(",")
        




        currentDirectory = os.getcwd()
        self.Watcher =watcher(self._mad,currentDirectory)
        self.mswThread()

        return True

    @auth_required
    def example_route(self):
        return render_template("testfile.html",
                               header="Test Plugin", title="Test Plugin"
                               )

    @auth_required
    def pluginfaq(self):
        return render_template("pluginfaq.html",
                               header="Test Plugin", title="Test Plugin"
                               )

class watcher(object):
    def __init__(self,mad,root_directory):
        self._mad = mad
        self.root_directory = root_directory
        self.templates = []
        self.template_names = ["contact","maybelater","next"]
        self.load_templates()

    def log(self,info):
        self._mad['logger'].info("[ContactHelper]: "+str(info))

    def load_templates(self):
        
        for Name in self.template_names:
            test = []
            test.append(Name)
            image = cv.imread(self.root_directory+"/plugins/ContactHelper/templates/"+Name+".jpg",cv.IMREAD_REDUCED_COLOR_2)
            test.append(image)
            self.templates.append(test)

    def find_pos(self, template_name, originscreen):
        try:
            ergebnis = []
            positon = self.template_names.index(template_name)
            template = self.templates[positon]

            name = template[0]
            image = template[1]
            ergebnis.append(name)
            screen = cv.imread(originscreen,cv.IMREAD_REDUCED_COLOR_2)
            result = cv.matchTemplate(screen, image, cv.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
                
            image_w = int(image.shape[1]/2)
            image_h = int(image.shape[0]/2)
            self.log("Best match top left position: %s" % str(max_loc))
            self.log("Best match confidence: %s" %max_val)
            self.log("Found "+name)
            x = (max_loc[0]+image_w)*2
            y = (max_loc[1]+image_h)*2
            werte_pos = []
            werte_pos.append(x)
            werte_pos.append(y)
            ergebnis.append(werte_pos)
            ergebnis.append(max_val)

            return(ergebnis)
        except:
            self.log("Fehler beim Template Matching")