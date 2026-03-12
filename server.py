import http.server
import socketserver
import json
import os
from src.main_controller import *

# [설계 원칙] 상수(Constant) 선언을 통한 하드코딩 방지
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data") # 상대 경로(./data) 대신 절대 경로 사용
GUI_DIR = "gui"

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

class DutyServerHandler(http.server.SimpleHTTPRequestHandler):
    
    # 1. 정적 파일(HTML, JS, CSS) 요청 처리 (GET)
    def do_GET(self):
        # 루트(/) 접속 시 gui/index.html로 라우팅
        if self.path == '/':
            self.path = f'/{GUI_DIR}/index.html'
        
        # 브라우저가 /script.js 등을 요청할 때 /gui/script.js로 자동 리다이렉션
        # 이 부분이 없으면 서버는 루트 폴더에서 찾으려다 404를 뱉습니다.
        elif not self.path.startswith(f'/{GUI_DIR}/'):
            # 요청한 파일이 실제로 gui 폴더 안에 있는지 검사 후 경로 수정
            potential_path = os.path.join(GUI_DIR, self.path.lstrip('/'))
            if os.path.exists(potential_path):
                self.path = f'/{GUI_DIR}{self.path}'
        
        # 시스템 로그에 현재 접근 중인 실제 경로 출력 (디버깅용)
        print(f"🔍 [GET Request] Searching for: {self.path}")
        return super().do_GET()

    def do_POST(self):
        if self.path == '/upload':
            # 파일 업로드 시 DATA_DIR를 확실히 참조하여 저장
            content_length = int(self.headers['Content-Length'])
            post_data = json.loads(self.rfile.read(content_length).decode('utf-8'))
            file_path = os.path.join(DATA_DIR, post_data['fileName'])
            
            with open(file_path, 'w', encoding='utf-8-sig') as f:
                f.write(post_data['content'])
            self._send_json_response({"status": "success"})

        elif self.path == '/generate':
            content_length = int(self.headers['Content-Length'])
            params = json.loads(self.rfile.read(content_length).decode('utf-8'))

            try:
                # 1. 날짜 역전 기초 검증
                if params['startDate'] > params['endDate']:
                    raise ValueError("시작 날짜가 종료 날짜보다 늦습니다.")

                # 2. 엔진 가동
                result_message = duty_generator(
                    start_date=params['startDate'],
                    end_date=params['endDate'],
                    ld_date=params['ldDate'],
                    last_workers=params['lastWorkers'],
                    event_list=params['eventArr']
                )

                # 3. 생성된 CSV 파일을 읽어서 클라이언트에 전송
                result_file_path = result_message

                csv_data = {}
                if os.path.exists(result_file_path):
                    with open(result_file_path, "r", encoding="utf-8-sig") as f:
                        csv_data['result'] = f.read()

                self._send_json_response({
                    "status": "success", 
                    "message": result_message,
                    "files": csv_data # 브라우저가 다운로드할 내용
                })
            except Exception as e:
                self._send_json_response({"status": "error", "message": str(e)}, 500)

    def _send_json_response(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

def run_server(port=8000):
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", port), DutyServerHandler) as httpd:
        print(f"===============================================")
        print(f"🚀 Admin System Active: http://localhost:{port}")
        print(f"===============================================")
        httpd.serve_forever()

if __name__ == "__main__":
    run_server()
