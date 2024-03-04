import subprocess
import os

def run(script_path):
    subprocess.Popen(['cmd', '/k', 'python', script_path], creationflags=subprocess.CREATE_NEW_CONSOLE)

def main():
    cliente = "./clientsocket.py"
    servidor = "./serversocket.py"
    test = "./test.py"

    if not os.path.exists(cliente):
        print(f"The script {cliente} does not exist.")
        exit()
    if not os.path.exists(servidor):
        print(f"The script {servidor} does not exist.")
        exit()
    if not os.path.exists(test):
        print(f"The script {test} does not exist.")
        exit()
    
    try:
        res = int(input('Please select a mode:\n    1. Run server and client.\n    2. Run server and tests.\nEnter an number: '))
    except ValueError:
        print('The answer must be 1 or 2')
        res = main()
    if res == 1:
        run(servidor)
        run(cliente)
    elif res == 2:
        run(servidor)
        run(test)
    else:
        print('The answer must be 1 or 2')
        main()

if __name__ == "__main__":
    main()