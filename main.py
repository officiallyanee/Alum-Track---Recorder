import subprocess

process1 = subprocess.Popen(['python', 'import_pyaudio.py'])


process2 = subprocess.Popen(['python', 'screen_2.py'])


process1.wait()
process2.wait()

print("Both files have finished execution.")