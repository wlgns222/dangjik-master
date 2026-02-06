import http.server
import socketserver
import json
import os
from src.duty_main import duty_generator

# [설계 원칙] 상수(Constant) 선언을 통한 하드코딩 방지
DATA_DIR = "./data"
GUI_DIR = "gui"  # 사용자님의 폴더 이름에 맞춰 정의

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

    # 2. 데이터 수신 및 연산 요청 처리 (POST)
    def do_POST(self):
        # [파일 업로드 로직]
        if self.path == '/upload':
            content_length = int(self.headers['Content-Length'])
            data = json.loads(self.rfile.read(content_length).decode('utf-8'))
            file_name = data.get('fileName')
            content = data.get('content')

            try:
                file_path = os.path.join(DATA_DIR, file_name)
                # utf-8-sig: 엑셀에서 만든 CSV의 한글 깨짐을 방지하는 최적의 인코딩
                with open(file_path, 'w', encoding='utf-8-sig') as f:
                    f.write(content)
                self._send_json_response({"status": "success", "message": f"{file_name} 업로드 완료"})
            except Exception as e:
                self._send_json_response({"status": "error", "message": str(e)}, 500)

        # [근무 배정 엔진 가동 로직]
        elif self.path == '/generate':
            content_length = int(self.headers['Content-Length'])
            params = json.loads(self.rfile.read(content_length).decode('utf-8'))

            try:
                # Core Engine 가동 (duty_main.py 내의 함수 호출)
                result_message = duty_generator(
                    start_date=params['startDate'],
                    end_date=params['endDate'],
                    ld_date=params['ldDate'],
                    last_workers=params['lastWorkers']
                )
                self._send_json_response({"status": "success", "message": result_message})
            except Exception as e:
                self._send_json_response({"status": "error", "message": str(e)}, 500)
        
        else:
            self.send_error(404, "API Endpoint Not Found")

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
        print(f"📂 정적 자원 경로: ./{GUI_DIR}/")
        print(f"===============================================")
        httpd.serve_forever()

if __name__ == "__main__":
    run_server()