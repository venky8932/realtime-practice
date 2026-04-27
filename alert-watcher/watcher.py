import os
import time
import smtplib
from email.mime.text import MIMEText
from kubernetes import client, config

NAMESPACE = os.getenv("NAMESPACE", "default")
DEPLOYMENTS = os.getenv("WATCH_DEPLOYMENTS", "fastapi,nodejs").split(",")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL_SECONDS", "60"))
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.example.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "user@example.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "password")
ALERT_TO = os.getenv("ALERT_TO", "alert@example.com")
ALERT_FROM = os.getenv("ALERT_FROM", SMTP_USER)


def send_email(subject: str, body: str):
    message = MIMEText(body)
    message["Subject"] = subject
    message["From"] = ALERT_FROM
    message["To"] = ALERT_TO
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as smtp:
        smtp.starttls()
        smtp.login(SMTP_USER, SMTP_PASSWORD)
        smtp.sendmail(ALERT_FROM, [ALERT_TO], message.as_string())


def check_deployments():
    config.load_incluster_config()
    api = client.AppsV1Api()
    for name in DEPLOYMENTS:
        try:
            deployment = api.read_namespaced_deployment(name=name, namespace=NAMESPACE)
            desired = deployment.spec.replicas or 0
            available = deployment.status.available_replicas or 0
            if desired > 0 and available == 0:
                subject = f"Alert: {name} has no available replicas"
                body = (
                    f"Deployment {name} in namespace {NAMESPACE} has {available} available replicas "
                    f"out of {desired}.\nPlease check the Kubernetes cluster."
                )
                print("[watcher] sending alert email", subject)
                send_email(subject, body)
        except Exception as exc:
            print(f"[watcher] unable to inspect deployment {name}: {exc}")


if __name__ == "__main__":
    print("[watcher] starting alert watcher")
    while True:
        check_deployments()
        time.sleep(CHECK_INTERVAL)
