def openwin():
    from phiendichvideo.configure.config import tr,params,app_cfg
    from phiendichvideo.util import tools
    from phiendichvideo.util.TestSrtTrans import TestSrtTrans
    from phiendichvideo.winform._helpers import make_feed_translator, make_setallmodels
    from phiendichvideo.component.set_form import MiniMaxForm

    winobj = MiniMaxForm()
    app_cfg.child_forms['minimax'] = winobj
    winobj.update_ui()

    feed = make_feed_translator(winobj, "test")

    def test():
        key = winobj.minimax_key.text()
        if not key:
            return tools.show_error(tr("Please input Secret"))
        params["minimax_key"] = key
        params["minimax_model"] = winobj.minimax_model.currentText()
        params["minimax_max_tokens"] = winobj.max_token.text()
        api = winobj.minimax_api.text().strip()
        if api:
            params["minimax_api"] = api
        params.save()
        winobj.test.setText(tr("Testing..."))
        from phiendichvideo import translator
        task = TestSrtTrans(parent=winobj, translator_type=translator.MINIMAX_INDEX)
        task.uito.connect(feed)
        task.start()

    def save():
        params["minimax_key"] = winobj.minimax_key.text()
        params["minimax_model"] = winobj.minimax_model.currentText()
        params["minimax_max_tokens"] = winobj.max_token.text()
        api = winobj.minimax_api.text().strip()
        if api:
            params["minimax_api"] = api
        params.save()
        winobj.close()

    winobj.set.clicked.connect(save)
    winobj.edit_allmodels.textChanged.connect(make_setallmodels(winobj, 'minimax_model', 'minimax_model'))
    winobj.test.clicked.connect(test)
    winobj.show()
