import xbmc, xbmcgui, xbmcaddon, os, platform, json, zipfile, urllib, re
import subprocess
import time

from urlparse import urljoin
from shutil import copyfile
 
#get actioncodes from https://github.com/xbmc/xbmc/blob/master/xbmc/guilib/Key.h
ACTION_PREVIOUS_MENU = 10
ACTION_SELECT_ITEM = 7

ACTION_MOVE_LEFT = 1
ACTION_MOVE_RIGHT = 2
ACTION_MOVE_UP = 3
ACTION_MOVE_DOWN = 4

ACTION_PAGE_UP = 5
ACTION_PAGE_DOWN = 6

ACTION_SHOW_INFO = 11
ACTION_STOP = 13
ACTION_NEXT_ITEM = 14
ACTION_PREV_ITEM = 15

ACTION_SHOW_GUI = 18

ACTION_SHOW_PLAYLIST = 33
ACTION_SHOW_FULLSCREEN = 36

ACTION_PLAYER_PLAY = 79

ACTION_NAV_BACK = 92
ACTION_CONTEXT_MENU = 117

REMOTE_0 = 58
REMOTE_1 = 59
REMOTE_2 = 60
REMOTE_3 = 61
REMOTE_4 = 62
REMOTE_5 = 63
REMOTE_6 = 64
REMOTE_7 = 65
REMOTE_8 = 66
REMOTE_9 = 67

# resolution values
#1080i = 0
#720p = 1
#480p = 2
#480p16x9 = 3
#ntsc = 4
#ntsc16x9 = 5
#pal = 6
#pal16x9 = 7
#pal60 = 8
#pal6016x9 = 9

class MyClass(xbmcgui.Window):

  # ------------ init ------------
  def __init__(self):
  
    self.setResolution(0)
                
    self.ADDON = xbmcaddon.Addon(id='script.web.browser')  
    self.FPATH = xbmc.translatePath(self.ADDON.getAddonInfo('path')).decode("utf-8")
    self.PHANTOMJS = xbmc.translatePath(self.ADDON.getSetting('file')).decode("utf-8") 
    
    self.CACHE = xbmc.translatePath("special://temp").decode("utf-8") 
    self.WEB = os.path.join(self.CACHE, 'web')
    self.FAV = os.path.join(self.CACHE, 'fav')
        
    # create dir
    if not os.path.exists(self.WEB):
        os.makedirs(self.WEB)
    # create dir
    if not os.path.exists(self.FAV):
        os.makedirs(self.FAV)
    
    #reload thumbs
    if (self.ADDON.getSetting('reload') == "true"):    
        self.deleteFavorites()
        self.ADDON.setSetting('reload', 'false')
        
    # load picture to avoid caching
    BACKG = os.path.join(self.FPATH,'background.png')
    self.image = xbmcgui.ControlImage(0, 70, 1920, 1080,filename = BACKG)
    self.addControl(self.image)
    
    # top bar
    BACKTOP = os.path.join(self.FPATH, 'webviewer-title-background.png') 
    self.backTop = xbmcgui.ControlImage(0, 0, 1920, 70, BACKTOP)
    self.addControl(self.backTop)
    
    # link
    self.strLink = xbmcgui.ControlLabel(100, 16, 1200, 70, '', 'font14', '0xFF000000')
    self.addControl(self.strLink)
    self.strLink.setLabel('about:blank')
         
    # id
    self.strID = xbmcgui.ControlLabel(1600, 16, 1700, 70, '', 'font16', '0xFF000000')
    self.addControl(self.strID) 
    self.strID.setLabel('')
    
    # zoom
    self.strZoom = xbmcgui.ControlLabel(1750, 16, 1850, 70, '', 'font16', '0xFF000000')
    self.addControl(self.strZoom) 
    self.strZoom.setLabel('100%')
    
    # play symbol
    self.play = xbmcgui.ControlImage(1400, 5, 130, 60, filename = 'OSDPlay.png', aspectRatio = 0)
    self.addControl(self.play)
    self.play.setVisible(False)
    
    # get favorites
    self.LINKS = [self.ADDON.getSetting('fav01'),self.ADDON.getSetting('fav02'),
        self.ADDON.getSetting('fav03'),self.ADDON.getSetting('fav04'),
        self.ADDON.getSetting('fav05'),self.ADDON.getSetting('fav06'),
        self.ADDON.getSetting('fav07'),self.ADDON.getSetting('fav08'),
        self.ADDON.getSetting('fav09')]
    
    for i in xrange(0, 9):
        if(self.LINKS[i] != ''):
            self.doCache(self.LINKS[i],"fav0" + str(i+1) + ".jpg")
    
    # make homepage
    self.makeHTML()
    
    # load homepage
    if (self.ADDON.getSetting('show') == "true"):  
        homepage = "file:///" + self.FPATH + '/home.html'
    else:
        homepage = self.ADDON.getSetting('home')  
    
    #get zoom
    self.ZOOM = float(self.ADDON.getSetting('zoom'))
    
    # init history
    self.HISTORY = []
    self.HISTORY.append(homepage)
    
    # show homepage
    self.loadPage(homepage);
    self.showPage()
  
  # ------------ on Action ------------
  def onAction(self, action):
    
    #self.strLink.setLabel(str(action.getId()))
    
    # ------------ prev. menu ------------
    if action == ACTION_PREVIOUS_MENU:
      self.close()
    # ------------ nav. back ------------
    if action == ACTION_NAV_BACK:
      self.close()
      
    # ------------ play ------------
    if action == ACTION_PLAYER_PLAY:
    
      save = os.path.join(self.CACHE, 'web','video.txt') 
             
      if(os.path.exists(save)): 
          size = os.path.getsize(save)
          if (size != 0):
              data = ''
	      
	      with open(save, 'r') as infile:
	          data = infile.read()
	                
              my_list = data.splitlines()
              if (len(my_list) != 0):
                  dialog = xbmcgui.Dialog()
                  value = dialog.select('Select video', my_list )
                  
                  if(value >= 0):
                      xbmc.Player().play(my_list[value])
    
    # ------------ stop ------------
    if action == ACTION_STOP:
         
        #homepage = self.ADDON.getSetting('home')	    
	homepage = "file:///" + self.FPATH + '/home.html'		    
	
	self.HISTORY.append(homepage)
	
	self.loadPage(homepage);
	self.showPage()
    
    # ------------ prev. item ------------
    if action == ACTION_PREV_ITEM:
       
        cnt = len(self.HISTORY)       
        if(cnt > 1):

            link = self.HISTORY.pop()
            link = self.HISTORY[cnt-2]
            
	    self.loadPage(link)
	    self.showPage()
	    
    # ------------ next item ------------        
    if action == ACTION_NEXT_ITEM:

        keyboard = xbmc.Keyboard('http://','Enter link')
	keyboard.doModal()
	if (keyboard.isConfirmed()):
	
	   self.HISTORY.append(keyboard.getText())
	
	   self.loadPage(keyboard.getText())   
	   self.showPage()
    
    # ------------ context menu ------------
    if action == ACTION_CONTEXT_MENU:
    
        dialog = xbmcgui.Dialog()
	value = dialog.numeric( 0, "Link No.", "" )
	
	if(value <> ''):    
            intValue = int(value)
            self.loadLinkNo(intValue)
    
    # ------------ select ------------
    if action == ACTION_SELECT_ITEM:

        sel = int(self.select)
        self.loadLinkNo(sel)

    # ------------ keys 0-9 ------------
    if action == REMOTE_0:
      self.select = self.select + '0'
    if action == REMOTE_1:
      self.select = self.select + '1'
    if action == REMOTE_2:
      self.select = self.select + '2'
    if action == REMOTE_3:
      self.select = self.select + '3'
    if action == REMOTE_4:
      self.select = self.select + '4'
    if action == REMOTE_5:
      self.select = self.select + '5'
    if action == REMOTE_6:
      self.select = self.select + '6'
    if action == REMOTE_7:
      self.select = self.select + '7'
    if action == REMOTE_8:
      self.select = self.select + '8'
    if action == REMOTE_9:
      self.select = self.select + '9'
   
    if(len(self.select)>4):
      self.select = self.select[1:5]
    
    if(self.select == ''):
        self.strID.setLabel('----')
    else:
        self.strID.setLabel(self.select)
    
    # ------------ move up ------------
    if action == ACTION_MOVE_UP:
      
      f = self.getDir(self.WEB)
            
      cnt = int(len(f))
      act = int(self.page)
      
      if self.page > 0:
      
        t = self.page - 1
        BACKG = os.path.join(self.CACHE, 'web',f[t]) 
    
      	if(os.path.exists(BACKG)):     
          self.page = self.page - 1
      	  self.image.setImage(BACKG, False)
    
    # ------------ move down ------------
    if action == ACTION_MOVE_DOWN:
      
      f = self.getDir(self.WEB)
      
      cnt = int(len(f))
      act = int(self.page)
      
      if act < (cnt-1):
      
          t = self.page + 1
          BACKG = os.path.join(self.CACHE, 'web',f[t]) 
      
          if(os.path.exists(BACKG)):  
            self.page = self.page + 1  	
            self.image.setImage(BACKG, False)

    # ------------ page up ------------
    if action == ACTION_PAGE_UP:
    
        if (self.ZOOM <= 1.45):
            self.ZOOM = self.ZOOM + 0.1

            self.loadPage(self.actual)   
            self.showPage()

    # ------------ page up ------------
    if action == ACTION_PAGE_DOWN:
    
        if (self.ZOOM >= 0.85):
            self.ZOOM = self.ZOOM - 0.1

            self.loadPage(self.actual)   
            self.showPage()      

  # ------------ load a page ------------
  def loadPage(self, URL):

    # disable play symbol
    self.play.setVisible(False)

    # shoy busy circle
    xbmc.executebuiltin("ActivateWindow(busydialog)") 
    
    try:
        xbmc.log('BROWSER load page ' + URL)
        
        self.deleteCache()
        
        self.strLink.setLabel(URL)
        self.strID.setLabel('----')
        self.strZoom.setLabel(str(int(self.ZOOM * 100)) + "%")
        
        self.page = 0
	self.select = ''
	self.actual = URL 
        
        self.image.setImage(os.path.join(self.FPATH,'background_load.png'), False)
    
    	zoom = self.ZOOM   	
    	if(URL.startswith('file')):
    	    zoom = 1.0
    	
    	xbmc.log('BROWSER zoom ' + str(zoom))
    	
        if(platform.system().startswith('Win')):
        
            # call phantomjs hidden for windows
            SW_HIDE = 0
            info = subprocess.STARTUPINFO()
            info.dwFlags = subprocess.STARTF_USESHOWWINDOW
            info.wShowWindow = SW_HIDE
            
            subprocess.call([self.PHANTOMJS, self.FPATH +"/load.js", URL, self.WEB + "/" , str(zoom)], startupinfo=info)
        else:
            subprocess.call(['.' + self.PHANTOMJS, self.FPATH +"/load.js", URL, self.WEB + "/" , str(zoom)])
    except Exception as e:
        xbmc.log('BROWSER ' + str(e))
        
    self.checkVideo()
    
    # finished
    xbmc.executebuiltin("Dialog.Close(busydialog)") 
  
  # ------------ show a page ------------
  def showPage(self):
  
      f = self.getDir(self.WEB)
      cnt = int(len(f))
    
      if(cnt>0):
          BACKG = os.path.join(self.CACHE, 'web',f[0]) 
          self.image.setImage(BACKG, False)  
      else:
          self.image.setImage(os.path.join(self.FPATH,'background_error.png'), False)
          xbmc.executebuiltin('Notification(Load page error,could not load, 3000)') 
      
      save = os.path.join(self.CACHE, 'web','video.txt') 
                   
      if(os.path.exists(save)): 
          size = os.path.getsize(save)
          if (size != 0):
              self.play.setVisible(True)
  
  # ------------ try to find link ID ------------
  def loadLinkNo(self, LinkNo):

      data = ''

      with open(os.path.join(self.CACHE, 'web','links.txt'), 'r') as infile:
          data = infile.read()
          
      my_list = data.splitlines()
  	
      no = '[_' + str(LinkNo) + '_]'
          
      self.select = ''
      self.strID.setLabel('')
          
      for line in my_list:
          if no in line:
                    
              self.strLink.setLabel(line)
              self.image.setImage(os.path.join(self.FPATH,'background_load.png'), False)
                  
              n1 = line.index('[_')
              no = line[:n1-1]
                  
              if(not no.startswith('http')):                 
                  no = urljoin(self.actual, no)

              self.HISTORY.append(no)
              
              self.loadPage(no)
              self.showPage()
                  
              break;
  
  # ------------ cache page picture ------------
  def doCache(self, URL, File):

      thumb = self.FAV + "/" + File

      if not os.path.exists(thumb):

          xbmc.executebuiltin('Notification(Cache thumbs,' + File +  ', 3000)') 
                    
          if(platform.system().startswith("Win")):

              # call phantomjs hidden for windows
              SW_HIDE = 0
              info = subprocess.STARTUPINFO()
              info.dwFlags = subprocess.STARTF_USESHOWWINDOW
              info.wShowWindow = SW_HIDE

              subprocess.call([self.PHANTOMJS, self.FPATH +"/thumb.js", URL, self.FAV + "/" + File], startupinfo=info)
          else:
              subprocess.call(['.' + self.PHANTOMJS, self.FPATH + "/thumb.js", URL, self.FAV + "/" + File])

  # ------------ generate home page ------------
  def makeHTML(self):
      
      f1 = open(self.FPATH + '/template.html','r')
      f2 = open(self.FPATH + '/home.html','w')
      
      html = f1.read()
      
      for i in xrange(0, 9):
          html = html.replace('http://www.link' + str(i+1) + '.com',self.ADDON.getSetting('fav0' + str(i+1))) 
           
      for i in xrange(0, 9):
          if(self.LINKS[i] != ''):
              html = html.replace('alt="fav0' + str(i+1) + '.jpg" src="template.png"','alt="fav0' + str(i+1) + '.jpg" src="file:///' + self.FAV + '\\fav0' + str(i+1) + '.jpg"')
          else:
              html = html.replace('alt="fav0' + str(i+1) + '.jpg" src="template.png"','alt="fav0' + str(i+1) + '.jpg" src="file:///' + self.FPATH + '\\template.png"')
    
      f2.write(html)
      
      f1.close()
      f2.close()
      
  # ------------ check for video links ------------
  def checkVideo(self):
        
      file = os.path.join(self.CACHE, 'web','page.html') 
      save = os.path.join(self.CACHE, 'web','video.txt') 
       
      if(os.path.exists(file)): 
          f1 = open(file,'r')  
          html = f1.read()
          f1.close()
      
          f2 = open(save,'w')
      
          pattern = '(\'|\")http:([^(\'|\")]*)mp4([^(\'|\")]*)(\'|\")'
          for m in re.finditer(pattern, html):
              vid = m.group(0).replace('\'','').replace('\"','')
              vid = vid.replace('\/','/')
              f2.write(vid + '\n')
              
          f2.close()
  
  # ------------ get cache dir pictures ------------
  def getDir(self, path):
    list = [s for s in os.listdir(path) if s.endswith('.jpg')]
    list.sort()
    return list
  
  # ------------ delete the cache ------------
  def deleteCache(self):
            
    if os.path.exists(self.WEB):
        for f in os.listdir(self.WEB):
            fpath = os.path.join(self.WEB, f)
            try:
                if os.path.isfile(fpath):
                    os.unlink(fpath)
            except Exception as e:
                xbmc.log("BROWSER " + str(e))

  # ------------ delete the favorites ------------
  def deleteFavorites(self):
            
    if os.path.exists(self.FAV):
        for f in os.listdir(self.FAV):
            fpath = os.path.join(self.FAV, f)
            try:
                if os.path.isfile(fpath):
                    os.unlink(fpath)
            except Exception as e:
                xbmc.log("BROWSER " + str(e))
  
  # ------------ set resolution ------------
  def setResolution(self, skinnedResolution):
      # get current resolution
      currentResolution = self.getResolution()
      offset = 0
      # if current and skinned resolutions differ and skinned resolution is not
      # 1080i or 720p (they have no 4:3) calculate widescreen offset
      if currentResolution != skinnedResolution and skinnedResolution > 1:
          # check if current resolution is 16x9
          if currentResolution == 0 or currentResolution % 2: iCur16x9 = 1
          else: iCur16x9 = 0
          # check if skinned resolution is 16x9
          if skinnedResolution % 2: i16x9 = 1
          else: i16x9 = 0
          # calculate offset
          offset = iCur16x9 - i16x9
      self.setCoordinateResolution(skinnedResolution + offset)

# ---------------- main call ---------------- 
mydisplay = MyClass()
mydisplay .doModal()
del mydisplay