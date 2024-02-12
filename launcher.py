import subprocess
def construct_command(passed_terminal_command):
        command = passed_terminal_command
        try:
            subprocess.call(['/bin/bash', '-i', '-c', command])
            return True
        except Exception as e:
            return e
        
witbot = construct_command("witbot")
print(witbot)