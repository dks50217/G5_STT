from pytranscriber.control.ctr_main import Ctr_Main
from pytranscriber.control.ctr_mssql import Ctr_MSSQL
import multiprocessing

if __name__ == '__main__':
    multiprocessing.freeze_support()
    import sys
    ctrSQL = Ctr_MSSQL()
    audioList = ctrSQL.GetG5AudioList()
    ctrMain = Ctr_Main(audioList)
    sys.exit(main())
