import flet as ft
import sqlite3
import jdatetime
from datetime import datetime

==========================================

۱. تنظیمات دیتابیس

==========================================

def init_db():
conn = sqlite3.connect("khariyar.db")
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS expenses (
id INTEGER PRIMARY KEY AUTOINCREMENT,
amount INTEGER,
category TEXT,
description TEXT,
date TEXT,
timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')
conn.commit()
conn.close()

def add_expense(amount, category, description):
conn = sqlite3.connect("khariyar.db")
cursor = conn.cursor()
today = jdatetime.date.today().strftime("%Y/%m/%d")
cursor.execute("INSERT INTO expenses (amount, category, description, date) VALUES (?, ?, ?, ?)",
(amount, category, description, today))
conn.commit()
conn.close()

def get_expenses(limit=None):
conn = sqlite3.connect("khariyar.db")
cursor = conn.cursor()
query = "SELECT id, amount, category, description, date FROM expenses ORDER BY id DESC"
if limit:
query += f" LIMIT {limit}"
cursor.execute(query)
rows = cursor.fetchall()
conn.close()
return rows

def get_total():
conn = sqlite3.connect("khariyar.db")
cursor = conn.cursor()
cursor.execute("SELECT SUM(amount) FROM expenses")
total = cursor.fetchone()[0]
conn.close()
return total or 0

==========================================

۲. رابط کاربری اصلی

==========================================

def main(page: ft.Page):
page.title = "خرج‌یار"
page.rtl = True
page.theme_mode = ft.ThemeMode.LIGHT
page.padding = 20
page.window_width = 400
page.window_height = 700

# رنگ‌بندی دسته‌بندی‌ها  
categories = {  
    "خوراک": ft.icons.FASTFOOD,  
    "حمل‌ونقل": ft.icons.DIRECTIONS_CAR,  
    "خانه": ft.icons.HOME,  
    "سلامت": ft.icons.LOCAL_HOSPITAL,  
    "تفریح": ft.icons.SPORTS_ESPORTS,  
    "سایر": ft.icons.CATEGORY  
}  

# متغیر برای ذخیره لیست هزینه‌ها  
recent_expenses_list = ft.ListView(expand=True, spacing=10)  

def load_data():  
    """بارگذاری مجدد داده‌ها در صفحه"""  
    recent_expenses_list.controls.clear()  
    expenses = get_expenses(limit=15)  
      
    if not expenses:  
        recent_expenses_list.controls.append(  
            ft.Text("هنوز هزینه‌ای ثبت نکرده‌اید.", color=ft.colors.GREY, text_align=ft.TextAlign.CENTER)  
        )  
    else:  
        for exp in expenses:  
            exp_id, amount, category, desc, date = exp  
            recent_expenses_list.controls.append(  
                ft.Container(  
                    content=ft.ListTile(  
                        leading=ft.Icon(categories.get(category, ft.icons.CATEGORY), color=ft.colors.BLUE_700),  
                        title=ft.Text(desc if desc else category, weight=ft.FontWeight.BOLD),  
                        subtitle=ft.Text(f"{date} - {category}"),  
                        trailing=ft.Text(f"{amount:,} تومان", weight=ft.FontWeight.BOLD, color=ft.colors.RED_700)  
                    ),  
                    bgcolor=ft.colors.SURFACE_VARIANT,  
                    border_radius=10  
                )  
            )  
      
    # آپدیت جمع کل  
    total_lbl.value = f"{get_total():,} تومان"  
    page.update()  

# ==========================================  
# ۳. فرم ثبت هزینه (BottomSheet)  
# ==========================================  
def open_add_expense(e):  
    amount_input = ft.TextField(label="مبلغ (تومان)", keyboard_type=ft.KeyboardType.NUMBER, prefix_icon=ft.icons.ATTACH_MONEY)  
    desc_input = ft.TextField(label="توضیحات (اختیاری)", prefix_icon=ft.icons.EDIT)  
      
    # انتخاب دسته بندی  
    cat_dropdown = ft.Dropdown(  
        label="دسته‌بندی",  
        options=[ft.dropdown.Option(key=k, text=k) for k in categories.keys()],  
        value="خوراک"  
    )  

    def save_expense(e):  
        try:  
            amount = int(amount_input.value.replace(",", ""))  
            if amount <= 0: raise ValueError  
            add_expense(amount, cat_dropdown.value, desc_input.value)  
            bs.open = False  
            load_data() # رفرش کردن لیست  
        except ValueError:  
            amount_input.error_text = "لطفاً یک عدد معتبر وارد کنید"  
            page.update()  

    bs = ft.BottomSheet(  
        ft.Container(  
            padding=20,  
            content=ft.Column([  
                ft.Text("ثبت هزینه جدید", size=20, weight=ft.FontWeight.BOLD),  
                ft.Divider(),  
                amount_input,  
                cat_dropdown,  
                desc_input,  
                ft.ElevatedButton(  
                    "ذخیره",   
                    icon=ft.icons.SAVE,   
                    bgcolor=ft.colors.GREEN_600,   
                    color=ft.colors.WHITE,  
                    width=page.width,  
                    on_click=save_expense  
                )  
            ], tight=True)  
        ),  
        open=True  
    )  
    page.overlay.append(bs)  
    page.update()  

# ==========================================  
# ۴. چیدمان صفحات (Tabs)  
# ==========================================  
  
# صفحه اول: داشبورد  
total_lbl = ft.Text("0 تومان", size=30, weight=ft.FontWeight.BOLD, color=ft.colors.GREEN_900)  
  
dashboard_view = ft.Column([  
    ft.Container(  
        padding=20,  
        bgcolor=ft.colors.BLUE_50,  
        border_radius=15,  
        content=ft.Column([  
            ft.Text("مجموع کل هزینه‌ها", color=ft.colors.BLUE_900),  
            total_lbl  
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)  
    ),  
    ft.Text("هزینه‌های اخیر", size=18, weight=ft.FontWeight.BOLD),  
    recent_expenses_list  
], expand=True)  

# صفحه دوم: تنظیمات  
def toggle_theme(e):  
    page.theme_mode = ft.ThemeMode.DARK if page.theme_mode == ft.ThemeMode.LIGHT else ft.ThemeMode.LIGHT  
    page.update()  

def clear_data(e):  
    conn = sqlite3.connect("khariyar.db")  
    conn.execute("DELETE FROM expenses")  
    conn.commit()  
    conn.close()  
    load_data()  

settings_view = ft.Column([  
    ft.Text("تنظیمات", size=24, weight=ft.FontWeight.BOLD),  
    ft.Switch(label="حالت تاریک (Dark Mode)", on_change=toggle_theme),  
    ft.Divider(),  
    ft.ElevatedButton(  
        "پاک کردن همه داده‌ها",   
        icon=ft.icons.DELETE_FOREVER,   
        color=ft.colors.WHITE,   
        bgcolor=ft.colors.RED_600,  
        on_click=clear_data  
    )  
])  

# مدیریت تعویض تب‌ها  
main_content_area = ft.Container(content=dashboard_view, expand=True)  

def change_tab(e):  
    if e.control.selected_index == 0:  
        main_content_area.content = dashboard_view  
    elif e.control.selected_index == 1:  
        main_content_area.content = settings_view  
    page.update()  

# دکمه شناور ثبت هزینه  
floating_btn = ft.FloatingActionButton(  
    icon=ft.icons.ADD,  
    bgcolor=ft.colors.GREEN_600,  
    on_click=open_add_expense  
)  

# نوار ناوبری پایین  
nav_bar = ft.NavigationBar(  
    selected_index=0,  
    on_change=change_tab,  
    destinations=[  
        ft.NavigationDestination(icon=ft.icons.HOME, label="خانه"),  
        ft.NavigationDestination(icon=ft.icons.SETTINGS, label="تنظیمات"),  
    ]  
)  

# اضافه کردن همه چیز به صفحه  
page.add(main_content_area)  
page.navigation_bar = nav_bar  
page.floating_action_button = floating_btn  
  
# بارگذاری اولیه داده‌ها  
load_data()

اجرای اپلیکیشن

init_db()
ft.app(target=main)
