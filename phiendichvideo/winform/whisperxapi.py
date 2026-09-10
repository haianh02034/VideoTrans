def openwin():
    from phiendichvideo.configure.config import tr,app_cfg,params
    from phiendichvideo.util import tools
    from phiendichvideo import recognition
    from phiendichvideo.util.TestSTT import TestSTT
    from phiendichvideo.winform._helpers import make_feed_stt
    from phiendichvideo.component.set_form import WhisperXAPIForm

    winobj = WhisperXAPIForm()
    app_cfg.child_forms['whisperx'] = winobj

    feed = make_feed_stt(winobj, "test")

    def _fix_url(url):
        if not url.startswith('http'):
            return 'http://' + url
        return url

    def test():
        params['whisperx_api'] = _fix_url(winobj.api_url.text().strip())
        winobj.test.setText(tr("Testing..."))
        task = TestSTT(parent=winobj, recogn_type=recognition.WHISPERX_API, model_name='tiny')
        task.uito.connect(feed)
        task.start()

    def save():
        params["whisperx_api"] = _fix_url(winobj.api_url.text().strip()).rstrip('/')
        params.save()
        winobj.close()

    winobj.api_url.setText(params.get("whisperx_api", ''))
    winobj.set.clicked.connect(save)
    winobj.test.clicked.connect(test)
    winobj.show()
