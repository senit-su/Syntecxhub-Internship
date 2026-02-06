import socket
import threading
import logging
from queue import Queue

# ---------------- CONFIG ----------------
TIMEOUT = 1
THREADS = 100
LOG_FILE = "scan_results.log"
# ----------------------------------------

# Setup logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

print_lock = threading.Lock()
port_queue = Queue()


def scan_port(host, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(TIMEOUT)

        result = sock.connect_ex((host, port))

        with print_lock:
            if result == 0:
                print(f"[OPEN] Port {port}")
                logging.info(f"{host}:{port} OPEN")
            else:
                print(f"[CLOSED] Port {port}")
                logging.info(f"{host}:{port} CLOSED")

        sock.close()

    except socket.timeout:
        with print_lock:
            print(f"[TIMEOUT] Port {port}")
            logging.info(f"{host}:{port} TIMEOUT")

    except Exception as e:
        with print_lock:
            print(f"[ERROR] Port {port} - {e}")
            logging.error(f"{host}:{port} ERROR - {e}")


def worker(host):
    while not port_queue.empty():
        port = port_queue.get()
        scan_port(host, port)
        port_queue.task_done()


def main():
    host = input("Enter target host (IP or domain): ")
    start_port = int(input("Start port: "))
    end_port = int(input("End port: "))

    print(f"\nScanning {host} from port {start_port} to {end_port}...\n")

    for port in range(start_port, end_port + 1):
        port_queue.put(port)

    thread_list = []

    for _ in range(THREADS):
        t = threading.Thread(target=worker, args=(host,))
        t.daemon = True
        t.start()
        thread_list.append(t)

    port_queue.join()
    print("\nScan completed.")
    print(f"Results saved in {LOG_FILE}")


if __name__ == "__main__":
    main()
