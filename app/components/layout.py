import reflex as rx
from app.states.auth_state import AuthState


def sidebar_item(
    label: str, icon: str, href: str, active: rx.Var[bool]
) -> rx.Component:
    return rx.el.a(
        rx.icon(icon, class_name="h-5 w-5 mr-3"),
        rx.el.span(label),
        href=href,
        class_name=rx.cond(
            active,
            "flex items-center px-4 py-3 rounded-lg transition-colors font-medium bg-orange-50 text-orange-600",
            "flex items-center px-4 py-3 rounded-lg transition-colors font-medium text-gray-600 hover:bg-gray-100 hover:text-gray-900",
        ),
    )


def layout(content: rx.Component) -> rx.Component:
    return rx.el.div(
        rx.el.aside(
            rx.el.div(
                rx.el.div(
                    rx.icon("utensils-crossed", class_name="h-7 w-7 text-orange-500"),
                    rx.el.span(
                        "Qmeal Admin", class_name="text-xl font-bold text-gray-900"
                    ),
                    class_name="flex h-16 items-center gap-3 border-b border-gray-200 px-6",
                ),
                rx.el.nav(
                    sidebar_item(
                        "Dashboard",
                        "layout-dashboard",
                        "/dashboard",
                        active=rx.State.router.page.path == "/dashboard",
                    ),
                    sidebar_item(
                        "Restaurants",
                        "store",
                        "/restaurants",
                        active=rx.State.router.page.path.contains("/restaurants"),
                    ),
                    sidebar_item(
                        "Orders",
                        "shopping-bag",
                        "/orders",
                        active=rx.State.router.page.path.contains("/orders"),
                    ),
                    sidebar_item(
                        "Users",
                        "users",
                        "/users",
                        active=rx.State.router.page.path.contains("/users"),
                    ),
                    sidebar_item(
                        "Riders",
                        "bike",
                        "/riders",
                        active=rx.State.router.page.path.contains("/riders"),
                    ),
                    sidebar_item(
                        "Settings",
                        "settings",
                        "/settings",
                        active=rx.State.router.page.path.contains("/settings"),
                    ),
                    sidebar_item(
                        "API Docs",
                        "code",
                        "/docs",
                        active=rx.State.router.page.path.contains("/docs"),
                    ),
                    class_name="flex w-full flex-col gap-2 px-4 py-6 text-sm",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            rx.cond(
                                AuthState.user_name.length() > 0,
                                rx.el.span(
                                    AuthState.user_name[0].upper(),
                                    class_name="text-orange-600 font-bold",
                                ),
                                rx.el.span("U", class_name="text-orange-600 font-bold"),
                            ),
                            class_name="h-8 w-8 rounded-full bg-orange-100 flex items-center justify-center mr-3",
                        ),
                        rx.el.div(
                            rx.el.p(
                                AuthState.user_name,
                                class_name="text-sm font-medium text-gray-900",
                            ),
                            rx.el.p(
                                AuthState.user_role,
                                class_name="text-xs text-gray-500 capitalize",
                            ),
                        ),
                        class_name="flex items-center",
                    ),
                    rx.el.button(
                        rx.icon(
                            "log-out",
                            class_name="h-5 w-5 text-gray-500 hover:text-red-500 transition-colors",
                        ),
                        on_click=AuthState.logout,
                        class_name="p-2",
                    ),
                    class_name="mt-auto border-t border-gray-200 p-4 flex items-center justify-between",
                ),
                class_name="flex-1 flex flex-col h-full",
            ),
            class_name="flex flex-col border-r border-gray-200 w-64 h-screen shrink-0 bg-white shadow-sm",
        ),
        rx.el.main(
            rx.el.header(
                rx.el.div(
                    rx.el.h2(
                        "Overview", class_name="text-xl font-semibold text-gray-800"
                    ),
                    rx.el.div(
                        rx.icon(
                            "bell",
                            class_name="h-5 w-5 text-gray-500 cursor-pointer hover:text-gray-700",
                        ),
                        class_name="flex items-center gap-4",
                    ),
                    class_name="flex items-center justify-between h-16 px-8 bg-white border-b border-gray-200",
                ),
                class_name="w-full",
            ),
            rx.el.div(
                content, class_name="flex-1 p-8 overflow-auto h-[calc(100vh-4rem)]"
            ),
            class_name="flex-1 flex flex-col min-h-screen bg-gray-50",
        ),
        class_name="flex min-h-screen w-full font-['Inter']",
    )