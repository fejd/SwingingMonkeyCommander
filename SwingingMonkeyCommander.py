import time
import os, sys
# Imports the monkeyrunner modules used by this program
from com.android.monkeyrunner import MonkeyRunner, MonkeyDevice

from javax.swing import JFrame
from javax.swing import JLabel
from javax.swing import ImageIcon
from javax.swing import JTextField
from javax.swing import JScrollPane
from javax.swing import SwingWorker, SwingUtilities

from java.lang import Runnable

from java.util import Collections
from java.util.concurrent import ExecutionException

from java.awt import BorderLayout
from java.awt.event import MouseAdapter
from java.awt.event import KeyAdapter
from java.awt.event import KeyEvent
from java.awt import KeyboardFocusManager

class SwingingMonkeyCommander(JFrame):
    '''
    A Jython tool that uses the Android SDK's monkeyrunner to communicate with
    the device. It fetches screenshots and draws them in the desktop window and
    can accept mouse and key events.
    
    Author: Fredrik Henricsson (fredrik.henricsson@gmail.com)
    '''
    def __init__(self):
        JFrame.__init__(self, "SwingingMonkeyCommander", \
                         layout=BorderLayout(), \
                         size=(505, 874), \
                         defaultCloseOperation=JFrame.EXIT_ON_CLOSE,) \

        # Include the text field later when we want to send text
        #self.textTest = JTextField()
        scriptDir = os.path.realpath(os.path.dirname(sys.argv[0]))
        self.frameIcon = ImageIcon(scriptDir + '/smcs.png')
        self.setIconImage(self.frameIcon.getImage())

        self.image = ImageIcon()
        self.label = JLabel(self.image)
        self.scrollpane = JScrollPane(JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED,
                                 JScrollPane.HORIZONTAL_SCROLLBAR_AS_NEEDED)
        #self.mouseListener = ScreenMouseListener(self)
        #self.mouseListener = ScreenMouseListener(self)
        self.scrollpane.addMouseListener(ScreenMouseListener(self))
        self.keyListener = ScreenKeyListener(self)
        self.initAndroidKeyMap()
        self.setFocusTraversalKeys(KeyboardFocusManager.FORWARD_TRAVERSAL_KEYS, Collections.EMPTY_SET);
        #self.label.addMouseListener(self.mouseListener)
        #self.addMouseListener(self.mouseListener)

        self.scrollpane.preferredSize = 480, 854
        self.scrollpane.viewport.view = self.label
        #self.label.size = (480, 854)
        self.label.preferredSize = (480, 854)
        self.add(self.scrollpane, BorderLayout.PAGE_START)
        #self.add(self.label, BorderLayout.PAGE_START)
        #self.add(self.textTest, BorderLayout.PAGE_END)
        self.show()

        self.androidDevice = None

        if self.waitForAndroidDeviceConnection() == False:
            print "Could not establish connection with device."
            return

        self.screenPullTask = ScreenPullTask(self)
        self.screenPullTask.execute()

        self.dragStart = (0,0)
        self.dragEnd = (0,0)

    def waitForAndroidDeviceConnection(self):
        maxAttempts = 5
        secondsBetweenAttempts = 5
        attempts = 0

        while(self.androidDevice == None or attempts >= maxAttempts):
            if attempts > 0:
                print "Could not connect to Android device. Trying again in 5 seconds."
                time.sleep(secondsBetweenAttempts)
            self.androidDevice = MonkeyRunner.waitForConnection()
            attempts += 1

        if self.androidDevice != None:
            return True
        else:
            return False

    def initAndroidKeyMap(self):
        # TODO: Can we use a tuple for the key and use keyCode as the first,
        # and keyLocation as the second value?
        # TODO: Need to check modifiers as well.
        # TODO: Do we need to consider the locale or does Java abstract that away?
        self.keyMap = { KeyEvent.VK_A : 'KEYCODE_A',
			KeyEvent.VK_B : 'KEYCODE_B',
			KeyEvent.VK_C : 'KEYCODE_C',
			KeyEvent.VK_D : 'KEYCODE_D',
			KeyEvent.VK_E : 'KEYCODE_E',
                        KeyEvent.VK_F : 'KEYCODE_F',
                        KeyEvent.VK_G : 'KEYCODE_G',
                        KeyEvent.VK_H : 'KEYCODE_H',
                        KeyEvent.VK_I : 'KEYCODE_I',
                        KeyEvent.VK_J : 'KEYCODE_J',
                        KeyEvent.VK_K : 'KEYCODE_K',
                        KeyEvent.VK_L : 'KEYCODE_L',
                        KeyEvent.VK_M : 'KEYCODE_M',
                        KeyEvent.VK_N : 'KEYCODE_N',
                        KeyEvent.VK_O : 'KEYCODE_O',
                        KeyEvent.VK_P : 'KEYCODE_P',
                        KeyEvent.VK_Q : 'KEYCODE_Q',
                        KeyEvent.VK_R : 'KEYCODE_R',
                        KeyEvent.VK_S : 'KEYCODE_S',
                        KeyEvent.VK_T : 'KEYCODE_T',
                        KeyEvent.VK_U : 'KEYCODE_U',
                        KeyEvent.VK_V : 'KEYCODE_V',
			KeyEvent.VK_W : 'KEYCODE_W',
                        KeyEvent.VK_X : 'KEYCODE_X',
                        KeyEvent.VK_Y : 'KEYCODE_Y',
                        KeyEvent.VK_Z : 'KEYCODE_Z',
                        KeyEvent.VK_0 : 'KEYCODE_0',
                        KeyEvent.VK_1 : 'KEYCODE_1',
                        KeyEvent.VK_2 : 'KEYCODE_2',
                        KeyEvent.VK_3 : 'KEYCODE_3',
                        KeyEvent.VK_4 : 'KEYCODE_4',
                        KeyEvent.VK_5 : 'KEYCODE_5',
                        KeyEvent.VK_6 : 'KEYCODE_6',
                        KeyEvent.VK_7 : 'KEYCODE_7',
                        KeyEvent.VK_8 : 'KEYCODE_8',
                        KeyEvent.VK_9 : 'KEYCODE_9',
                        KeyEvent.VK_NUMPAD0 : 'KEYCODE_NUMPAD_0',
                        KeyEvent.VK_NUMPAD1 : 'KEYCODE_NUMPAD_1',
                        KeyEvent.VK_NUMPAD2 : 'KEYCODE_NUMPAD_2',
                        KeyEvent.VK_NUMPAD3 : 'KEYCODE_NUMPAD_3',
                        KeyEvent.VK_NUMPAD4 : 'KEYCODE_NUMPAD_4',
                        KeyEvent.VK_NUMPAD5 : 'KEYCODE_NUMPAD_5',
                        KeyEvent.VK_NUMPAD6 : 'KEYCODE_NUMPAD_6',
                        KeyEvent.VK_NUMPAD7 : 'KEYCODE_NUMPAD_7',
                        KeyEvent.VK_NUMPAD8 : 'KEYCODE_NUMPAD_8',
                        KeyEvent.VK_NUMPAD9 : 'KEYCODE_NUMPAD_9',
                        KeyEvent.VK_BACK_SPACE : 'KEYCODE_DEL',
                        KeyEvent.VK_ENTER : 'KEYCODE_ENTER',
                        KeyEvent.VK_SPACE : 'KEYCODE_SPACE',
			KeyEvent.VK_SHIFT : 'KEYCODE_SHIFT_LEFT',
			KeyEvent.VK_CONTROL : 'KEYCODE_CONTROL_LEFT',
			KeyEvent.VK_CAPS_LOCK : 'KEYCODE_CAPS_LOCK',
			KeyEvent.VK_ESCAPE : 'KEYCODE_ESCAPE',
			KeyEvent.VK_ALT : 'KEYCODE_ALT_LEFT',
                        KeyEvent.VK_PAGE_UP : 'KEYCODE_PAGE_UP',
                        KeyEvent.VK_PAGE_DOWN : 'KEYCODE_PAGE_DOWN',
			KeyEvent.VK_LEFT : 'KEYCODE_DPAD_LEFT',
			KeyEvent.VK_RIGHT : 'KEYCODE_DPAD_RIGHT',
			KeyEvent.VK_UP : 'KEYCODE_DPAD_UP',
			KeyEvent.VK_DOWN : 'KEYCODE_DPAD_DOWN',
			KeyEvent.VK_INSERT : 'KEYCODE_INSERT',
			KeyEvent.VK_HOME : 'KEYCODE_HOME',
			KeyEvent.VK_NUM_LOCK : 'KEYCODE_NUM_LOCK',
			KeyEvent.VK_SCROLL_LOCK : 'KEYCODE_SCROLL_LOCK',
			KeyEvent.VK_PAUSE : 'KEYCODE_BREAK',
			KeyEvent.VK_TAB : 'KEYCODE_TAB',
			KeyEvent.VK_SEMICOLON : 'KEYCODE_SEMICOLON',
			}

    def sendMouseEvent(self, event):
        #TODO: Compensate for the app bar. Solve in a nicer way.
        #yAdj = 30
        # No need to compensate if the listener is in the scrollpane
        yAdj = 0
        #print "Mouse pressed: " + str(event.getX()) + " " + str(event.getY() - yAdj)
        self.androidDevice.touch(event.getX(), event.getY() - yAdj, MonkeyDevice.DOWN_AND_UP)

    def sendDragEvent(self):
        self.androidDevice.drag(self.dragStart, self.dragEnd, 1.0, 10)

    def sendKeyEvent(self, event, action):
        print event
        androidKey = ''
        #keyLocation = event.getKeyLocation()
        #if (keyLocation == KeyEvent.KEY_LOCATION_LEFT) or (keyLocation == KeyEvent.KEY_LOCATION_RIGHT):
	#    androidKey = self.keyMap[event.getKeyCode() + "_" + keyLocation]
        #else:
        
        androidKey = self.keyMap[event.getKeyCode()]
	print "Android KeyEvent: " + androidKey
        self.androidDevice.press(androidKey, action)

class ScreenMouseListener(MouseAdapter):
    def __init__(self, gui):
        MouseAdapter.__init__(self)
        self.gui = gui

    def mouseClicked(self, event):
        #print "mouseClicked"
        self.gui.sendMouseEvent(event)

    def mousePressed(self, event):
        #print "mousePressed"
        #self.gui.sendMouseEvent(event)
        self.gui.dragStart = (event.getX(), event.getY())

    def mouseReleased(self, event):
        #print "mouseReleased"
        self.gui.dragEnd = (event.getX(), event.getY())
        if self.gui.dragStart != self.gui.dragEnd:
            self.gui.sendDragEvent()

    #def mouseEntered(self, event):
        #print "mouseEntered"
        #pass

    #def mouseExited(self, event):
        #print "mouseExited"
        #pass

class ScreenKeyListener(KeyAdapter):
    def __init__(self, gui):
        KeyAdapter.__init__(self)
        self.gui = gui

    def keyPressed(self, event):
        self.gui.sendKeyEvent(event, MonkeyDevice.DOWN)
    
    def keyReleased(self, event):
        self.gui.sendKeyEvent(event, MonkeyDevice.UP)

    def keyTyped(self, event):
	if event.getKeyCode() == 0:
            # Unknown key code. Already swallowed by pressed/released?
            return
        self.gui.sendKeyEvent(event, MonkeyDevice.DOWN_AND_UP)

class ScreenPullTask(SwingWorker):
    def __init__(self, gui):
        self.gui = gui
        SwingWorker.__init__(self)
        self.androidDevice = gui.androidDevice

    def doInBackground(self):
        while not self.isCancelled():
            result = self.androidDevice.takeSnapshot()
            if result != None:
                imageBytes = result.convertToBytes("png")
                self.super__publish([imageBytes])
            time.sleep(0.1)

    def process(self, imageBytes):
        image = ImageIcon(imageBytes[0])
        self.gui.label.setIcon(image)

    def done(self):
        try:
            self.get()  #raise exception if abnormal completion
        except ExecutionException, e:
            raise SystemExit, e.getCause()

class Runnable(Runnable):
    def __init__(self, runFunction):
        self._runFunction = runFunction

    def run(self):
        self._runFunction()

if __name__ == '__main__':
    #JFrame.setDefaultLookAndFeelDecorated(True)
    SwingUtilities.invokeAndWait(Runnable(SwingingMonkeyCommander))
    #from com.android.monkeyrunner import MonkeyRunner as mr
    #from com.android.monkeyrunner.recorder import MonkeyRecorder as recorder
    #device = mr.waitForConnection()
    #recorder.start(device)
    while True:
        time.sleep(1000)
