import glob
import subprocess

arquivos = glob.glob("fl_[0-9]*_[0-9]")


r = dict.fromkeys(arquivos,[0,0,0])

for f in arquivos:
	print (f)
	s = subprocess.call('python verifier.py ' + f + ' 0 1>/dev/null', shell=True)
	r[f][0] = int(s)
	print (s)
	s = subprocess.call('python verifier.py ' + f + ' 1 1>/dev/null', shell=True)
	r[f][1] = int(s)
	print(s)
	s = subprocess.call('python verifier.py ' + f + ' 2 1>/dev/null', shell=True)
	r[f][2] = int(s)
	print(s)
	
	
print (r)