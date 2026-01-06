from flask import Flask, render_template, request
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time
import re
import jwt

app = Flask(__name__)

# 🔐 MUST MATCH NODE SECRET
SECRET_KEY = "ROH_MARV"

# --- CONSTANTS ---
SENDER_EMAIL = "rohanshalom05@gmail.com"
EMAIL_PASSWORD = "rqnq ijth zgpb rjeh"
FROM_CODE = "BLR"

# ---------------- JWT PROTECTED HOME ----------------
@app.route("/")
def home():
    token = request.args.get("token")

    if not token:
        return "Unauthorized access", 401

    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username = decoded.get("username")
        return render_template("index.html", username=username)
    except jwt.ExpiredSignatureError:
        return "Session expired. Please login again.", 401
    except jwt.InvalidTokenError:
        return "Invalid token. Access denied.", 401

# ---------------- SCRAPER LOGIC ----------------
def run_scraper(to_code, depart_date, return_date, receiver_email):
    options = Options()

    # ✅ REQUIRED FOR DOCKER
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    # Anti-detection (your original logic preserved)
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    # ✅ FORCE SYSTEM CHROMEDRIVER (CRITICAL FIX)
    service = Service("/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)

    try:
        # 1. BUILD URL
        if return_date:
            url = f"https://www.google.com/travel/flights?q=Flights%20from%20{FROM_CODE}%20to%20{to_code}%20on%20{depart_date}%20through%20{return_date}"
        else:
            url = f"https://www.google.com/travel/flights?q=Flights%20from%20{FROM_CODE}%20to%20{to_code}%20on%20{depart_date}%20oneway"

        driver.get(url)
        time.sleep(15)

        # 2. JAVASCRIPT EXTRACTION
        script = """
        let results = [];
        let elements = document.querySelectorAll('li, [role="listitem"], .pI9Wbc');
        elements.forEach(el => {
            if (el.innerText.includes('₹') && el.innerText.length > 60) {
                results.push(el.innerText);
            }
        });
        return results;
        """
        raw_flights = driver.execute_script(script)

        # 3. FORMAT REPORT
        report_body = f"FLIGHT SEARCH REPORT\n{'='*30}\n"
        report_body += f"Route: {FROM_CODE} -> {to_code}\nDates: {depart_date}"
        if return_date:
            report_body += f" to {return_date}"
        report_body += "\n\n"

        seen = set()
        count = 0

        for flight_text in raw_flights:
            if count >= 10:
                break

            lines = [line.strip() for line in flight_text.split('\n') if line.strip()]
            signature = " ".join(lines[:3])

            if signature not in seen and any("₹" in l for l in lines):
                count += 1
                price = next(
                    (re.search(r"₹[\d,]+", l).group() for l in lines if "₹" in l),
                    "N/A"
                )

                report_body += f"OPTION #{count}\n"
                report_body += f"  Airline : {lines[0]}\n"
                report_body += f"  Price   : {price}\n"
                report_body += f"  Details : {' | '.join(lines[1:4])}\n"
                report_body += f"{'-'*30}\n"

                seen.add(signature)

        # 4. SAVE FILE
        with open("flight_data.txt", "w", encoding="utf-8") as f:
            f.write(report_body)

        # 5. SEND EMAIL
        if count > 0:
            send_email(receiver_email, report_body, to_code)
            return f"Success! {count} options sent to {receiver_email}."
        else:
            return "No flights found during the search."

    except Exception as e:
        return f"Error during scraping: {str(e)}"

    finally:
        driver.quit()

# ---------------- EMAIL FUNCTION ----------------
def send_email(receiver, content, to_code):
    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = receiver
    msg["Subject"] = f"Top 10 Flight Prices: {FROM_CODE} to {to_code}"
    msg.attach(MIMEText(content, "plain"))

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(SENDER_EMAIL, EMAIL_PASSWORD)
    server.send_message(msg)
    server.quit()

# ---------------- TRACK ROUTE (POST) ----------------
@app.route("/track", methods=["POST"])
def track():
    to_code = request.form.get("to_code").upper()
    depart = request.form.get("depart_date")
    ret = request.form.get("return_date")
    email = request.form.get("receiver_email")

    result_msg = run_scraper(to_code, depart, ret, email)

    return f"""
    <html>
        <body style="font-family: Arial; padding: 50px;">
            <h2>Process Complete</h2>
            <p>{result_msg}</p>
            <br>
            <a href="/">Search Again</a>
        </body>
    </html>
    """

# ---------------- APP START ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
