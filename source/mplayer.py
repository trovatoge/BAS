from subprocess import Popen, PIPE
import subprocess
import sys
from time import sleep
import os
import vlc


class MPlayer():

    directory = ""
    vo = ""
    

    def __init__(self, URL = None, vo=None):
        if sys.platform == "win32":
            self.MPlayer = MPlayer.directory + '\mplayer.exe'
            #Set gl as default video for windows
            if vo is None:
                self.vo = 'gl'
            else:
                self.vo = vo
        else:
           self.MPlayer = 'mplayer'
           self.vo = vo

        self.totalTime = 0
        self.URL = ""

        if URL != None:
            self.open(URL, self.vo)


    def open(self, URL, vo=None):
        self.URL = URL
        #Hide console at startup
        
        opts = ['-slave','-quiet','-nomouseinput', URL]
        if vo is not None:
            opts = ['-vo', vo] + opts
        
        #Startupinfo doesn't work on linux?
        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            self.mp = Popen([self.MPlayer] + opts, stdin=PIPE, stdout=PIPE, startupinfo=startupinfo)
        except:
            self.mp = Popen([self.MPlayer] + opts, stdin=PIPE, stdout=PIPE)
        
        self.mp.stdin.write(b'pause\n')
        self.mp.stdin.write(b'pausing_keep_force get_property length\n')
        x = ""
        while x[0:3] != 'ANS':
            x = self.mp.stdout.readline().decode('utf8')
            print(x)

        #sleep(0.2)
        self.seek(0)
        #sleep(0.1)
        self.mp.stdin.write(b'pausing_keep_force get_property length\n')
        #sleep(0.1)
        reply = self.mp.stdout.readline().decode()
        self.totalTime = float(reply.split('=')[-1])
        

    def play(self, speed = 1):
        self.mp.stdin.write(('speed_set ' + str(speed) + '\n').encode())

    def stop(self):
        try:
            self.mp.stdin.write(b'stop \n')
        except:
            pass

    def pause(self):
        self.mp.stdin.write(b'pausing_keep_force get_property pause\n')
        reply = self.mp.stdout.readline().decode("utf-8")
        paused = reply.split("=")[1].strip()
        #Pause if not already paused, otherwise keep paused, MPlayer pause commands toggles pausing
        if paused == "no":
            self.mp.stdin.write(b'pause\n')

    def nextFrame(self):
        self.mp.stdin.write(b'pausing_keep frame_step\n')
        self.mp.stdin.write(b'pausing_keep_force get_property time_pos\n')

    def currentTime(self):
        try:
            self.mp.stdin.write(b'pausing_keep_force get_property time_pos\n')
            reply = self.mp.stdout.readline().decode()
            time = float(reply.split('=')[-1])
        except:
            time = None
        return(time)

    def seek(self, time):
        """Seek to absolute position, seconds from beginning"""
        self.mp.stdin.write(('pausing_keep seek ' + str(time) + ' 2\n').encode())

    def seekRelative(self, time):
        """Seek to relative position, seconds from current position"""
        self.mp.stdin.write(('pausing_keep seek ' + str(time) + ' 0\n').encode())

class VLC():

    directory = ""

    def __init__(self, URL = None, vo = None):
        self.totalTime = 0
        self.URL = ""

        if URL != None:
            self.open(URL)

    def open(self, URL, vo = None):
        self.URL = URL
        self.mp = vlc.MediaPlayer(URL)
        self.play()
        sleep(0.1)
        self.pause()
        self.mp.set_position(0)
        self.totalTime = self.mp.get_length()/1000.0

    def play(self, speed = 1):
        self.mp.set_rate(speed)
        self.mp.play()

    def stop(self):
        self.mp.stop()

    def pause(self):
        self.mp.set_pause(1)
        
    def nextFrame(self):
        self.mp.next_frame()
        
    def currentTime(self):
        time = self.mp.get_time()
        if time == -1:
            return None
        else:
            return(time/1000.0)

    def seek(self, time):
        """Seek to absolute position, seconds from beginning"""
        self.mp.set_time(int(time*1000))

    def seekRelative(self, time):
        """Seek to relative position, seconds from current position"""
        new = self.currentTime() + time
        self.seek(new)



class Players():
    """Open several player instances and control them as one player """

    def __init__(self, URLS=None, player = MPlayer, vo = "gl"):
        self.totalTime = 0
        self.URLS = ""

        if URLS != None:
            self.open(URLS = URLS, player = player, vo = vo)


    def open(self, URLS, player = MPlayer, vo = "gl"):
        """Open several player instances, URLS is a list of files"""
        self.players = []
        self.URLS = URLS
        for URL in URLS:
            self.players.append(player())
            self.players[-1].open(URL = URL, vo = vo)

        self.totalTime = self.players[0].totalTime

    def play(self, speed = 1):
        for player in self.players:
            player.play(speed)

    def stop(self):
        for player in self.players:
            player.stop()

    def pause(self):
        for player in self.players:
            player.pause()

            
    def nextFrame(self):
        for player in self.players:
            player.nextFrame()

    def currentTime(self):
        return(self.players[0].currentTime())
    

    def seek(self, time):
        for player in self.players:
            player.seek(time)

    def seekRelative(self, time):
        for player in self.players:
            player.seekRelative(time)

        
if __name__ == "__main__":
    #p = MPlayer()
    #p.open("d:/wildlife.wmv")
    #p.open("/media/DATA/test.mkv")
    #p2 = MPlayer()
    #p2.open("d:/wildlife.wmv")
    #p2.open("/media/DATA/test.mkv")
    p = Players(["d:/test.mkv", "d:/test.mkv"], player = VLC)
    #p.open(["d:/test.mkv", "d:/test.mkv"])
    #p.open(["e:/sika.mp4", "e:/sika2.webm"])