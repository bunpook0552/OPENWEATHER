import os
import requests
import folium
from datetime import datetime
import pytz

# 1. ดึง Key จากตู้นิรภัย GitHub (Secrets)
API_KEY = os.environ.get('OPENWEATHER_API_KEY')

if not API_KEY:
    raise ValueError("❌ ไม่พบ API Key! กรุณาตั้งค่าใน GitHub Secrets ก่อน")

# 2. ตั้งค่าพิกัดจุดตรวจวัดใน อ.อินทร์บุรี (เพิ่มลดได้ตามใจชอบ)
locations = [
    {"name": "ตลาดอินทร์บุรี", "lat": 15.006, "lon": 100.326},
    {"name": "ต.ทับยา", "lat": 14.980, "lon": 100.310},
    {"name": "ต.ทองเอน", "lat": 15.050, "lon": 100.350},
    {"name": "ต.ชีน้ำร้าย", "lat": 14.950, "lon": 100.300},
    {"name": "ต.น้ำตาล", "lat": 14.990, "lon": 100.340},
    {"name": "ต.งิ้วราย", "lat": 14.970, "lon": 100.330},
]

# 3. สร้างแผนที่พื้นหลัง (Dark Mode)
m = folium.Map(location=[15.006, 100.326], zoom_start=12, tiles='CartoDB dark_matter')

# 4. วนลูปดึงข้อมูลจริงจาก API
print("กำลังดึงข้อมูลสภาพอากาศ...")

for loc in locations:
    try:
        # ยิง request ไปหา OpenWeatherMap
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={loc['lat']}&lon={loc['lon']}&appid={API_KEY}&units=metric&lang=th"
        response = requests.get(url)
        data = response.json()

        # แกะข้อมูลที่ได้
        temp = data['main']['temp']       # อุณหภูมิ
        rain_1h = data.get('rain', {}).get('1h', 0) # ปริมาณฝน 1 ชม. ล่าสุด (ถ้าไม่มีคือ 0)
        desc = data['weather'][0]['description'] # คำอธิบาย (เช่น เมฆปานกลาง)

        # กำหนดสีจุดตามสถานการณ์ (Logic แจ้งเตือนภัย)
        if rain_1h > 10:
            color = '#ff0033' # แดง (อันตราย - ฝนหนัก)
            radius = 15
            status_text = "⚠️ ฝนตกหนัก"
        elif rain_1h > 0:
            color = '#00ccff' # ฟ้า (ฝนตก)
            radius = 10
            status_text = "🌧️ มีฝนตก"
        else:
            color = '#00ff00' # เขียว (ปกติ)
            radius = 5
            status_text = "☁️ ปกติ"

        # สร้าง Popup สวยๆ
        popup_html = f"""
        <div style="font-family: sans-serif; width: 200px;">
            <h4>📍 {loc['name']}</h4>
            <b>สถานะ:</b> {status_text} ({desc})<br>
            <b>ฝน (1ชม.):</b> {rain_1h} มม.<br>
            <b>อุณหภูมิ:</b> {temp} °C
        </div>
        """

        # ปักจุดลงแผนที่
        folium.CircleMarker(
            location=[loc['lat'], loc['lon']],
            radius=radius,
            popup=folium.Popup(popup_html, max_width=300),
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.7
        ).add_to(m)
        
        print(f"✅ {loc['name']}: {desc} (ฝน {rain_1h} มม.)")

    except Exception as e:
        print(f"❌ Error ที่ {loc['name']}: {e}")

# 5. ใส่ Timestamp อัปเดตล่าสุด
tz = pytz.timezone('Asia/Bangkok')
update_time = datetime.now(tz).strftime("%d/%m/%Y %H:%M")

title_html = f'''
     <div style="position: fixed; bottom: 50px; left: 50px; z-index:9999; font-size:14px; color:white; background:rgba(0,0,0,0.7); padding:10px; border-radius:5px;">
         <b>📡 Auto Weather In Buri</b><br>
         ข้อมูลอัปเดต: {update_time}
     </div>
     '''
m.get_root().html.add_child(folium.Element(title_html))

# 6. บันทึกเป็นไฟล์ index.html (เพื่อให้ GitHub Pages แสดงผล)
m.save("index.html")
print("🎉 สร้างแผนที่สำเร็จ! บันทึกไฟล์ index.html เรียบร้อย")
