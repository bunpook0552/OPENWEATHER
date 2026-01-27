import os
import requests
import folium
from folium.features import DivIcon
from datetime import datetime
import pytz

# 1. ดึง Key
API_KEY = os.environ.get('OPENWEATHER_API_KEY')
if not API_KEY:
    raise ValueError("❌ ไม่พบ API Key")

# 2. รายชื่อจุดตรวจวัด (อยากเพิ่มจุดไหน ก๊อปปี้บรรทัดเดิมแล้วแก้ชื่อ/พิกัด ได้เลย!)
locations = [
    {"name": "ตลาดอินทร์บุรี", "lat": 15.006, "lon": 100.326},
    {"name": "ต.ทับยา", "lat": 14.980, "lon": 100.310},
    {"name": "ต.ทองเอน", "lat": 15.050, "lon": 100.350},
    {"name": "ต.ชีน้ำร้าย", "lat": 14.950, "lon": 100.300},
    {"name": "ต.น้ำตาล", "lat": 14.990, "lon": 100.340},
    {"name": "ต.งิ้วราย", "lat": 14.970, "lon": 100.330},
    {"name": "ต.ประศุก", "lat": 15.030, "lon": 100.380},
    {"name": "ต.โพธิ์ชัย", "lat": 14.960, "lon": 100.320}, # เพิ่มตัวอย่างให้ 1 จุด
]

# 3. สร้างแผนที่ (Dark Mode)
m = folium.Map(location=[15.006, 100.326], zoom_start=12, tiles='CartoDB dark_matter')

print("กำลังดึงข้อมูลสภาพอากาศ V2...")

for loc in locations:
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={loc['lat']}&lon={loc['lon']}&appid={API_KEY}&units=metric&lang=th"
        response = requests.get(url)
        data = response.json()

        if response.status_code != 200: continue

        temp = round(data['main']['temp'], 1)
        rain_1h = data.get('rain', {}).get('1h', 0)
        desc = data['weather'][0]['description']

        # Logic สี และ ไอคอน
        if rain_1h > 10:
            color = '#ff3333' # แดงฉาน
            icon_char = "⛈️" # พายุ
            status_alert = "style='color:red; font-weight:bold;'"
        elif rain_1h > 0:
            color = '#00ccff' # ฟ้า
            icon_char = "🌧️" # ฝน
            status_alert = "style='color:skyblue;'"
        else:
            color = '#00ff88' # เขียวนีออน
            icon_char = "☁️" # เมฆ/ปกติ
            status_alert = ""

        # --- ส่วนแสดงผลบนแผนที่ (Label) แบบไม่ต้องคลิก ---
        # 1. วงกลมสี (พื้นหลัง)
        folium.CircleMarker(
            location=[loc['lat'], loc['lon']],
            radius=6,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=1.0,
            popup=f"{loc['name']}: {desc}"
        ).add_to(m)

        # 2. ข้อความลอย (Text Label)
        folium.map.Marker(
            [loc['lat'], loc['lon']],
            icon=DivIcon(
                icon_size=(150,36),
                icon_anchor=(0,0),
                # HTML ตรงนี้คือสิ่งที่โชว์บนแผนที่ตลอดเวลา
                html=f"""
                    <div style="font-size: 12px; font-weight: bold; color: {color}; text-shadow: 1px 1px 2px black; margin-left: 10px; margin-top: -8px;">
                        {icon_char} {loc['name']}<br>
                        🌡️ {temp}°C | 💧 {rain_1h} มม.
                    </div>
                """
            )
        ).add_to(m)

    except Exception as e:
        print(f"Error {loc['name']}: {e}")

# 4. Dashboard Overlay (กรอบสรุปข้อมูลมุมขวาบน)
tz = pytz.timezone('Asia/Bangkok')
update_time = datetime.now(tz).strftime("%H:%M")

legend_html = f'''
     <div style="position: fixed; top: 10px; right: 10px; z-index:9999; font-size:14px; background:rgba(0,0,0,0.8); padding:10px; border-radius:5px; border: 1px solid #444; color: white; width: 200px;">
         <h4 style="margin:0; color:#00ff88;">📡 In Buri War Room</h4>
         <hr style="border-color:#555; margin: 5px 0;">
         <small>🕒 อัปเดต: {update_time} น.</small><br>
         <br>
         <span style="color:#ff3333;">⛈️</span> = ฝนตกหนัก<br>
         <span style="color:#00ccff;">🌧️</span> = มีฝน<br>
         <span style="color:#00ff88;">☁️</span> = ปกติ
     </div>
     '''
m.get_root().html.add_child(folium.Element(legend_html))

m.save("index.html")
print("🎉 อัปเกรดหน้าตาสำเร็จ!")
