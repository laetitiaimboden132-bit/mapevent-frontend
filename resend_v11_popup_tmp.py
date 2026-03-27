import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

smtp_user = "mapeventworld@gmail.com"
smtp_password = "oxta novu unxj jizx".replace(" ", "")
to_addr = "mapeventworld@gmail.com"
subject = "URGENT RENVOI V11 - 2 blocs par ligne"

html_body = """<!doctype html>
<html><body style="margin:0;padding:0;background:#020617;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="padding:24px;background:#020617;"><tr><td align="center">
  <table width="430" cellpadding="0" cellspacing="0" style="background:#f4f4f5;border:1px solid #d1d5db;border-radius:10px;overflow:hidden;">
    <tr><td><div style="height:200px;background:linear-gradient(135deg,#7c3aed,#2563eb);"></div></td></tr>
    <tr><td style="padding:12px;">
      <div style="font-size:30px;font-weight:800;font-family:Georgia,'Times New Roman',serif;color:#0f172a;">Scène Urbaine</div>
      <div style="margin-top:8px;display:flex;justify-content:space-between;align-items:center;padding:10px 8px;border-top:1px solid #cbd5e1;border-bottom:1px solid #cbd5e1;">
        <div style="padding:6px 10px;border:1px solid #0f172a;border-radius:999px;font-size:13px;">🤍 J'aime</div>
        <div style="padding:6px 10px;border:1px dashed #94a3b8;border-radius:999px;font-size:13px;">👥 208</div>
        <div style="padding:6px 10px;border:1px solid #0f172a;border-radius:999px;font-size:13px;">💬 Discussion</div>
      </div>
      <div style="margin-top:10px;padding:10px;border:1px solid #cbd5e1;border-radius:12px;background:#eef2f7;">
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">
          <div style="text-align:center;padding:10px 8px;border-radius:11px;background:linear-gradient(135deg,#00ffc3,#10b981);font-size:13px;font-weight:800;">🎟 Participer</div>
          <div style="text-align:center;padding:10px 8px;border-radius:11px;border:1px solid #0f172a;font-size:13px;">➕ Inviter</div>
          <div style="text-align:center;padding:10px 8px;border-radius:11px;border:1px solid #2563eb;background:#0b1228;color:#dbeafe;font-size:13px;">🗓 Ajouter</div>
          <div style="text-align:center;padding:10px 8px;border-radius:11px;border:1px solid #0f172a;font-size:13px;">🔗 Partager</div>
          <div style="text-align:center;padding:10px 8px;border-radius:11px;border:1px solid #0f172a;font-size:13px;">🗺 Y aller</div>
          <div style="text-align:center;padding:10px 8px;border-radius:11px;border:1px solid #7f1d1d;color:#7f1d1d;font-size:13px;">🚨 Signaler</div>
        </div>
        <div style="margin-top:10px;padding:10px;border-radius:11px;background:linear-gradient(135deg,rgba(245,158,11,.16),rgba(234,88,12,.12));border:1px solid rgba(245,158,11,.48);text-align:center;">
          <span style="font-size:13px;font-weight:800;color:#b45309;">Voir la publication</span>
        </div>
      </div>
    </td></tr>
  </table>
</td></tr></table>
</body></html>"""

msg = MIMEMultipart("alternative")
msg["From"] = f"MapEvent <{smtp_user}>"
msg["To"] = to_addr
msg["Subject"] = subject
msg.attach(MIMEText("Renvoi V11 conforme.", "plain", "utf-8"))
msg.attach(MIMEText(html_body, "html", "utf-8"))

with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as server:
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(smtp_user, smtp_password)
    server.sendmail(smtp_user, [to_addr], msg.as_string())

print("SMTP_SENT_OK")
print("TO", to_addr)
print("SUBJECT", subject)
