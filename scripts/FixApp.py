# Yes, we will overwrite this and use it as an early entry point for stuff that we feel needs to be patched early
def FixApp():
    # Stock code
    import App

    # noinspection PyUnresolvedReferences
    App.ObjectGroupWithInfo.__getitem__ = App.ObjectGroupWithInfo.GetInfo
    # noinspection PyUnresolvedReferences
    App.ObjectGroupWithInfo.__setitem__ = App.ObjectGroupWithInfo.AddNameAndInfo
    # noinspection PyUnresolvedReferences
    App.ObjectGroupWithInfo.__delitem__ = App.ObjectGroupWithInfo.RemoveName
    # End of stock code

    SetEarlyOverrides()


def SetEarlyOverrides():
    from Custom.EarlyLoad import Loader

    Loader.Load()
