import os
import requests
import folium
from folium import Icon, CustomIcon
from datetime import datetime
import pytz

# 1. ดึง Key (เหมือนเดิม)
API_KEY = os.environ.get('OPENWEATHER_API_KEY')
if not API_KEY: raise ValueError("❌ ไม่พบ API Key")

# 2. รายชื่อจุดตรวจวัด (ตรงนี้แหละที่คุณต้องเอาพิกัดเป๊ะๆ จาก Google Maps มาใส่!)
locations = [
    {"name": "ตลาดอินทร์บุรี (จุดหลัก)", "lat": 15.0065, "lon": 100.3268}, # <-- ลองแก้พิกัดให้เป๊ะดูครับ
    {"name": "ต.ทับยา", "lat": 14.980, "lon": 100.310},
    {"name": "ต.ทองเอน", "lat": 15.050, "lon": 100.350},
    {"name": "ต.ชีน้ำร้าย", "lat": 14.950, "lon": 100.300},
    {"name": "ต.น้ำตาล", "lat": 14.990, "lon": 100.340},
    {"name": "ต.งิ้วราย", "lat": 14.970, "lon": 100.330},
    {"name": "ต.ประศุก", "lat": 15.030, "lon": 100.380},
]

# --- ลิงก์รูปไอคอนการ์ตูน 3D (ใช้ของฟรีจากเน็ตไปก่อน) ---
# ถ้าในอนาคตคุณมีรูปสวยๆ ของตัวเอง สามารถเปลี่ยนลิงก์ตรงนี้ได้ครับ
ICON_SUNNY = "https://cdn-icons-png.flaticon.com/512/2921/2921839.png"  # แดดออก (รูปดวงอาทิตย์ยิ้ม)
ICON_RAINY = "https://cdn-icons-png.flaticon.com/512/2921/2921949.png"  # ฝนตก (รูปเมฆมีหยดน้ำ)
ICON_STORM = "https://cdn-icons-png.flaticon.com/512/2921/2921970.png"  # พายุ (รูปเมฆมีสายฟ้า)


# 3. สร้างแผนที่พื้นหลัง (เปลี่ยนจาก Dark Mode เป็นแนวสีน้ำ สว่างๆ น่ารัก)
# ใช้ tiles='Stamen Watercolor' เพื่อให้ดูเป็นภาพวาด
# หมายเหตุ: ถ้า Stamen โหลดช้า อาจเปลี่ยนเป็น 'OpenStreetMap' แทนได้ แต่จะไม่สวยเท่า
m = folium.Map(location=[15.006, 100.326], zoom_start=12, tiles='OpenStreetMap')

print("กำลังดึงข้อมูลสภาพอากาศ V3 (Cute Mode)...")

for loc in locations:
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={loc['lat']}&lon={loc['lon']}&appid={API_KEY}&units=metric&lang=th"
        response = requests.get(url)
        data = response.json()

        if response.status_code != 200: continue

        temp = round(data['main']['temp'], 1)
        rain_1h = data.get('rain', {}).get('1h', 0)
        desc = data['weather'][0]['description']

        # Logic เลือกรูปไอคอนให้ตรงกับอากาศ
        if rain_1h > 10:
            icon_url = ICON_STORM
            status_text = "พายุเข้า!"
            bg_color = "#ffcccc" # พื้นหลังpopupสีแดงอ่อน
        elif rain_1h > 0:
            icon_url = ICON_RAINY
            status_text = "มีฝนตก"
            bg_color = "#ccf2ff" # พื้นหลังpopupสีฟ้าอ่อน
        else:
            icon_url = ICON_SUNNY
            status_text = "อากาศดี"
            bg_color = "#ccffcc" # พื้นหลังpopupสีเขียวอ่อน

        # สร้างไอคอนแบบกำหนดเอง (CustomIcon)
        weather_icon = CustomIcon(
            icon_image=icon_url,
            icon_size=(60, 60), # ขนาดไอคอน (ปรับให้ใหญ่ขึ้นจะได้ดูเป็น 3D ชัดๆ)
            icon_anchor=(30, 60), # จุดปัก (ให้ตรงกลางด้านล่างของรูปปักลงพิกัดพอดี)
            popup_anchor=(0, -60) # จุดที่ Popup เด้งขึ้นมา
        )

        # สร้าง Popup แบบน่ารักๆ
        popup_html = f"""
        <div style="font-family: 'Comic Sans MS', 'Chalkboard SE', sans-serif; text-align: center; background-color: {bg_color}; padding: 10px; border-radius: 15px; border: 2px solid white; box-shadow: 3px 3px 5px rgba(0,0,0,0.2);">
            <h4 style="margin:0; color:#333;">🏡 {loc['name']}</h4>
            <img src="{icon_url}" width="50" style="margin: 5px;">
            <br>
            <b style="color:#555; font-size: 16px;">{status_text}</b><br>
            <span style="font-size: 14px;">( {desc} )</span><br>
            <hr style="border-top: 1px dashed #999;">
            🌡️ อุณหภูมิ: <b>{temp}°C</b><br>
            💧 ฝน 1 ชม.: <b>{rain_1h} มม.</b>
        </div>
        """

        # ปักหมุดลงแผนที่ (ใช้ Marker แทน CircleMarker)
        folium.Marker(
            location=[loc['lat'], loc['lon']],
            icon=weather_icon,
            popup=folium.Popup(popup_html, max_width=250)
        ).add_to(m)

    except Exception as e:
        print(f"Error {loc['name']}: {e}")

# 4. ป้ายชื่อโครงการแบบน่ารัก (มุมซ้ายล่าง)
tz = pytz.timezone('Asia/Bangkok')
update_time = datetime.now(tz).strftime("%H:%M")

title_html = f'''
     <div style="position: fixed; bottom: 20px; left: 20px; z-index:9999; font-family: 'Comic Sans MS', cursive; background: white; padding: 15px; border-radius: 20px; border: 3px solid #FFD700; box-shadow: 5px 5px 0px #FF9900;">
         <h3 style="margin:0; color:#FF6600; text-shadow: 1px 1px 0px #FFCC00;">🌈 แผนที่อากาศอินทร์บุรี</h3>
         <small style="color:#666;">อัปเดตล่าสุด: {update_time} น.</small>
     </div>
     '''
m.get_root().html.add_child(folium.Element(title_html))

m.save("index.html")
print("🎉 เปลี่ยนเป็นธีมการ์ตูนน่ารักสำเร็จ!")
