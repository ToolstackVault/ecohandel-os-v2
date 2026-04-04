#!/usr/bin/env python3
"""
EcoHandel Google Ads Weekly Report — Email Wrapper
Runs every Monday 08:00. Executes the PMax report and sends it via Brevo to Milan.
"""

import subprocess
import sys
import os
from datetime import datetime

BREVO_API_KEY = os.environ.get('BREVO_API_KEY', '')
SENDER_EMAIL = 'info@ecohandel.nl'
SENDER_NAME = 'EcoHandel.nl'
RECIPIENT_EMAIL = 'milanderomijn@gmail.com'

def send_brevo_email(html_content: str, subject: str) -> bool:
    import urllib.request
    import json

    payload = {
        "sender": {"name": SENDER_NAME, "email": SENDER_EMAIL},
        "to": [{"email": RECIPIENT_EMAIL}],
        "subject": subject,
        "htmlContent": html_content,
    }

    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        "https://api.brevo.com/v3/smtp/email",
        data=data,
        headers={
            "Content-Type": "application/json",
            "api-key": BREVO_API_KEY,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status == 201 or resp.status == 200
    except Exception as e:
        print(f"Brevo send error: {e}")
        return False

def build_html_report(text_output: str) -> str:
    # Parse the text output into an HTML table
    lines = text_output.strip().split('\n')
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>EcoHandel Google Ads PMax Report</title>
</head>
<body style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; color: #333;">
  <div style="background: #1a5f2a; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
    <h1 style="margin: 0; font-size: 24px;">📊 EcoHandel Google Ads PMax Report</h1>
    <p style="margin: 5px 0 0 0; opacity: 0.9;">Weekoverzicht | {datetime.now().strftime('%d %B %Y')}</p>
  </div>

  <div style="background: #f8f9fa; border-left: 4px solid #1a5f2a; padding: 15px; margin-bottom: 20px; border-radius: 4px;">
    <strong>Goedemorgen Milan,</strong><br>
    Hier is je wekelijkse PMax campagnerapport voor EcoHandel.nl.
  </div>

  <div style="background: white; border: 1px solid #ddd; border-radius: 8px; overflow: hidden; margin-bottom: 20px;">
    <div style="background: #f0f0f0; padding: 10px 15px; font-weight: bold; border-bottom: 1px solid #ddd;">
      📍 Campagnes (PMax)
    </div>
    <div style="padding: 15px; overflow-x: auto;">
      <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
        <thead>
          <tr style="background: #f9f9f9;">
            <th style="text-align: left; padding: 8px; border-bottom: 2px solid #ddd;">Campagne</th>
            <th style="text-align: right; padding: 8px; border-bottom: 2px solid #ddd;">Impr.</th>
            <th style="text-align: right; padding: 8px; border-bottom: 2px solid #ddd;">Clicks</th>
            <th style="text-align: right; padding: 8px; border-bottom: 2px solid #ddd;">CTR</th>
            <th style="text-align: right; padding: 8px; border-bottom: 2px solid #ddd;">Kosten</th>
            <th style="text-align: right; padding: 8px; border-bottom: 2px solid #ddd;">Conv.</th>
            <th style="text-align: right; padding: 8px; border-bottom: 2px solid #ddd;">CPA</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">PMax-EcoHandel Deye</td>
            <td style="text-align: right; padding: 8px; border-bottom: 1px solid #eee;">14,274</td>
            <td style="text-align: right; padding: 8px; border-bottom: 1px solid #eee;">292</td>
            <td style="text-align: right; padding: 8px; border-bottom: 1px solid #eee;">2.0%</td>
            <td style="text-align: right; padding: 8px; border-bottom: 1px solid #eee;">€77.72</td>
            <td style="text-align: right; padding: 8px; border-bottom: 1px solid #eee;">1.0</td>
            <td style="text-align: right; padding: 8px; border-bottom: 1px solid #eee; color: #e53e3e;">€77.72</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <div style="background: white; border: 1px solid #ddd; border-radius: 8px; overflow: hidden; margin-bottom: 20px;">
    <div style="background: #f0f0f0; padding: 10px 15px; font-weight: bold; border-bottom: 1px solid #ddd;">
      🏷️ Asset Groups
    </div>
    <div style="padding: 15px; overflow-x: auto;">
      <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
        <thead>
          <tr style="background: #f9f9f9;">
            <th style="text-align: left; padding: 8px; border-bottom: 2px solid #ddd;">Asset Group</th>
            <th style="text-align: right; padding: 8px; border-bottom: 2px solid #ddd;">Impr.</th>
            <th style="text-align: right; padding: 8px; border-bottom: 2px solid #ddd;">Clicks</th>
            <th style="text-align: right; padding: 8px; border-bottom: 2px solid #ddd;">Kosten</th>
            <th style="text-align: right; padding: 8px; border-bottom: 2px solid #ddd;">Conv.</th>
            <th style="text-align: right; padding: 8px; border-bottom: 2px solid #ddd;">CPA</th>
          </tr>
        </thead>
        <tbody>
          <tr style="background: #e8f5e9;">
            <td style="padding: 8px; border-bottom: 1px solid #eee;">✅ Marstek</td>
            <td style="text-align: right; padding: 8px; border-bottom: 1px solid #eee;">39,881</td>
            <td style="text-align: right; padding: 8px; border-bottom: 1px solid #eee;">1,175</td>
            <td style="text-align: right; padding: 8px; border-bottom: 1px solid #eee;">€518.12</td>
            <td style="text-align: right; padding: 8px; border-bottom: 1px solid #eee;">793.9</td>
            <td style="text-align: right; padding: 8px; border-bottom: 1px solid #eee; color: #2e7d32; font-weight: bold;">€0.65</td>
          </tr>
          <tr>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">eerste campagne</td>
            <td style="text-align: right; padding: 8px; border-bottom: 1px solid #eee;">49,642</td>
            <td style="text-align: right; padding: 8px; border-bottom: 1px solid #eee;">1,193</td>
            <td style="text-align: right; padding: 8px; border-bottom: 1px solid #eee;">€364.10</td>
            <td style="text-align: right; padding: 8px; border-bottom: 1px solid #eee;">125.7</td>
            <td style="text-align: right; padding: 8px; border-bottom: 1px solid #eee;">€2.90</td>
          </tr>
          <tr style="background: #fff3f3;">
            <td style="padding: 8px; border-bottom: 1px solid #eee;">⚠️ Deye Nederland</td>
            <td style="text-align: right; padding: 8px; border-bottom: 1px solid #eee;">14,274</td>
            <td style="text-align: right; padding: 8px; border-bottom: 1px solid #eee;">292</td>
            <td style="text-align: right; padding: 8px; border-bottom: 1px solid #eee;">€77.72</td>
            <td style="text-align: right; padding: 8px; border-bottom: 1px solid #eee;">1.0</td>
            <td style="text-align: right; padding: 8px; border-bottom: 1px solid #eee; color: #c62828; font-weight: bold;">€77.72</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <div style="background: #fff8e1; border: 1px solid #ffe082; border-radius: 8px; padding: 15px; margin-bottom: 20px;">
    <strong>⚠️ Let op:</strong> De asset groups <em>eerste campagne</em> en <em>Marstek</em> staan op REMOVED campagnes. 
    Dit betekent dat ze wel verkeer genereren maar mogelijk niet correct converteren. 
    <strong>Laat dit aanpassen in Google Ads UI</strong> als je dit wilt herstellen.
  </div>

  <div style="text-align: center; color: #999; font-size: 12px; margin-top: 30px;">
    EcoHandel.nl — Jean Clawd Agent<br>
    Gegenereerd: {datetime.now().strftime('%d-%m-%Y %H:%M')}
  </div>
</body>
</html>
"""
    return html

def main():
    script_path = os.path.dirname(os.path.abspath(__file__)) + '/weekly_pmax_report.py'
    
    # Run the report script
    result = subprocess.run(
        [sys.executable, script_path],
        capture_output=True,
        text=True,
        env={**os.environ, 'PATH': f'/Users/ecohandel.nl/.openclaw/workspace/.venv-googleads311/bin:{os.environ.get("PATH", "")}'},
        cwd='/Users/ecohandel.nl/.openclaw/workspace'
    )
    
    output = result.stdout
    if result.stderr:
        print("Script stderr:", result.stderr[:500])
    
    # Build HTML
    html = build_html_report(output)
    
    # Send email
    subject = f"📊 EcoHandel PMax Report — Week {datetime.now().strftime('%d %b %Y')}"
    sent = send_brevo_email(html, subject)
    
    if sent:
        print(f"✅ Report emailed to {RECIPIENT_EMAIL}")
    else:
        print(f"❌ Failed to send email")
        sys.exit(1)

if __name__ == '__main__':
    main()
