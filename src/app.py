import os
from PIL import Image
import pandas as pd
from datetime import datetime
import streamlit as st

# تنظیمات رابط کاربری
st.title("Image Merge Tool")
st.write("این ابزار به شما کمک می‌کند تصاویر را از دو فولدر ترکیب کرده و خروجی بگیرید.")

# ورودی تنظیمات از کاربر
folder_01 = st.text_input("نام فولدر اول:", "01")
folder_02 = st.text_input("نام فولدر دوم:", "02")
export_folder = st.text_input("نام فولدر خروجی:", "export")

input_extension_01 = st.selectbox("پسوند تصاویر فولدر اول:", [".jpg", ".png", ".webp", ".avif"])
input_extension_02 = st.selectbox("پسوند تصاویر فولدر دوم:", [".jpg", ".png", ".webp", ".avif"])
output_extension = st.selectbox("پسوند تصاویر خروجی:", [".jpg", ".png", ".webp", ".avif"])

output_quality = st.slider("کیفیت خروجی (0 تا 100):", 0, 100, 85)

if st.button("شروع عملیات"):
    # ثبت زمان شروع
    start_time = datetime.now()

    # لیست گزارش عملیات
    report_data = []

    # بررسی وجود فولدر export و ایجاد آن در صورت نیاز
    if not os.path.exists(export_folder):
        os.makedirs(export_folder)

    # تابع برای نرمال‌سازی نام فایل‌ها (حذف اسپیس و جایگزینی خط تیره)
    def normalize_name(filename):
        return filename.replace(' ', '-')

    # پیمایش فایل‌ها در فولدر 01
    for filename_01 in os.listdir(folder_01):
        if filename_01.endswith(input_extension_01):
            # نرمال‌سازی نام فایل از فولدر 01
            normalized_name = normalize_name(os.path.splitext(filename_01)[0])

            # جستجوی فایل متناظر در فولدر 02
            file_02_path = None
            for filename_02 in os.listdir(folder_02):
                if filename_02.endswith(input_extension_02) and normalize_name(os.path.splitext(filename_02)[0]) == normalized_name:
                    file_02_path = os.path.join(folder_02, filename_02)
                    break

            if file_02_path:
                try:
                    # مسیر فایل‌های دو فولدر
                    file_01_path = os.path.join(folder_01, filename_01)

                    # بارگذاری تصاویر
                    image1 = Image.open(file_01_path).convert("RGBA")  # تصویر لایه بالا
                    image2 = Image.open(file_02_path).convert("RGBA")  # تصویر بک‌گراند

                    # بررسی تطابق سایز تصاویر
                    if image1.size != image2.size:
                        image1 = image1.resize(image2.size)

                    # ترکیب دو تصویر
                    combined_image = Image.alpha_composite(image2, image1)

                    # ذخیره تصویر ترکیب‌شده
                    output_filename = f"{normalized_name}{output_extension}"
                    output_path = os.path.join(export_folder, output_filename)
                    combined_image = combined_image.convert("RGB")  # تبدیل به RGB برای ذخیره webp
                    combined_image.save(output_path, output_extension[1:], quality=output_quality)

                    # افزودن به گزارش
                    report_data.append({
                        "Input File 1": file_01_path,
                        "Input File 2": file_02_path,
                        "Output File": output_path,
                        "Status": "Success"
                    })

                    st.write(f"تصویر ذخیره شد: {output_path}")
                except Exception as e:
                    # ثبت خطا در گزارش
                    report_data.append({
                        "Input File 1": file_01_path,
                        "Input File 2": file_02_path,
                        "Output File": "-",
                        "Status": f"Failed: {str(e)}"
                    })
            else:
                # ثبت وضعیت عدم تطابق در گزارش
                report_data.append({
                    "Input File 1": os.path.join(folder_01, filename_01),
                    "Input File 2": "Not Found",
                    "Output File": "-",
                    "Status": "No Match"
                })

    # ثبت زمان پایان
    end_time = datetime.now()

    # ایجاد فایل گزارش
    report_df = pd.DataFrame(report_data)
    report_path = os.path.join(export_folder, "operation_report.xlsx")
    report_df.to_excel(report_path, index=False)

    # چاپ اطلاعات زمان شروع و پایان
    st.write(f"زمان شروع عملیات: {start_time}")
    st.write(f"زمان پایان عملیات: {end_time}")
    st.write(f"گزارش عملیات ذخیره شد: {report_path}")

    # لینک دانلود گزارش
    with open(report_path, "rb") as file:
        btn = st.download_button(
            label="دانلود گزارش عملیات",
            data=file,
            file_name="operation_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )