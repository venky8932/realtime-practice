import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

HOST = "0.0.0.0"
PORT = 8080

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status": "ok"}')
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        return


def run_health_server():
    server = HTTPServer((HOST, PORT), HealthHandler)
    print(f"[worker] health endpoint listening on http://{HOST}:{PORT}/health")
    server.serve_forever()


def main_loop():
    heartbeat = 0
    while True:
        print(f"[worker] heartbeat {heartbeat}")
        heartbeat += 1
        time.sleep(10)


if __name__ == "__main__":
    thread = threading.Thread(target=run_health_server, daemon=True)
    thread.start()
    main_loop()
