def openwin():
    from phiendichvideo.configure.config import tr,params,app_cfg
    from phiendichvideo.util import tools
    from phiendichvideo.util.TestSrtTrans import TestSrtTrans
    from phiendichvideo.winform._helpers import make_feed_translator
    from phiendichvideo.component.set_form import AliForm

    winobj = AliForm()
    app_cfg.child_forms['ali'] = winobj

    feed = make_feed_translator(winobj, "test")

    def test():
        appid = winobj.ali_id.text()
        miyue = winobj.ali_key.text()
        if not appid or not miyue:
            return tools.show_error(tr("Please input AccessKey ID and AccessKey Secret"))
        params["ali_id"] = appid
        params["ali_key"] = miyue
        winobj.test.setText(tr("Testing..."))
        from phiendichvideo import translator
        task = TestSrtTrans(parent=winobj, translator_type=translator.ALI_INDEX)
        task.uito.connect(feed)
        task.start()

    def save():
        params["ali_id"] = winobj.ali_id.text()
        params["ali_key"] = winobj.ali_key.text()
        params.save()
        winobj.close()

    if params.get("ali_id"):
        winobj.ali_id.setText(str(params.get("ali_id")))
    if params.get("ali_key"):
        winobj.ali_key.setText(str(params.get("ali_key")))
    winobj.set.clicked.connect(save)
    winobj.test.clicked.connect(test)
    winobj.show()
