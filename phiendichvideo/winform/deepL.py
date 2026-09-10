def openwin():
    from phiendichvideo.configure.config import tr,params,app_cfg
    from phiendichvideo.util import tools
    from phiendichvideo.util.TestSrtTrans import TestSrtTrans
    from phiendichvideo.winform._helpers import make_feed_translator
    from phiendichvideo.component.set_form import DeepLForm

    winobj = DeepLForm()
    app_cfg.child_forms['deepl'] = winobj

    feed = make_feed_translator(winobj, "test")

    def test():
        key = winobj.deepl_authkey.text()
        if not key:
            return tools.show_error(tr("Please input auth Secret"))
        params['deepl_authkey'] = key
        params['deepl_api'] = winobj.deepl_api.text().strip()
        params['deepl_gid'] = winobj.deepl_gid.text().strip()
        winobj.test.setText(tr("Testing..."))
        from phiendichvideo import translator
        task = TestSrtTrans(parent=winobj, translator_type=translator.DEEPL_INDEX)
        task.uito.connect(feed)
        task.start()

    def save():
        params['deepl_authkey'] = winobj.deepl_authkey.text()
        params['deepl_api'] = winobj.deepl_api.text().strip()
        params['deepl_gid'] = winobj.deepl_gid.text().strip()
        params.save()
        winobj.close()

    if params['deepl_authkey']:
        winobj.deepl_authkey.setText(params['deepl_authkey'])
    if params['deepl_api']:
        winobj.deepl_api.setText(params['deepl_api'])
    if params['deepl_gid']:
        winobj.deepl_gid.setText(str(params['deepl_gid']))
    winobj.set_deepl.clicked.connect(save)
    winobj.test.clicked.connect(test)
    winobj.show()
