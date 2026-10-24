"""
feedback_util.py - Open default mail client with log attachment for user feedback.
"""

import logging
import os
import sys
import threading
import webbrowser
from datetime import datetime
from urllib.parse import quote


FEEDBACK_RECIPIENT = "lamvu211@gmail.com"


def _resolve_log_dir() -> str:
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_log_file_path() -> str:
    return os.path.join(_resolve_log_dir(), "directtrans.log")


def _flush_log_handlers():
    for handler in logging.root.handlers:
        try:
            handler.flush()
        except Exception:
            pass


def _open_outlook_compose(log_path: str, subject: str) -> bool:
    """Return True if Outlook compose was opened."""
    import pythoncom
    import win32com.client

    pythoncom.CoInitialize()
    try:
        outlook = win32com.client.Dispatch("Outlook.Application")
        mail = outlook.CreateItem(0)
        mail.To = FEEDBACK_RECIPIENT
        mail.Subject = subject
        if os.path.isfile(log_path):
            mail.Attachments.Add(log_path)
        # Modal Display(True) blocks the caller until Outlook closes — freezes Tkinter.
        mail.Display(False)
        logging.info("Feedback mail opened via Outlook (subject=%s)", subject)
        return True
    except Exception as e:
        logging.warning("Outlook feedback compose failed: %s", e)
        return False
    finally:
        pythoncom.CoUninitialize()


def _open_mailto_fallback(log_path: str, subject: str):
    body = (
        "DirectTrans feedback\n\n"
        f"Log file (please attach manually if not included):\n{log_path}\n"
    )
    mailto = (
        f"mailto:{FEEDBACK_RECIPIENT}"
        f"?subject={quote(subject)}"
        f"&body={quote(body)}"
    )
    webbrowser.open(mailto)
    logging.info("Feedback opened via mailto (subject=%s)", subject)


def _feedback_worker():
    _flush_log_handlers()
    log_path = os.path.abspath(get_log_file_path())
    subject = f"Direct Trans issue_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    if not _open_outlook_compose(log_path, subject):
        _open_mailto_fallback(log_path, subject)


def open_feedback_mail():
    """Open mail compose with log attached (Outlook COM) or mailto fallback."""
    threading.Thread(target=_feedback_worker, daemon=True).start()
