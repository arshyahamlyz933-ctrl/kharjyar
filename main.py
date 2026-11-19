
import flet as ft
import sqlite3
import jdatetime
import os

# ==========================================
# 1. Database
# ==========================================

DB_PATH = os.path.join(os.getcwd(), "khariyar.db")

CATEGORIES = [
    "خوراک",
    "حمل‌ونقل",
    "خانه",
    "سلامت",
    "تفریح",
    "سایر"
]

CATEGORY_ICONS = {
    "خوراک": ft.Icons.FASTFOOD,
    "حمل‌ونقل": ft.Icons.DIRECTIONS_CAR,
    "خانه": ft.Icons.HOME,
    "سلامت": ft.Icons.LOCAL_HOSPITAL,
    "تفریح": ft.Icons.SPORTS_ESPORTS,
    "سایر": ft.Icons.CATEGORY,
}


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount INTEGER NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                date TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)


def add_expense(amount, category, description):
    today = jdatetime.date.today().strftime("%Y/%m/%d")

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO expenses
            (amount, category, description, date)
            VALUES (?, ?, ?, ?)
            """,
            (amount, category, description, today)
        )


def get_expenses(limit=15):
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT id, amount, category, description, date
            FROM expenses
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,)
        ).fetchall()


def get_total():
    with get_connection() as conn:
        result = conn.execute(
            "SELECT SUM(amount) FROM expenses"
        ).fetchone()

    return result[0] or 0


def clear_expenses():
    with get_connection() as conn:
        conn.execute("DELETE FROM expenses")


# ==========================================
# 2. Main Application
# ==========================================

def main(page: ft.Page):

    page.title = "خرج‌یار"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 15
    page.rtl = True
    page.scroll = ft.ScrollMode.AUTO

    total_label = ft.Text(
        "0 تومان",
        size=30,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.GREEN_900
    )

    recent_list = ft.ListView(
        expand=True,
        spacing=10,
        auto_scroll=False
    )

    main_area = ft.Container(expand=True)

    # ==========================================
    # 3. Refresh Dashboard
    # ==========================================

    def load_data():

        recent_list.controls.clear()

        expenses = get_expenses(15)

        if not expenses:
            recent_list.controls.append(
                ft.Container(
                    padding=20,
                    content=ft.Text(
                        "هنوز هزینه‌ای ثبت نکرده‌اید.",
                        color=ft.Colors.GREY,
                        text_align=ft.TextAlign.CENTER
                    )
                )
            )

        else:
            for exp in expenses:

                exp_id, amount, category, desc, date = exp

                recent_list.controls.append(
                    ft.Container(
                        padding=10,
                        border_radius=10,
                        bgcolor=ft.Colors.SURFACE_CONTAINER,
                        content=ft.ListTile(
                            leading=ft.Icon(
                                CATEGORY_ICONS.get(
                                    category,
                                    ft.Icons.CATEGORY
                                ),
                                color=ft.Colors.BLUE_700
                            ),
                            title=ft.Text(
                                desc if desc else category,
                                weight=ft.FontWeight.BOLD
                            ),
                            subtitle=ft.Text(
                                f"{date} - {category}"
                            ),
                            trailing=ft.Text(
                                f"{amount:,} تومان",
                                color=ft.Colors.RED_700,
                                weight=ft.FontWeight.BOLD
                            )
                        )
                    )
                )

        total_label.value = f"{get_total():,} تومان"
        page.update()

    # ==========================================
    # 4. Add Expense
    # ==========================================

    def open_add_expense(e):

        amount_input = ft.TextField(
            label="مبلغ (تومان)",
            keyboard_type=ft.KeyboardType.NUMBER,
            prefix_icon=ft.Icons.ATTACH_MONEY
        )

        desc_input = ft.TextField(
            label="توضیحات (اختیاری)",
            prefix_icon=ft.Icons.EDIT
        )

        category_input = ft.Dropdown(
            label="دسته‌بندی",
            value="خوراک",
            options=[
                ft.DropdownOption(key=c, text=c)
                for c in CATEGORIES
            ]
        )

        def save_expense(e):

            try:
                amount = int(
                    amount_input.value.replace(",", "").strip()
                )

                if amount <= 0:
                    raise ValueError

                add_expense(
                    amount,
                    category_input.value,
                    desc_input.value or ""
                )

                page.pop_dialog()
                load_data()

            except (ValueError, AttributeError):
                amount_input.error_text = (
                    "لطفاً مبلغ معتبر وارد کنید"
                )
                page.update()

        sheet = ft.BottomSheet(
            content=ft.Container(
                padding=20,
                content=ft.Column(
                    tight=True,
                    controls=[
                        ft.Text(
                            "ثبت هزینه جدید",
                            size=22,
                            weight=ft.FontWeight.BOLD
                        ),
                        ft.Divider(),
                        amount_input,
                        category_input,
                        desc_input,
                        ft.Button(
                            content="ذخیره هزینه",
                            icon=ft.Icons.SAVE,
                            width=float("inf"),
                            on_click=save_expense
                        )
                    ]
                )
            )
        )

        page.show_dialog(sheet)

    # ==========================================
    # 5. Dashboard
    # ==========================================

    dashboard_view = ft.Column(
        expand=True,
        controls=[
            ft.Container(
                padding=20,
                border_radius=15,
                bgcolor=ft.Colors.BLUE_50,
                content=ft.Column(
                    horizontal_alignment=(
                        ft.CrossAxisAlignment.CENTER
                    ),
                    controls=[
                        ft.Text(
                            "مجموع کل هزینه‌ها",
                            color=ft.Colors.BLUE_900
                        ),
                        total_label
                    ]
                )
            ),
            ft.Text(
                "هزینه‌های اخیر",
                size=20,
                weight=ft.FontWeight.BOLD
            ),
            recent_list
        ]
    )

    # ==========================================
    # 6. Settings
    # ==========================================

    def toggle_theme(e):

        if page.theme_mode == ft.ThemeMode.LIGHT:
            page.theme_mode = ft.ThemeMode.DARK
        else:
            page.theme_mode = ft.ThemeMode.LIGHT

        page.update()

    def clear_data(e):

        def confirm_clear(ev):
            clear_expenses()
            page.pop_dialog()
            load_data()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("پاک کردن اطلاعات"),
            content=ft.Text(
                "آیا مطمئن هستید که تمام هزینه‌ها حذف شوند؟"
            ),
            actions=[
                ft.TextButton(
                    content="انصراف",
                    on_click=lambda ev: page.pop_dialog()
                ),
                ft.TextButton(
                    content="حذف همه",
                    on_click=confirm_clear
                )
            ]
        )

        page.show_dialog(dialog)

    settings_view = ft.Column(
        controls=[
            ft.Text(
                "تنظیمات",
                size=25,
                weight=ft.FontWeight.BOLD
            ),
            ft.Switch(
                label="حالت تاریک",
                on_change=toggle_theme
            ),
            ft.Divider(),
            ft.Button(
                content="پاک کردن همه داده‌ها",
                icon=ft.Icons.DELETE_FOREVER,
                bgcolor=ft.Colors.RED_600,
                color=ft.Colors.WHITE,
                on_click=clear_data
            )
        ]
    )

    # ==========================================
    # 7. Navigation
    # ==========================================

    def change_tab(e):

        if e.control.selected_index == 0:
            main_area.content = dashboard_view
        else:
            main_area.content = settings_view

        page.update()

    page.navigation_bar = ft.NavigationBar(
        selected_index=0,
        on_change=change_tab,
        destinations=[
            ft.NavigationBarDestination(
                icon=ft.Icons.HOME,
                label="خانه"
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.SETTINGS,
                label="تنظیمات"
            )
        ]
    )

    page.floating_action_button = ft.FloatingActionButton(
        icon=ft.Icons.ADD,
        bgcolor=ft.Colors.GREEN_600,
        on_click=open_add_expense
    )

    main_area.content = dashboard_view

    page.add(main_area)

    load_data()


# ==========================================
# 8. Run Application
# ==========================================

if __name__ == "__main__":
    init_db()
    ft.run(main)
    
