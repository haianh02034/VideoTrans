from PySide6.QtCore import QThread, Signal

class TestSTT(QThread):
    uito = Signal(str)

    def __init__(self, *, parent=None, recogn_type=0, model_name=''):
        super().__init__(parent=parent)
        self.recogn_type = recogn_type
        self.model_name = model_name

    def run(self):
        try:
            from phiendichvideo import recognition

            from phiendichvideo.configure.config import ROOT_DIR,tr,app_cfg,settings,params,logger,defaulelang,HOME_DIR
            from phiendichvideo.configure import config
            from phiendichvideo.util import tools
            res = recognition.run(
                audio_file=ROOT_DIR + '/phiendichvideo/styles/no-remove.wav',
                cache_folder=config.TEMP_DIR,
                recogn_type=self.recogn_type,
                model_name=self.model_name,
                detect_language="zh-cn"
            )
            srt_str = tools.get_srt_from_list(res)
            self.uito.emit(f"ok:{srt_str}")
        except Exception as e:
            from phiendichvideo.configure.excepts import get_msg_from_except
            import traceback
            except_msg=get_msg_from_except(e)
            msg = f'{except_msg}:\n' + traceback.format_exc()
            self.uito.emit(msg)
