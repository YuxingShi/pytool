# coding: utf-8
from http.server import SimpleHTTPRequestHandler, HTTPServer
import os
from urllib.parse import unquote

DIRECTORY = "F:/mp3"  # 指定要下载文件的目录
PORT = 8008  # 指定服务器端口


class FileDownloadHandler(SimpleHTTPRequestHandler):
    def generate_file_list(self):
        file_list = []
        for root, dirs, files in os.walk(DIRECTORY):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, DIRECTORY)
                download_link = f'<a href="/{relative_path}" download="{file}">{file}</a>'
                file_list.append(download_link)
        return '<br>'.join(file_list)

    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=UTF-8')
            self.end_headers()
            file_list_html = self.generate_file_list()
            html_content = f'<html><body>{file_list_html}</body></html>'
            self.wfile.write(html_content.encode())
        else:
            filename = self.path[1:]
            filepath = os.path.join(DIRECTORY, unquote(filename))
            if os.path.exists(filepath) and os.path.isfile(filepath):
                self.send_response(200)
                self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
                self.end_headers()
                with open(filepath, 'rb') as file:
                    self.wfile.write(file.read())
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'File not found')

try:
    server = HTTPServer(('0.0.0.0', PORT), FileDownloadHandler)
    print(f'Server started at 0.0.0.0:{PORT}')
    server.serve_forever()

except KeyboardInterrupt:
    print('^C received, shutting down the server')
    server.socket.close()