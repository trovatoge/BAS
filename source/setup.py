from distutils.core import setup
import py2exe
import CowLog

setup(
        data_files = ["almod2.ico"],   
        windows=[
        {   
            "script" : 'CowLog.py',
            "version" : CowLog.__version__,
            "icon_resources" : [(1,"almod2.ico")],
            "icon_file" : "almod2.ico"
        }], 
        options= {"py2exe": {"includes":["sip"]}}
    ) 