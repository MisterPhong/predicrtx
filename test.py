from datetime import datetime, timedelta, date

# สร้างวันที่ของวันพรุ่งนี้
# tomorrow_date = date.today() + timedelta(days=1)

# สร้าง object datetime สำหรับวันพรุ่งนี้ตอน 7 โมงเช้า
tomorrow_morning = datetime.combine(date.today() + timedelta(days=1), datetime.min.time()).replace(hour=7).strftime('%Y-%m-%d %H:%M:%S')

# แสดงผลวันที่และเวลา
print(tomorrow_morning)