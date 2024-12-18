import flet as ft
from services.firebase import get_current_user, get_user_data, logout, db
from utils.helpers import show_success_snackbar, show_error_snackbar
from components.nav_bar import NavBar
from components.header import HeaderBar
from services.auth import hash_password

def show_account_page(page: ft.Page, router):
    user_id = get_current_user()
    user_data = get_user_data(user_id)

    if user_data is None:
        show_error_snackbar(page, "User data not found.")
        router.navigate("/home")
        return

    def handle_logout(e):
        logout()
        show_success_snackbar(page, "Logged out successfully!")
        router.navigate("/login")

    def handle_back(e):
        router.navigate_back()

    def handle_save_profile(e):
        try:
            # Get the updated values from text fields
            new_name = name_field.value.split()
            if len(new_name) != 2:
                show_error_snackbar(page, "Please enter both first and last name.")
                return
                
            new_firstname, new_lastname = new_name
            new_email = email_field.value
            new_password = password_field.value.replace('•', '') if not password_field.password else password_field.value
            hashed_password = hash_password(new_password)

            # Update the database
            db.collection('Users').document(user_id).update({
                'firstname': new_firstname,
                'lastname': new_lastname,
                'email': new_email,
                'password': hashed_password.decode('utf-8')
            })

            # Update the user data in memory
            user_data.update({
                'firstname': new_firstname,
                'lastname': new_lastname,
                'email': new_email,
                'password': hashed_password.decode('utf-8')
            })

            show_success_snackbar(page, "Profile updated successfully!")
        except Exception as e:
            show_error_snackbar(page, f"Error updating profile: {str(e)}")


    # Update the profile section styling
    name_field = ft.TextField(
        value=f"{user_data['firstname']} {user_data['lastname']}", 
        prefix_icon=ft.Icons.PERSON,
        label="Full Name",
        border=ft.InputBorder.UNDERLINE,
        height=50,
    )

    email_field = ft.TextField(
        value=user_data['email'],
        prefix_icon=ft.Icons.EMAIL,
        label="Email",
        border=ft.InputBorder.UNDERLINE,
        height=50,
    )

    password_field = ft.TextField(
        value="",
        prefix_icon=ft.Icons.LOCK,
        password=True,
        can_reveal_password=True,
        label="New Password",
        border=ft.InputBorder.UNDERLINE,
        height=50,
    )

    profile_section = ft.Container(
        content=ft.Column([
            # Profile picture with network image
            ft.Container(
                content=ft.CircleAvatar(
                    foreground_image_url="https://fastly.picsum.photos/id/501/200/200.jpg?hmac=tKXe69j4tHhkAA_Qc3XinkTuubEWwkFVhA9TR4TmCG8",
                    radius=75,
                ),
                alignment=ft.alignment.center,
                padding=ft.padding.only(bottom=20),
            ),
            # Form fields in a card
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        name_field,
                        email_field,
                        password_field,
                    ], spacing=10),
                    padding=20,
                ),
                elevation=0,
            ),

            # Centered Save Profile button
            ft.Container(
                content=ft.ElevatedButton(
                    "Save profile",
                    on_click=handle_save_profile,
                    style=ft.ButtonStyle(
                        color=ft.colors.WHITE,
                        bgcolor=ft.colors.BLUE,
                        shape=ft.RoundedRectangleBorder(radius=15),
                    ),
                    width=300,
                    height=50,
                ),
                alignment=ft.alignment.center,
                padding=ft.padding.only(top=20),
            ),
        ]),
        padding=20,
        expand=True
    )

    # Header with back button, profile title, and logout button
    header = ft.Container(
        content=ft.Row([
            HeaderBar(router),
            ft.Text("Profile", size=24, weight=ft.FontWeight.BOLD),
            ft.IconButton(
                icon=ft.icons.LOGOUT,
                icon_color=ft.colors.RED_500,
                on_click=handle_logout,
                tooltip="Logout",  # Added tooltip for better UX
            )
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        padding=ft.padding.symmetric(horizontal=20, vertical=5),
        expand=True
    )

    # Combine header and profile section
    page_content = ft.Column([
        header,
        profile_section
    ])

    nav_bar = NavBar(router=router, active_route="/account")

    return ft.View(
        route="/account",
        controls=[page_content, nav_bar],
        vertical_alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        padding=0
    )