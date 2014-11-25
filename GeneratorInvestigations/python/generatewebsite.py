import os
import varial.tools
varial.tools.mk_plotter_chain().run()
varial.tools.WebCreator().run()
os.system('rm -r ~/www/T_th')
os.system('mv RootFilePlots/fileservice/fileservice ~/www/T_th')
os.system('rm -r RootFilePlots')