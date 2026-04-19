import requests

# קריאת המפתח מהקובץ
with open("config.txt", "r") as f:
    api_key = f.read().strip()

def test_connection():
    url = "https://api.fathom.video/v1/recordings" # רשימת ההקלטות
    headers = {"Authorization": f"Bearer {api_key}"}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print("Success! החיבור עובד.")
        # הדפסת שמות 3 הפגישות האחרונות
        for meeting in data.get('results', [])[:3]:
            print(f"- {meeting.get('title')}")
    else:
        print(f"יש בעיה בחיבור. קוד שגיאה: {response.status_code}")

test_connection()
