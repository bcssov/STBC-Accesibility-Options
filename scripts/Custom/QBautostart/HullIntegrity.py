# THIS FILE IS NOT SUPPORTED BY ACTIVISION
# THIS FILE IS UNDER THE LGPL LICENSE AS WELL
# HullIntegrity.py
# 1st March 2025, by USS Sovereign, and tweaked by Noat and Alex SL Gato (CharaToLoki)
#         Inspired by the Shield Percentages mod by Defiant. It was originally made pre-2010 with the goal of showing lots of accessibility options, such as for colorblind people.
#
# Modify, redistribute to your liking. Just remember to give credit where due.
#################################################################################################################

import App
import MissionLib
import string

#
# noinspection SpellCheckingInspection
MODINFO = {"Author": "\"USS Sovereign\" (mario0085), Noat (noatblok),\"Alex SL Gato\" (andromedavirgoa@gmail.com)",
           "Version": "0.12",
           "License": "LGPL",
           "Description": "Read the small title above for more info"
           }
#
#################################################################################################################
#

sPath = "Custom.UnifiedMainMenu.ConfigModules.Options.SavedConfigs.AccessibilityConfigVals"
sCPath = "Custom.UnifiedMainMenu.ConfigModules.Options.AccessibilityConfig"

pModule = __import__(sPath)
pConfigModule = __import__(sCPath)

pText = None
pHealth = None
pTimer = None
pMission = None
pOriginalWidth = 1
pOriginalHeight = 1
firstTime = 1

globalVarList = {
    "ShowPercent": 0,
    "ShowBar": 1,
    "ShowFraction": 0,
    "NumberDecimals": 0,
    "RadixNotation": ".",
    "sFont": "Crillee",
    "FontSize": 5,
}


def CheckAndRefreshModule(pMyModule, theWay,
                          issue=0):  # Used when for example you had an incomplete BC Accessibility Config values
    if not pMyModule:
        pMyModule = __import__(theWay)
    elif pMyModule or issue > 0:
        global pModule
        # noinspection PyUnresolvedReferences
        reload(pModule)
        pMyModule = __import__(theWay)
        pModule = pMyModule

    global globalVarList
    if pMyModule is not None and issue == 0:
        for variable in globalVarList.keys():
            if hasattr(pMyModule, variable):
                globalVarList[variable] = getattr(pMyModule, variable)
            else:
                print(theWay, " on cache has no ", variable, " attribute.")
                issue = issue + 1


def RefreshConfig(pObject, _pEvent):
    print("Saved mid-game, refreshing configuration...")
    CheckAndRefreshModule(pModule, sPath, 0)
    global pText, firstTime

    if pModule is None:
        return

    # Grab health gauge
    pTCW = App.TacticalControlWindow_GetTacticalControlWindow()
    if not pTCW:
        return
    pDisplay = pTCW.GetShipDisplay()
    if not pDisplay:
        return

    global pHealth, firstTime

    if not pHealth:
        pHealth = pDisplay.GetHealthGauge()

    if not pHealth:
        return

    firstTime = 1
    # This line hides the health gauge which is replaced by the percentage text
    if globalVarList["ShowBar"] == 0:
        pHealth.SetNotVisible(0)
    else:
        pHealth.SetVisible(0)

    if globalVarList["ShowPercent"] or globalVarList["ShowFraction"]:
        wasNone = 0
        if pText is None:
            pText = App.TGParagraph_Create("Hull :          100%", 1.0, None, globalVarList["sFont"],
                                           globalVarList["FontSize"])
            wasNone = 1
        else:
            pText.SetFontGroup(App.g_kFontManager.GetFontGroup(globalVarList["sFont"], globalVarList["FontSize"]))

        if globalVarList["ShowFraction"]:
            howRight = 0
        else:
            howRight = pHealth.GetRight() * 0.8 - pText.GetWidth()

        if wasNone != 0:
            pDisplay.AddChild(pText, howRight, pHealth.GetBottom())

    else:
        if pText is not None:  # "Hiding" in a way...
            pText.SetString("")
        pDisplay.SetFixedSize(pOriginalWidth, pOriginalHeight)
        pHealth.Resize(pDisplay.GetMaximumInteriorWidth(), pHealth.GetHeight(), 0)

    pDisplay.InteriorChangedSize()
    # pDisplay.Layout()
    pObject.AddHandler()  # shipSwapChecker.AddHandler()

    global pTimer
    if not pTimer:
        pTimer = Watcher()


def ShipCheck(_pObject, _pEvent):  # Underscore to shut up pycharm
    global firstTime
    firstTime = 1


# noinspection PyMethodMayBeStatic
class ShipSwapCheckClass:
    def __init__(self, name):
        self.name = name
        self.pEventHandler = App.TGPythonInstanceWrapper()
        # noinspection PyUnresolvedReferences
        self.pEventHandler.SetPyWrapper(self)
        self.AddSHandler()

    def ShipCheck(self, _pEvent):  # Somehow I cannot call this function... but the global one I pretty much can...
        global firstTime
        firstTime = 1

    def AddHandler(self):
        self.RemoveHandler()
        App.g_kEventManager.AddBroadcastPythonFuncHandler(App.ET_SET_PLAYER, self.pEventHandler,
                                                          __name__ + ".ShipCheck")

    def RemoveHandler(self):
        App.g_kEventManager.RemoveBroadcastHandler(App.ET_SET_PLAYER, self.pEventHandler, __name__ + ".ShipCheck")

    def AddSHandler(self):
        if pConfigModule is not None and hasattr(pConfigModule,
                                                 "ET_SAVED_CONFIG") and pConfigModule.ET_SAVED_CONFIG is not None:
            App.g_kEventManager.RemoveBroadcastHandler(pConfigModule.ET_SAVED_CONFIG, self.pEventHandler,
                                                       __name__ + ".RefreshConfig")
            App.g_kEventManager.AddBroadcastPythonFuncHandler(pConfigModule.ET_SAVED_CONFIG, self.pEventHandler,
                                                              __name__ + ".RefreshConfig")

    def RemoveSHandler(self):
        if pConfigModule is not None and hasattr(pConfigModule,
                                                 "ET_SAVED_CONFIG") and pConfigModule.ET_SAVED_CONFIG is not None:
            App.g_kEventManager.RemoveBroadcastHandler(pConfigModule.ET_SAVED_CONFIG, self.pEventHandler,
                                                       __name__ + ".RefreshConfig")


shipSwapChecker = ShipSwapCheckClass("Ship Swap checker")

CheckAndRefreshModule(pModule, sPath, 0)


def init():
    CheckAndRefreshModule(pModule, sPath, 0)

    if pModule is None:
        return

    # Grab health gauge
    pTCW = App.TacticalControlWindow_GetTacticalControlWindow()
    if not pTCW:
        return
    pDisplay = pTCW.GetShipDisplay()
    if not pDisplay:
        return

    global pHealth, firstTime
    pHealth = pDisplay.GetHealthGauge()
    if not pHealth:
        return

    firstTime = 1
    # This line hides the health gauge which is replaced by the percentage text
    if globalVarList["ShowBar"] == 0:
        pHealth.SetNotVisible(0)

    global pOriginalWidth, pOriginalHeight
    pOriginalWidth = pDisplay.GetWidth()
    pOriginalHeight = pDisplay.GetHeight()

    # Create the text
    global pText
    if globalVarList["ShowPercent"]:
        pText = App.TGParagraph_Create("Hull :          100%", 1.0, None, globalVarList["sFont"],
                                       globalVarList["FontSize"])
    elif globalVarList["ShowFraction"]:
        pText = App.TGParagraph_Create("Hull :          100/100", 1.0, None, globalVarList["sFont"],
                                       globalVarList["FontSize"])

    if not pText:
        return

    # print(pHealth.GetPosition) # Sov had this

    if globalVarList["ShowFraction"]:
        howRight = 0
    else:
        howRight = pHealth.GetRight() * 0.8 - pText.GetWidth()

    pDisplay.AddChild(pText, howRight, pHealth.GetBottom())

    # Decided to do the size change on the Active Watcher as the first time, so init only gathers data and appends these
    # newWidth = pOriginalWidth
    # if (1.05 * pText.GetWidth()) > newWidth:
    #	newWidth = pText.GetWidth() * 1.05 #pOriginalWidth + pText.GetWidth()/2.0
    # pDisplay.SetFixedSize(newWidth, (pOriginalHeight + pText.GetHeight()))
    # pHealth.Resize(pDisplay.GetMaximumInteriorWidth(), pHealth.GetHeight(), 0)
    pDisplay.InteriorChangedSize()

    # When you change a player ship then initiate the script
    shipSwapChecker.AddHandler()

    global pTimer
    if not pTimer:
        pTimer = Watcher()


# noinspection PyShadowingBuiltins
def exit():
    global pText, pHealth, pTimer
    pText = None
    pHealth = None
    pTimer = None

    shipSwapChecker.RemoveSHandler()
    shipSwapChecker.RemoveHandler()


class Watcher:
    def __init__(self):
        self.iDec = None
        self.iCon = None
        self.iExact = None
        self.fHullMax = None
        self.fHullCurr = None
        self.pTimer = None
        self.StartTiming()

    # noinspection PyUnresolvedReferences
    def StartTiming(self):
        if self.pTimer:
            return
        if not globalVarList["ShowPercent"] and not globalVarList["ShowFraction"]:
            return
        self.pTimer = App.PythonMethodProcess()
        self.pTimer.SetInstance(self)
        self.pTimer.SetFunction("Update")
        self.pTimer.SetDelay(1)
        self.pTimer.SetPriority(App.TimeSliceProcess.LOW)

    def Update(self, _fTime):

        pPlayer = MissionLib.GetPlayer()
        if not pPlayer:
            return

        global pText
        if pText is not None:

            pHull = pPlayer.GetHull()

            if not pHull or not hasattr(pHull, "GetMaxCondition"):
                return

            self.fHullCurr = pHull.GetCondition()
            self.fHullMax = pHull.GetMaxCondition()
            if not self.fHullCurr or not self.fHullMax or self.fHullMax == 0.0:
                # noinspection PyUnresolvedReferences
                pText.SetString("Hull : N/A")
                return

            self.iExact = self.fHullCurr / self.fHullMax
            self.iCon = int(self.iExact * 100)

            infoString = ""

            if globalVarList["ShowPercent"]:
                auxPercString = ""
                if globalVarList["NumberDecimals"] > 0:
                    self.iDec = string.zfill(int(self.iExact * 100 * (10 ** globalVarList["NumberDecimals"])) - int(
                        self.iCon * (10 ** globalVarList["NumberDecimals"])), globalVarList["NumberDecimals"])
                    auxPercString = auxPercString + str(globalVarList["RadixNotation"]) + str(self.iDec)
                infoString = infoString + str(self.iCon) + auxPercString + "%"
                if not globalVarList["ShowFraction"]:
                    infoString = "          " + infoString
                else:
                    infoString = " " + infoString
            if globalVarList["ShowFraction"]:
                if self.fHullMax <= 1.0:
                    signifyDec = 6
                else:
                    signifyDec = globalVarList["NumberDecimals"]

                currHullApprox = int(self.fHullCurr)
                maxHullApprox = int(self.fHullMax)

                if signifyDec >= 1:
                    # noinspection PyBroadException
                    try:
                        currHullDecApprox = string.zfill(
                            int(int(self.fHullCurr * (10 ** signifyDec)) - (currHullApprox * (10 ** signifyDec))),
                            signifyDec)
                    except:
                        # Floats of the scale that cause problems, over 2^64, are likely to lose precision anyway. So hm, just place 0, or this calculation?
                        currHullDecApprox = str(self.fHullCurr % 1.0)[2:(2 + signifyDec)]
                    # noinspection PyBroadException
                    try:
                        maxHullDecApprox = string.zfill(
                            int(int(self.fHullMax * (10 ** signifyDec)) - (maxHullApprox * (10 ** signifyDec))),
                            signifyDec)
                    except:
                        maxHullDecApprox = str(self.fHullMax % 1.0)[2:(2 + signifyDec)]

                    sCurrHull = str(currHullApprox) + str(globalVarList["RadixNotation"]) + str(currHullDecApprox)
                    sMaxHull = str(maxHullApprox) + str(globalVarList["RadixNotation"]) + str(maxHullDecApprox)
                else:
                    sCurrHull = str(currHullApprox)
                    sMaxHull = str(maxHullApprox)

                auxString = str(sCurrHull) + "/" + str(sMaxHull)
                if globalVarList["ShowPercent"]:
                    auxString = "(" + auxString + ")"
                infoString = infoString + " " + auxString

            if globalVarList["ShowFraction"] or globalVarList["ShowPercent"]:
                # noinspection PyUnresolvedReferences
                pText.SetString("Hull :" + infoString)

        global pHealth

        if not pHealth:
            pTCW = App.TacticalControlWindow_GetTacticalControlWindow()
            if not pTCW:
                return
            pDisplay = pTCW.GetShipDisplay()
            if not pDisplay:
                return
            pHealth = pDisplay.GetHealthGauge()
            return

        if not pHealth:
            return

        if pHealth.IsVisible() and globalVarList["ShowBar"] == 0:
            pHealth.SetNotVisible(0)
        elif not pHealth.IsVisible() and globalVarList["ShowBar"] == 1:
            pHealth.SetVisible(0)

        global firstTime
        if firstTime > 0:
            pTCW = App.TacticalControlWindow_GetTacticalControlWindow()
            if not pTCW:
                return
            pDisplay = pTCW.GetShipDisplay()
            if not pDisplay:
                return
            firstTime = 0
            newWidth = pOriginalWidth
            extraHeight = 0
            if (globalVarList["ShowFraction"] or globalVarList["ShowPercent"]) and pText is not None:
                # noinspection PyUnresolvedReferences
                if (1.05 * pText.GetWidth()) > newWidth:
                    # noinspection PyUnresolvedReferences
                    newWidth = pText.GetWidth() * 1.05
                # noinspection PyUnresolvedReferences
                extraHeight = pText.GetHeight()

            pDisplay.SetFixedSize(newWidth, (pOriginalHeight + extraHeight))
            pHealth.Resize(pDisplay.GetMaximumInteriorWidth(), pHealth.GetHeight(), 0)
            pDisplay.InteriorChangedSize()
    # pDisplay.Layout()
