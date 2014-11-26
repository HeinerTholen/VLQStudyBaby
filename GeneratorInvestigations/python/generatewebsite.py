import os
import varial.tools
os.system('rm -r T_th')
varial.tools.mk_plotter_chain(name='T_th').run()
varial.tools.WebCreator().run()
os.system('rm -r ~/www/T_th')
os.system('cp -r T_th/fileservice/fileservice ~/www/T_th')
