import os
from rasa.cli import run

def run_server():
    args = ['run']
    args.extend(['--enable-api', '--cors', '*', '--port', os.getenv('PORT', '5005')])
    run.main(args=args)

if __name__ == '__main__':
    run_server()
