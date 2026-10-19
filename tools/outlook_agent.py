import argparse
import json
import os
import traceback
from http.server import BaseHTTPRequestHandler, HTTPServer
import win32com.client
import pythoncom

# Токен задаётся через переменную окружения OUTLOOK_AGENT_TOKEN
# (или .env рядом с этим файлом). Должен совпадать со значением в CRM.
TOKEN = os.getenv("OUTLOOK_AGENT_TOKEN", "").strip()
if not TOKEN:
    raise SystemExit(
        "OUTLOOK_AGENT_TOKEN не задан. Укажите токен в переменной окружения "
        "(тот же, что использует CRM) и перезапустите агент."
    )
OUTLOOK = None

def get_outlook():
    global OUTLOOK
    try:
        if OUTLOOK is None:
            OUTLOOK = win32com.client.Dispatch("Outlook.Application")
        # Проверяем, жив ли объект
        _ = OUTLOOK.Name
        return OUTLOOK
    except Exception:
        OUTLOOK = None
        try:
            OUTLOOK = win32com.client.Dispatch("Outlook.Application")
            return OUTLOOK
        except Exception as e:
            raise Exception(f"Не удалось подключиться к Outlook. Убедитесь, что запущен классический Outlook (не 'Новый Outlook'). Ошибка: {e}")

class AgentHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args): pass

    def _send_json(self, code, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/health":
            try:
                get_outlook()
                self._send_json(200, {"ok": True, "status": "Outlook connected"})
            except Exception as e:
                self._send_json(500, {"ok": False, "error": str(e)})
        else:
            self._send_json(404, {"ok": False, "error": "Not found"})

    def do_POST(self):
        if self.path != "/outlook" or self.headers.get("X-CRM-Token") != TOKEN:
            self._send_json(403, {"ok": False, "error": "Invalid token"})
            return

        try:
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length).decode("utf-8"))
            
            outlook = get_outlook()
            mail = outlook.CreateItem(0)
            mail.To = str(data.get("to", ""))
            mail.Subject = str(data.get("subject", ""))
            mail.Body = str(data.get("body", ""))
            
            # Пытаемся показать окно. Если не выходит (например, скрытый режим), сохраняем в черновики
            try:
                mail.Display(False)
            except Exception:
                mail.Save()
                return self._send_json(200, {"ok": True, "message": "Письмо сохранено в черновики Outlook (не удалось открыть окно)"})

            self._send_json(200, {"ok": True, "message": "Письмо открыто в Outlook"})

        except Exception as exc:
            self._send_json(500, {"ok": False, "error": f"Ошибка Outlook: {str(exc)}. Проверьте, запущен ли классический Outlook."})

if __name__ == "__main__":
    pythoncom.CoInitialize()
    server = HTTPServer(("127.0.0.1", 8765), AgentHandler)
    print("Outlook Agent запущен на порту 8765. Не закрывайте это окно.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        pythoncom.CoUninitialize()