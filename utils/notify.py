import sys

def notify(title, message):
    try:
        if sys.platform.startswith("linux"):
            import subprocess
            subprocess.run(['notify-send', title, message])
        elif sys.platform == "darwin":
            import os
            os.system(f"""osascript -e 'display notification "{message}" with title "{title}"'""")
        elif sys.platform == "win32":
            from win10toast import ToastNotifier
            toaster = ToastNotifier()
            toaster.show_toast(title, message, duration=5)
    except Exception as e:
        print(f"Notification error: {e}")