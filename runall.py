# run_experiments.py
import subprocess
import time

def run_node(script_name):
    print(f"Starting node with {script_name}...")
    return subprocess.Popen(["python", script_name])

def perform_operations():
    print("Performing operations on nodes...")
    time.sleep(10)  # Allow time for nodes to start

    # Send messages to all nodes
    subprocess.run(["python", "send_messages.py"])
    time.sleep(10)  # Wait for operations to complete

if __name__ == "__main__":
    # Run all nodes
    nodes = [
        "laplace.py",
        "gauss.py",
        "exp.py",
        "rand.py"
    ]

    processes = []
    for node_script in nodes:
        process = run_node(node_script)
        processes.append(process)

    # Wait for nodes to fully initialize
    time.sleep(15)

    # Perform operations
    perform_operations()

    # Optionally, wait for all processes to finish
    for process in processes:
        process.terminate()
        process.wait()

    print("Experiments completed.")

