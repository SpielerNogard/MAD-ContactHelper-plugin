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

    def log(self,info):
        self._mad['logger'].info("[ContactHelper]: "+str(info))

    def take_screenshot(self,origin):
        self.log("Making Screenshot from "+origin)
        link = self.my_mad_link+'/take_screenshot?origin='+str(origin)+"&adb=False"
        r = requests.get(link)
        self.log(r)
        time.sleep(10)
        currentDirectory = os.getcwd()
        temp_directory = currentDirectory+"/temp/"
        image_directory = currentDirectory+"/plugins/ContactHelper/Bilder/"
        device_image ="screenshot_"+ origin +".jpg"
        originscreen = image_directory+device_image
        shutil.copy2(temp_directory+device_image, image_directory+device_image)
        self.log(originscreen+" copied")
    
    def swipe_screen(self,origin):
        self.log("Swiping screen on "+origin)
        link = self.my_mad_link+'/swipe_screenshot?origin='+str(origin)+"&adb=False&clickx=60&clickxe=10&clicky=10&clickye=10"
        r = requests.get(link)
        self.log(r)
        time.sleep(10)

    def click_on_screen(self,origin,real_x,real_y):
        x = int(real_x/7.2)
        y = int(real_y/12.8)
        self.log("Clicking on "+origin)
        link = self.my_mad_link+'/click_screenshot?origin='+str(origin)+"&adb=False&clickx="+str(x)+"&clicky="+str(y)
        r = requests.get(link)
        self.log(r)
        time.sleep(10)

    def create_mad_link(self):
        self.my_mad_link = "http://"+str(self._mad_user)+":"+str(self._mad_password)+"@"+str(self._mad_adress)+":"+str(self._mad_port)

    def ContactHelper(self):
        time.sleep(120)
        while True:
            devices = ["Leveln1"]
            currentDirectory = os.getcwd()
            image_directory = currentDirectory+"/plugins/ContactHelper/Bilder/"
            for device in self._devices:
                self.take_screenshot(device)
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
                        self.log("Found Contact Screen")
                        self.swipe_screen(device)
                        self.take_screenshot(device)
                        self.handle_contact_screen(device)
                    else:
                        self.log("Contact Screen not found")




            time.sleep(1)

    def handle_contact_screen(self,device):
        currentDirectory = os.getcwd()
        image_directory = currentDirectory+"/plugins/ContactHelper/Bilder/"
        self.take_screenshot(device)
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
            time.sleep(10)

        self.take_screenshot(device)


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

        self._workers: dict = {}

        self._mad_adress = self._pluginconfig.get("plugin", "mad_adress", fallback='localhost')
        self._mad_port = self._pluginconfig.get("plugin", "mad_port", fallback='5000')
        self._mad_user = self._pluginconfig.get("plugin", "mad_user", fallback='root')
        self._mad_password = self._pluginconfig.get("plugin", "mad_password", fallback='')
        self._devices = self._pluginconfig.get("plugin", "devices", fallback='')
        
        self._devices = self._devices.replace(", ",",")
        self._devices = self._devices.split(",")
        self.log(self._devices)
        self.create_mad_link()




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
        self.template_names = ["contact","maybelater"]
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