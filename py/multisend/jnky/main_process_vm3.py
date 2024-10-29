import subprocess
import time
import os
import sys
import signal
import psutil

def signal_handler(sig, frame):
    print('\nProgram interrupted by user. Cleaning up...')
    delete_accounts_json()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def get_process_time(pid):
    try:
        process = psutil.Process(pid)
        return process.cpu_times().user + process.cpu_times().system
    except psutil.NoSuchProcess:
        return None

def run_script(script_name):
    print(f"Running {script_name}...")
    max_execution_time = 150  # 2 minutes
    start_time = time.time()
    last_cpu_time = None
    cpu_time_check_interval = 10  # Check CPU time every 10 seconds

    try:
        process = subprocess.Popen(['python3', script_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())

            current_time = time.time()
            
            # Check if the process has exceeded the max execution time
            if current_time - start_time > max_execution_time:
                print(f"{script_name} has exceeded the maximum execution time. Terminating...")
                return restart_script(process, script_name)

            # Check CPU time every 10 seconds
            if current_time - start_time > cpu_time_check_interval:
                current_cpu_time = get_process_time(process.pid)
                if current_cpu_time is not None:
                    if last_cpu_time is not None and current_cpu_time == last_cpu_time:
                        print(f"{script_name} CPU time has not changed. Restarting...")
                        return restart_script(process, script_name)
                    last_cpu_time = current_cpu_time
                start_time = current_time  # Reset the start time for the next interval

        rc = process.poll()
        if rc != 0:
            print(f"Error running {script_name}. Return code: {rc}")
            error_output = process.stderr.read()
            print(f"Error output: {error_output}")
        else:
            print(f"{script_name} completed successfully.")
    except Exception as e:
        print(f"An error occurred while running {script_name}: {str(e)}")

    print(f"Waiting for 3 seconds before next step...")
    time.sleep(3)

def restart_script(process, script_name):
    parent = psutil.Process(process.pid)
    for child in parent.children(recursive=True):
        child.terminate()
    parent.terminate()
    try:
        parent.wait(timeout=5)
    except psutil.TimeoutExpired:
        print(f"Process for {script_name} did not terminate. Killing...")
        parent.kill()
    print(f"Restarting {script_name}...")
    return run_script(script_name)  # Restart the script

def delete_accounts_json():
    try:
        if os.path.exists('accounts.json'):
            os.remove('accounts.json')
            print("accounts.json file has been deleted.")
        else:
            print("accounts.json file does not exist.")
    except Exception as e:
        print(f"Error deleting accounts.json: {str(e)}")

def main():
    scripts = [
        'mnemonic_privatekey_generate3.py',
        'batch_transfer_vm3.py',
        'faucet_interaction3.py',
        'batch_approve3.py',
        'batch_send_recipient3.py'
    ]

    wait_time = 1  # 1초 대기 (초 단위)
    while True:
        try:
            for script in scripts:
                if script == 'mnemonic_privatekey_generate.py' and os.path.exists('accounts.json'):
                    print("accounts.json already exists. Skipping mnemonic_privatekey_generate.py.")
                    continue
                run_script(script)
                print(f"Completed {script}")
                print("----------------------------")
            delete_accounts_json()
            print("All processes completed for this iteration.")
            print(f"Waiting for {wait_time} seconds before starting the next iteration...")
            time.sleep(wait_time)
            print("Starting next iteration...")
        except Exception as e:
            print(f"An error occurred in the main loop: {str(e)}")
            print("Waiting for 3 seconds before retrying...")
            time.sleep(3)

if __name__ == "__main__":
    main()