# This is automatically loaded by the early load plugin loader. The loader just loads the module it's up to you to execute whatever logic you want if any.

import App


class Font:
    def __init__(self, name, size, file, loadMethod):
        self.name = name
        self.size = size
        self.file = file
        self.loadMethod = loadMethod


registry = []
defaultFont = None


def RegisterFontOverride(_self, name, size, file, loadMethod):
    global registry, defaultFont
    registry.append(Font(name, size, file, loadMethod))
    # First registered font is default
    if len(registry) == 1:
        defaultFont = registry[0]
    return originalRegisterFont(_self, name, size, file, loadMethod)


def GetFontList(_self):
    global registry
    # Return a copy, don't return original list
    return list(registry)


def SetDefaultFontOverride(_self, name, size):
    global registry, defaultFont
    for font in registry:
        if font.name == name:
            defaultFont = font
            break
    return originalSetDefaultFont(_self, name, size)


# noinspection PyUnresolvedReferences
def GetDefaultFontInfo(_self):
    global defaultFont
    if defaultFont:
        return Font(defaultFont.name, defaultFont.size, defaultFont.file, defaultFont.loadMethod)
    return None


# Yes monkey patch to extend the logic, you can chain them the way you want to it will have no ill effects
originalRegisterFont = App.TGFontManager.RegisterFont
originalSetDefaultFont = App.TGFontManager.SetDefaultFont
App.TGFontManager.RegisterFont = RegisterFontOverride
App.TGFontManager.SetDefaultFont = SetDefaultFontOverride
# New method to expose lists
App.TGFontManager.GetFontList = GetFontList
App.TGFontManager.GetDefaultFontInfo = GetDefaultFontInfo
