# THIS FILE IS NOT SUPPORTED BY ACTIVISION
# THIS FILE IS UNDER THE LGPL LICENSE AS WELL
# AccessibilityConfig.py
# 2nd March 2025, by USS Sovereign, and tweaked by Noat and Alex SL Gato (CharaToLoki)
#         Inspired by the Shield Percentages mod by Defiant. It was originally made pre-2010 with the goal of showing lots of accessibility options, such as for colorblind people.
#
# Modify, redistribute to your liking. Just remember to give credit where due.
#################################################################################################################
# 0.13 Update: if your installation has the "scripts/FontExtension.py" script (which extends the TGFontManager class with functions which track and return font list and default font) called at the very beginning, now it will fetch Fonts automatically and will ignore manual additions. However, the script still supports 0.12 ("Legacy") manual additions, which the script will fall back to in case of Sovereign's file (or equivalent) not being present.
# This latter method consists on manually importing a font list from files located at the "extraConfigPath" indicated below. From there people can add fonts.
# But remember, before adding a new font to this script (or to all scripts, also applies for >= 0.13):
# 1. The font file must exist beforehand. For new fonts, a new proper file (like those font files at script/Icons) must have already been created first.
# 2. That font must have been registered to the App.g_kFontManager, in a not dissimilar way to the line used on scripts/Icons/FontsAndIcons.py: "App.g_kFontManager.RegisterFont("Crillee", 5, "Crillee5", "LoadCrillee5")" (first parameter being the font name, second font size, third the actual file located at scripts/Icons/ and finally the function inside that file that actually takes care of loading the new font for that size).
# Below, we have a legacy example file used for listing the Default fonts that a regular BC Install has into our AccessibilityConfig script, on a file called DefaultFonts.py:
"""
# THIS FILE IS NOT SUPPORTED BY ACTIVISION
# THIS FILE IS UNDER THE LGPL LICENSE AS WELL
# DefaultFonts.py
# 1st March 2025, by Alex SL Gato (CharaToLoki)
# Version: 1.0
# Meant to be used alongside the AccessibilityConfig UMM option (located at scripts/Custom/UnifiedMainMenu/ConfigModules/Options/), this file must be under scripts/Custom/UnifiedMainMenu/ConfigModules/Options/AccessibilityConfigFiles
##################################
# This file takes care of listing the default Fonts and Sizes that a regular STBC install supports.
dFont = {
    "Crillee": [5, 6, 9, 12, 15],
    "LCARSText": [5, 6, 9, 12, 15],
    "Tahoma": [8, 14],
    "Arial": [8],
    "Serpentine": [12],
}
"""

import App
import string
import nt
import traceback

# noinspection SpellCheckingInspection
MODINFO = {"Author": "\"USS Sovereign\" (mario0085), Noat (noatblok),\"Alex SL Gato\" (andromedavirgoa@gmail.com)",
           "Version": "0.13",
           "License": "LGPL",
           "Description": "Read the small title above for more info"
           }
#
#################################################################################################################
#

LCARS = __import__(App.GraphicsModeInfo_GetCurrentMode().GetLcarsModule())

pModule = None
# noinspection PyBroadException
try:
    pModule = __import__("SavedConfigs.AccessibilityConfigVals")
except:
    pModule = None

configPath = "scripts\\Custom\\UnifiedMainMenu\\ConfigModules\\Options\\SavedConfigs\\AccessibilityConfigVals.py"

ET_SAVED_CONFIG = App.UtopiaModule_GetNextEventType()  # You may wonder, ¿why? Because it is actually possible to play a mission and have access to the Customize configurations on the fly as long as the last Configure Window you opened was Customize
ET_SELECT_BUTTON = App.UtopiaModule_GetNextEventType()

sSaveButton = "Save Config"
sSaveNotSaved = "Save Config: Unsaved changes. Save to apply."
canChangeSave = None
saveMsgDelay = 1  # in seconds
dConfig = {}

issues = 0  # To prevent another case like Galaxy Charts wrong configuration values breaking an entire install - yes, like KCS' case.


# noinspection PyTypeChecker
def SaveConfig():
    file = nt.open(configPath, nt.O_WRONLY | nt.O_TRUNC | nt.O_CREAT | nt.O_BINARY)
    nt.write(file, "ShowPercent = " + str(dConfig["ShowPercent"]))
    nt.write(file, "\nShowBar = " + str(dConfig["ShowBar"]))
    nt.write(file, "\nShowFraction = " + str(dConfig["ShowFraction"]))
    nt.write(file, "\nNumberDecimals = " + str(dConfig["NumberDecimals"]))
    nt.write(file, "\nRadixNotation = \"" + str(dConfig["RadixNotation"]) + "\"")
    nt.write(file, "\nsFont = \"" + str(dConfig["sFont"]) + "\"")
    nt.write(file, "\nFontSize = " + str(dConfig["FontSize"]))
    nt.close(file)

    # Because of shenanigans with menu being available during QB on KM, you can sometimes access modify and save configurations mid-game. We may want to notify other related scripts that this has happened!
    pEvent = App.TGStringEvent_Create()
    pEvent.SetEventType(ET_SAVED_CONFIG)
    # pEvent.SetDestination(None)
    pEvent.SetString("SAVED BC ACCESSIBILITY")
    App.g_kEventManager.AddEvent(pEvent)


def SafeConfigStatement(variable, pMyModule, default, issue=0):
    # noinspection PyBroadException
    try:
        if pMyModule is not None and hasattr(pMyModule, variable):
            myVariable = getattr(pMyModule, variable)
        else:
            # print(configPath, " has no ", variable, " attribute. This will be addressed")
            myVariable = default
            issue = issue + 1
    except:
        traceback.print_exc()
        myVariable = default
        issue = issue + 1

    return myVariable, issue


# noinspection GrazieInspection
dRadixNotation = [
    [",", "Comma (,)"],
    [".", "Lower point (.)"],
    ["·", "Middle point (·)"],  # TO-DO LOOK FOR ALTERNATIVE
    ["'", "Apostrophe (')"],  # Apparently "’" cannot be understood by the game
]
dFont = {
    #	"Crillee": [5, 6, 9, 12, 15],
    #	"LCARSText": [5, 6, 9, 12, 15],
    #	"Tahoma": [8, 14],
    #	"Arial": [8],
    #	"Serpentine": [12],
}

_g_dExcludeSomePlugins = {
    # Some random plugins that I don't want to risk people attempting to load using this tech
    "__init__": 1,
}


def FuseTwoLists(l1, l2):
    def gen_dict(*args):
        d = {}
        for k in args:
            for item in k:
                d[item] = item
        return d.keys()

    result = list(gen_dict(l1, l2))
    result.sort()
    return result


# Based on LoadExtraPlugins by Dasher42 and MLeo's, but heavily modified so it only imports a few things

font = App.g_kFontManager.GetDefaultFontInfo()
fonts = App.g_kFontManager.GetFontList()

defaultFont = font.name
defaultSize = font.size
for font in fonts:
    lst = []
    # noinspection PyUnresolvedReferences
    if dFont.has_key(font.name):
        lst = dFont[font.name]
    else:
        dFont[font.name] = lst
    lst.append(font.size)

listedFonts = list(dFont.keys())
listedFonts.sort()
if defaultFont not in dFont.keys():
    defaultFont = listedFonts[0]
if defaultSize not in dFont[defaultFont]:
    defaultSize = dFont[defaultFont][0]

dConfig["ShowPercent"], issues = SafeConfigStatement("ShowPercent", pModule, 0, issues)
dConfig["ShowBar"], issues = SafeConfigStatement("ShowBar", pModule, 1, issues)
dConfig["ShowFraction"], issues = SafeConfigStatement("ShowFraction", pModule, 0, issues)

dConfig["NumberDecimals"], issues = SafeConfigStatement("NumberDecimals", pModule, 0, issues)
dConfig["RadixNotation"], issues = SafeConfigStatement("RadixNotation", pModule, ".", issues)

dConfig["sFont"], issues = SafeConfigStatement("sFont", pModule, defaultFont, issues)
dConfig["FontSize"], issues = SafeConfigStatement("FontSize", pModule, defaultSize, issues)

pFontSubMenu = None
sBaseFMenu = "Font Selection: "
sSeparator = ", size "

# sColor = {"Default": [], } # TO-DO DIFFERENT HEALTH BAR COLORS? ALSO, TGParagraph.SetColor:
# TO-DO MAKE IT SO IT SAVES THE ORIGINAL App colors, and then it temporarily replaces its values.

if issues > 0:
    # print("Re-applying a safe save Accessibility Config")
    # noinspection PyBroadException
    try:
        SaveConfig()
    except:
        traceback.print_exc()


def GetName():
    return "Hull Indicator Options"


# Builds our menu.  Remember to add the "return App.TGPane_Create(0,0)" command!
def CreateMenu(pOptionsPane, pContentPanel, _bGameEnded=0):
    global pFontSubMenu

    CreateButton("Show Health Bar", pContentPanel, pOptionsPane, pContentPanel, __name__ + ".BarToggle",
                 isChosen=dConfig["ShowBar"], isToggle=1)
    CreateButton("Show Health Percent", pContentPanel, pOptionsPane, pContentPanel, __name__ + ".PercentToggle",
                 isChosen=dConfig["ShowPercent"], isToggle=1)
    CreateButton("Show Health Fraction", pContentPanel, pOptionsPane, pContentPanel, __name__ + ".FractionToggle",
                 isChosen=dConfig["ShowFraction"], isToggle=1)

    CreateTextEntryButton("Number of decimals: ", pContentPanel, pOptionsPane, pContentPanel, "NumberDecimals",
                          __name__ + ".HandleKeyboardGoBetween")
    CreateMultipleChoiceButton("Radix Notation: ", pContentPanel, pOptionsPane, pContentPanel, __name__ + ".SelectNext",
                               "RadixNotation", dRadixNotation, EventInt=0)

    pFontSubMenu = CreateFontMenu(sBaseFMenu + str(dConfig["sFont"]) + str(sSeparator) + str(dConfig["FontSize"]),
                                  pContentPanel, pOptionsPane, pContentPanel)

    return App.TGPane_Create(0, 0)


def BarToggle(_object, event):
    # global ShowBar
    global dConfig
    dConfig["ShowBar"] = not dConfig["ShowBar"]
    App.STButton_Cast(event.GetSource()).SetChosen(
        dConfig["ShowBar"])  # Found method to get the button from BridgePlugin.py

    SaveConfig()


def PercentToggle(_object, event):
    # global ShowPercent
    global dConfig
    dConfig["ShowPercent"] = not dConfig["ShowPercent"]
    App.STButton_Cast(event.GetSource()).SetChosen(dConfig["ShowPercent"])

    SaveConfig()


def FractionToggle(_object, event):
    # global ShowFraction
    global dConfig
    dConfig["ShowFraction"] = not dConfig["ShowFraction"]
    App.STButton_Cast(event.GetSource()).SetChosen(dConfig["ShowFraction"])

    SaveConfig()


# noinspection PyUnresolvedReferences
def HandleKeyboardGoBetween(pObject, pEvent):
    pPara = App.TGParagraph_Cast(pEvent.GetDestination())
    pParent = App.TGPane_Cast(pPara.GetParent())
    pSubPara = App.TGParagraph_Cast(pParent.GetNthChild(2))
    pString = App.TGString()
    pSubPara.GetString(pString)
    pNewVal = App.TGString()
    pPara.GetString(pNewVal)
    sNewVal = pNewVal.GetCString()
    if string.count(sNewVal, ".") > 1:
        lList = string.split(sNewVal, ".")
        sNewVal = lList[0] + "." + string.join(lList[1:-1], "")
        pPara.SetString(sNewVal)

    if pNewVal.GetCString() is not None and pNewVal.GetCString() != "":
        dConfig[pString.GetCString()] = int(pNewVal.GetCString())
        if pString.GetCString() == "sFont" or pString.GetCString() == "FontSize":
            UpdateFontSubMenu(0)

        SaveConfig()

    pObject.CallNextHandler(pEvent)


def CreateTextEntryButton(sButtonName, pMenu, _pOptionPane, _pContentPanel, sVar, sFunction, _isChosen=0, _isToggle=0,
                          _EventInt=0, _ET_EVENT=None):
    pTextField = CreateTextField(App.TGString(sButtonName), sVar, sFunction)
    pMenu.AddChild(pTextField)


# From Custom\UnifiedMainMenu\ConfigModules\Options\Graphics\NanoFX by MLeoDaalder
def CreateTextField(pName, sVar, _sFunction):
    pGraphicsMode = App.GraphicsModeInfo_GetCurrentMode()
    # noinspection PyShadowingNames
    LCARS = __import__(pGraphicsMode.GetLcarsModule())
    fMaxWidth = LCARS.MAIN_MENU_CONFIGURE_CONTENT_WIDTH - 0.02
    pPane = App.TGPane_Create(fMaxWidth, 1.0)

    # Create the text tag
    pText = App.TGParagraph_CreateW(pName)
    fWidth = pText.GetWidth() + 0.01
    pTText = App.STButton_CreateW(pName, None)
    del pText

    pPane.AddChild(pTText, 0, 0)
    pTText.SetUseEndCaps(0)
    pTText.SetJustification(App.STButton.LEFT)
    pTText.SetDisabled(1)
    pTText.SetDisabledColor(App.g_kMainMenuBorderMainColor)
    pTText.SetColorBasedOnFlags()
    pTText.SetVisible()

    pTextEntry = App.TGParagraph_Create(str(dConfig[sVar]))
    # noinspection SpellCheckingInspection
    pTextEntry.SetIgnoreString(
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ*?\t\\/,<>\"|:;\'\n-+()&^%$#@!`~\n\r")

    pTextEntry.Resize(fMaxWidth - fWidth, pTextEntry.GetHeight(), 0)
    pTextEntry.SetReadOnly(0)
    pTextEntry.SetColor(App.NiColorA(0, 0, 0, 1))

    pTextEntry.AddPythonFuncHandlerForInstance(App.ET_KEYBOARD, __name__ + ".HandleKeyboardGoBetween")

    pSubEntry = App.TGParagraph_Create(str(sVar))
    pSubEntry.SetNotVisible(1)

    pPane.AddChild(pTextEntry, fWidth + 0.02, 0.002)
    pPane.AddChild(pSubEntry)

    pPane.Resize(fMaxWidth, pTText.GetHeight(), 0)

    return pPane


# noinspection PyPep8
def SelectNext(pObject, pEvent, _variable=None, _sButtonName=None):
    if pEvent and hasattr(pEvent, "GetCString"):
        variable = pEvent.GetCString()
        # noinspection PyUnboundLocalVariable
        if variable is not None and dConfig[variable] is not None:
            # print "Called SelectNext for variable ", variable
            global dConfig
            pButton = pEvent.GetSource()
            if not pButton:
                pObject.CallNextHandler(pEvent)
                return

            pButton = App.STButton_Cast(pButton)
            if not pButton or not hasattr(pButton, "GetName"):
                pObject.CallNextHandler(pEvent)
                return

            error = 0
            # noinspection PyBroadException
            try:
                if pButton.GetObjID() == App.NULL_ID:
                    error = 1
            except:
                error = 1

            if error != 0:
                pObject.CallNextHandler(pEvent)
                return

            sButtonName = dConfig[str(variable) + str(" Menu Name")]
            if sButtonName is not None:
                lOptions = dConfig[str(variable) + str(" Menu Options")]
                if lOptions is not None:
                    if type(lOptions) == type([]) and len(lOptions) > 0:
                        iCounter = 0
                        found = 0
                        defaultValue = None
                        defaultName = "ERROR"
                        for s in lOptions:
                            iCounter = iCounter + 1
                            if type(s) == type([]):
                                if len(s) >= 2:
                                    if defaultValue is None:
                                        defaultValue = str(s[0])
                                        defaultName = str(s[1])
                                    if dConfig[variable] == str(s[0]):
                                        found = 1
                                        break
                                elif len(s) == 1:
                                    if defaultValue is None:
                                        defaultValue = str(s[0])
                                        defaultName = str(s[0])
                                    if dConfig[variable] == str(s[0]):
                                        found = 1
                                        break

                            elif type(s) == type({}):
                                for k in s.keys():
                                    if defaultValue is None:
                                        defaultValue = str(k)
                                        defaultName = str(s[k])
                                    if dConfig[variable] == str(k):
                                        found = 1
                                        break
                                if found:
                                    break

                            elif type(s) == type("") or type(s) == type(1) or type(s) == type(1.2):
                                if defaultValue is None:
                                    defaultValue = str(s)
                                    defaultName = str(s)
                                if dConfig[variable] == str(s):
                                    found = 1
                                    break

                        iCounter = iCounter % len(lOptions)
                        changedSetting = 0
                        if not found or iCounter == 0:
                            dConfig[str(variable)] = defaultValue
                            pButton.SetName(App.TGString(sButtonName + str(defaultName)))
                            changedSetting = 1
                        else:
                            pNext = lOptions[iCounter]
                            if type(pNext) == type([]):
                                if len(pNext) >= 2:
                                    dConfig[str(variable)] = str(pNext[0])
                                    pButton.SetName(App.TGString(sButtonName + str(pNext[1])))
                                    changedSetting = 1
                                elif len(pNext) == 1:
                                    dConfig[str(variable)] = str(pNext[0])
                                    pButton.SetName(App.TGString(sButtonName + str(pNext[0])))
                                    changedSetting = 1

                            elif type(pNext) == type({}):
                                for k in pNext.keys():
                                    dConfig[str(variable)] = str(k)
                                    pButton.SetName(App.TGString(sButtonName + str(pNext[k])))
                                    changedSetting = 1
                                    break

                            elif type(pNext) == type("") or type(pNext) == type(1) or type(pNext) == type(1.2):
                                dConfig[str(variable)] = str(pNext)
                                pButton.SetName(App.TGString(sButtonName + str(pNext)))
                                changedSetting = 1

                        if changedSetting:
                            SaveConfig()

    pObject.CallNextHandler(pEvent)


# noinspection PyPep8
def CreateMultipleChoiceButton(sButtonName, _pMenu, pOptionsPane, pContentPanel, sFunction, variable, lOptions,
                               isChosen=0, isToggle=0, EventInt=0, ET_EVENT=None):
    global dConfig
    pButton = None
    if variable is not None:
        pButton = CreateButton(str(variable), pContentPanel, pOptionsPane, pContentPanel, sFunction, isChosen, isToggle,
                               EventInt, ET_EVENT)

        if dConfig[variable] is not None:
            dConfig[str(variable) + str(" Menu Name")] = sButtonName

            lOptionsProperConstructed = []
            if type(lOptions) == type([]):
                for s in lOptions:
                    if s is not None and (
                            type(s) == type([]) or type(s) == type([]) or type(s) == type("") or type(s) == type(
                        1) or type(s) == type(1.2)):
                        lOptionsProperConstructed.append(s)
            elif type(lOptions) == type({}):
                for s in lOptions.keys():
                    leType = lOptions[s]
                    if leType is not None and (
                            type(leType) == type([]) or type(leType) == type([]) or type(leType) == type("") or type(
                        leType) == type(1) or type(leType) == type(1.2)):
                        lOptionsProperConstructed.append(leType)
            else:
                if type(lOptions) == type("") or type(lOptions) == type(1) or type(lOptions) == type(1.2):
                    lOptionsProperConstructed.append(lOptions)

            dConfig[str(variable) + str(" Menu Options")] = lOptionsProperConstructed
            found = 0
            entry = ""
            for s in lOptionsProperConstructed:
                if s is not None:
                    if type(s) == type([]):
                        if len(s) >= 2:
                            if dConfig[variable] == str(s[0]):
                                found = 1
                                pButton.SetName(App.TGString(sButtonName + str(s[1])))
                                break
                        elif len(s) == 1:
                            if dConfig[variable] == str(s[0]):
                                found = 1
                                pButton.SetName(App.TGString(sButtonName + str(s[0])))
                                break

                    elif type(s) == type({}):
                        for k in s.keys():
                            if dConfig[variable] == str(k):
                                found = 1
                                pButton.SetName(App.TGString(sButtonName + str(s[k])))
                                break
                        if found:
                            break

                    elif type(s) == type("") or type(s) == type(1) or type(s) == type(1.2):
                        if dConfig[variable] == str(s):
                            found = 1
                            pButton.SetName(App.TGString(sButtonName + str(s)))
                            break

                    entry = s
            if found == 0:
                # print(
                #    "ATTENTION: The current configuration is not found on the default select names. It is possible the configuration for ",
                #    variable, " has been manually edited for a custom value.")
                # No clue what's this supposed to be handling but ensure we at least don't spit out an error
                pButton.SetName(App.TGString(sButtonName + "CUSTOM: " + str(entry)))
        else:
            pButton.SetName(App.TGString(sButtonName + " ERROR: No variable " + str(variable) + " found."))
            # print("ERROR on ", __name__, ".CreateMultipleChoiceButton: the specified variable for one of our calls is not found on our configuration.")
    else:
        # print("ERROR on ", __name__, ".CreateMultipleChoiceButton: the specified variable for one of our calls is None.")
        pass

    return pButton


def CreateButton(sButtonName, pMenu, pOptionPane, _pContentPanel, sFunction, isChosen=0, isToggle=0, _EventInt=0,
                 ET_EVENT=None):
    if ET_EVENT is None:
        ET_EVENT = App.UtopiaModule_GetNextEventType()

    pOptionPane.AddPythonFuncHandlerForInstance(ET_EVENT, sFunction)

    pEvent = App.TGStringEvent_Create()
    pEvent.SetEventType(ET_EVENT)
    pEvent.SetDestination(pOptionPane)
    pEvent.SetString(sButtonName)

    pButton = App.STButton_Create(sButtonName, pEvent)
    pButton.SetChoosable(isToggle)
    pButton.SetChosen(isChosen)

    pEvent.SetSource(pButton)
    pMenu.AddChild(pButton)

    return pButton


def CreateFontMenu(sMenuName, pMenu, _pOptionsPane, _pContentPanel):
    pSubMenu = App.STMenu_Create(sMenuName)
    pSubMenu.AddPythonFuncHandlerForInstance(ET_SELECT_BUTTON, __name__ + ".HandleSelectButton")

    for f in listedFonts:
        for i in range(len(dFont[f])):
            pEvent = App.TGStringEvent_Create()
            pEvent.SetEventType(ET_SELECT_BUTTON)
            pEvent.SetDestination(pSubMenu)
            s = "%s%s%d" % (f, sSeparator, dFont[f][i])
            pEvent.SetString(str(s))
            pButton = App.STButton_Create(s, pEvent)
            pSubMenu.AddChild(pButton)

    # Not allowing this
    # CreateTextEntryButton("Custom size (may cause font issues): ", pSubMenu, pOptionsPane, pSubMenu, "FontSize", __name__ + ".HandleKeyboardGoBetween")
    pMenu.AddChild(pSubMenu)

    return pSubMenu


def HandleSelectButton(pObject, pEvent):
    pObject.CallNextHandler(pEvent)
    i = pEvent.GetCString()

    s = string.split(i, sSeparator)
    if len(s) >= 2 and s[0] is not None and s[0] != "" and s[1] is not None and s[1] != "":
        global dConfig
        dConfig["sFont"] = s[0]
        dConfig["FontSize"] = s[1]
        UpdateFontSubMenu(1)


def UpdateFontSubMenu(close=0):
    global pFontSubMenu
    # noinspection PyUnresolvedReferences
    pFontSubMenu.SetName(App.TGString(sBaseFMenu + str(dConfig["sFont"]) + str(sSeparator) + str(dConfig["FontSize"])))
    if close:
        # noinspection PyUnresolvedReferences
        pFontSubMenu.Close()

    SaveConfig()
