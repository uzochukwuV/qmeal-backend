import reflex as rx
from app.states.auth_state import AuthState
from app.states.dashboard_state import DashboardState
from app.states.users_state import UsersState
from app.states.riders_state import RidersState
from app.states.settings_state import SettingsState
from app.components.layout import layout


def stat_card(title: str, value: str, icon: str) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.h3(title, class_name="text-sm font-medium text-gray-500"),
                rx.el.p(value, class_name="text-2xl font-bold text-gray-900 mt-1"),
            ),
            rx.el.div(
                rx.icon(icon, class_name="h-6 w-6 text-orange-500"),
                class_name="p-3 bg-orange-50 rounded-lg",
            ),
            class_name="flex items-center justify-between",
        ),
        class_name="bg-white p-6 rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition-shadow",
    )


def dashboard_page() -> rx.Component:
    return layout(
        rx.el.div(
            rx.el.div(
                stat_card("Total Users", f"{DashboardState.total_users}", "users"),
                stat_card(
                    "Restaurants", f"{DashboardState.total_restaurants}", "store"
                ),
                stat_card(
                    "Total Orders", f"{DashboardState.total_orders}", "shopping-bag"
                ),
                stat_card(
                    "Total Revenue",
                    f"${DashboardState.total_revenue:.2f}",
                    "dollar-sign",
                ),
                class_name="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6 mb-8",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.h3(
                        "Recent Orders",
                        class_name="text-lg font-semibold text-gray-800 mb-4",
                    ),
                    rx.el.div(
                        rx.el.table(
                            rx.el.thead(
                                rx.el.tr(
                                    rx.el.th(
                                        "Order ID",
                                        class_name="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                    ),
                                    rx.el.th(
                                        "Restaurant",
                                        class_name="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                    ),
                                    rx.el.th(
                                        "Customer",
                                        class_name="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                    ),
                                    rx.el.th(
                                        "Status",
                                        class_name="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                    ),
                                    rx.el.th(
                                        "Total",
                                        class_name="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                    ),
                                    class_name="bg-gray-50 border-b border-gray-200",
                                )
                            ),
                            rx.el.tbody(
                                rx.foreach(
                                    DashboardState.recent_orders,
                                    lambda order: rx.el.tr(
                                        rx.el.td(
                                            order["order_id"],
                                            class_name="px-4 py-4 whitespace-nowrap text-sm font-medium text-gray-900",
                                        ),
                                        rx.el.td(
                                            order["restaurant_name"],
                                            class_name="px-4 py-4 whitespace-nowrap text-sm text-gray-600",
                                        ),
                                        rx.el.td(
                                            order["customer"],
                                            class_name="px-4 py-4 whitespace-nowrap text-sm text-gray-600",
                                        ),
                                        rx.el.td(
                                            rx.el.span(
                                                order["status"],
                                                class_name=f"{rx.match(order['status'], ('pending', 'bg-yellow-100 text-yellow-800'), ('confirmed', 'bg-blue-100 text-blue-800'), ('preparing', 'bg-orange-100 text-orange-800'), ('delivered', 'bg-green-100 text-green-800'), ('cancelled', 'bg-red-100 text-red-800'), 'bg-gray-100 text-gray-800')} px-2.5 py-1 rounded-full text-xs font-medium capitalize",
                                            ),
                                            class_name="px-4 py-4 whitespace-nowrap",
                                        ),
                                        rx.el.td(
                                            f"${order['total']:.2f}",
                                            class_name="px-4 py-4 whitespace-nowrap text-sm font-medium text-gray-900",
                                        ),
                                        class_name="hover:bg-gray-50 transition-colors border-b border-gray-100",
                                    ),
                                )
                            ),
                            class_name="min-w-full text-left",
                        ),
                        class_name="overflow-x-auto",
                    ),
                    class_name="bg-white p-6 rounded-xl border border-gray-200 shadow-sm col-span-1 lg:col-span-2",
                ),
                rx.el.div(
                    rx.el.h3(
                        "Top Restaurants",
                        class_name="text-lg font-semibold text-gray-800 mb-4",
                    ),
                    rx.el.div(
                        rx.foreach(
                            DashboardState.top_restaurants,
                            lambda rest: rx.el.div(
                                rx.el.div(
                                    rx.el.h4(
                                        rest["name"],
                                        class_name="text-sm font-semibold text-gray-900",
                                    ),
                                    rx.el.p(
                                        rest["cuisine_type"],
                                        class_name="text-xs text-gray-500",
                                    ),
                                ),
                                rx.el.div(
                                    rx.icon(
                                        "star",
                                        class_name="h-4 w-4 text-yellow-400 mr-1",
                                    ),
                                    rx.el.span(
                                        f"{rest['rating']:.1f}",
                                        class_name="text-sm font-medium text-gray-700",
                                    ),
                                    class_name="flex items-center bg-gray-50 px-2 py-1 rounded border border-gray-100",
                                ),
                                class_name="flex items-center justify-between p-4 border border-gray-100 rounded-lg mb-3 hover:border-orange-200 transition-colors",
                            ),
                        ),
                        class_name="flex flex-col",
                    ),
                    class_name="bg-white p-6 rounded-xl border border-gray-200 shadow-sm col-span-1",
                ),
                class_name="grid grid-cols-1 lg:grid-cols-3 gap-6",
            ),
        )
    )


def login_page() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.icon(
                        "utensils-crossed",
                        class_name="h-12 w-12 text-orange-500 mx-auto",
                    ),
                    rx.el.h2(
                        "Welcome to Qmeal",
                        class_name="mt-6 text-3xl font-extrabold text-gray-900",
                    ),
                    rx.el.p(
                        "Sign in to your admin account",
                        class_name="mt-2 text-sm text-gray-600",
                    ),
                    class_name="text-center mb-8",
                ),
                rx.cond(
                    AuthState.login_error,
                    rx.el.div(
                        AuthState.login_error,
                        class_name="mb-4 bg-red-50 text-red-600 px-4 py-3 rounded-lg text-sm border border-red-200",
                    ),
                    rx.el.div(),
                ),
                rx.el.form(
                    rx.el.div(
                        rx.el.label(
                            "Email address",
                            class_name="block text-sm font-medium text-gray-700 mb-1",
                        ),
                        rx.el.input(
                            name="email",
                            type="email",
                            required=True,
                            placeholder="admin@qmeal.com",
                            class_name="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-orange-500 focus:border-orange-500 sm:text-sm",
                        ),
                        class_name="mb-4",
                    ),
                    rx.el.div(
                        rx.el.label(
                            "Password",
                            class_name="block text-sm font-medium text-gray-700 mb-1",
                        ),
                        rx.el.input(
                            name="password",
                            type="password",
                            required=True,
                            placeholder="••••••••",
                            class_name="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-orange-500 focus:border-orange-500 sm:text-sm",
                        ),
                        class_name="mb-6",
                    ),
                    rx.el.button(
                        rx.cond(
                            AuthState.is_loading,
                            rx.el.span(
                                "Signing in...",
                                class_name="flex items-center justify-center",
                            ),
                            rx.el.span(
                                "Sign in", class_name="flex items-center justify-center"
                            ),
                        ),
                        type="submit",
                        disabled=AuthState.is_loading,
                        class_name="w-full flex justify-center py-2.5 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-orange-600 hover:bg-orange-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500 transition-colors disabled:opacity-50",
                    ),
                    on_submit=AuthState.login,
                ),
                class_name="bg-white py-10 px-8 shadow-xl rounded-2xl sm:px-12 w-full max-w-md border border-gray-100",
            ),
            class_name="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8",
        ),
        class_name="min-h-screen bg-gray-50 font-['Inter']",
    )


from app.states.restaurant_state import RestaurantState
from app.states.orders_state import OrdersState


def restaurants_page() -> rx.Component:
    return layout(
        rx.el.div(
            rx.el.div(
                rx.el.h1("Restaurants", class_name="text-2xl font-bold text-gray-900"),
                rx.el.span(
                    f"{RestaurantState.restaurants.length()} total",
                    class_name="px-2.5 py-0.5 rounded-full bg-orange-100 text-orange-800 text-sm font-medium",
                ),
                class_name="flex items-center gap-4 mb-8",
            ),
            rx.el.div(
                rx.el.input(
                    placeholder="Search restaurants...",
                    default_value=RestaurantState.search_query,
                    on_change=RestaurantState.set_search_query.debounce(500),
                    class_name="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500",
                ),
                rx.el.select(
                    rx.el.option("All Cuisines", value=""),
                    rx.foreach(
                        RestaurantState.cuisines,
                        lambda cuisine: rx.el.option(cuisine, value=cuisine),
                    ),
                    value=RestaurantState.cuisine_filter,
                    on_change=RestaurantState.set_cuisine_filter,
                    class_name="w-48 px-4 py-2 appearance-none border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500",
                ),
                class_name="flex flex-col sm:flex-row gap-4 mb-6",
            ),
            rx.el.div(
                rx.foreach(
                    RestaurantState.restaurants,
                    lambda rest: rx.el.div(
                        rx.el.div(
                            rx.el.div(
                                rx.el.h3(
                                    rest["name"],
                                    class_name="text-lg font-bold text-gray-900",
                                ),
                                rx.el.span(
                                    rest["cuisine_type"],
                                    class_name="px-2 py-1 bg-gray-100 text-gray-600 text-xs font-medium rounded",
                                ),
                                class_name="flex items-start justify-between mb-2",
                            ),
                            rx.el.div(
                                rx.icon(
                                    "star", class_name="w-4 h-4 text-yellow-400 mr-1"
                                ),
                                rx.el.span(
                                    f"{rest['rating']}",
                                    class_name="text-sm font-medium text-gray-700",
                                ),
                                rx.el.span(
                                    f"({rest['review_count']} reviews)",
                                    class_name="text-sm text-gray-500 ml-1",
                                ),
                                class_name="flex items-center mb-3",
                            ),
                            rx.el.p(
                                rest["address"],
                                class_name="text-sm text-gray-500 truncate mb-4",
                            ),
                            rx.el.div(
                                rx.el.div(
                                    rx.icon(
                                        "clock", class_name="w-4 h-4 text-gray-400 mr-1"
                                    ),
                                    rx.el.span(
                                        f"{rest['delivery_time_min']}-{rest['delivery_time_max']} min",
                                        class_name="text-sm text-gray-600",
                                    ),
                                    class_name="flex items-center",
                                ),
                                rx.el.div(
                                    rx.cond(
                                        rest["is_open"],
                                        rx.el.span(
                                            "Open",
                                            class_name="text-sm text-green-600 font-medium flex items-center gap-1 before:content-[''] before:w-2 before:h-2 before:bg-green-500 before:rounded-full",
                                        ),
                                        rx.el.span(
                                            "Closed",
                                            class_name="text-sm text-red-600 font-medium flex items-center gap-1 before:content-[''] before:w-2 before:h-2 before:bg-red-500 before:rounded-full",
                                        ),
                                    ),
                                    on_click=lambda: RestaurantState.toggle_restaurant_status(
                                        rest["restaurant_id"], rest["is_open"]
                                    ),
                                    class_name="cursor-pointer hover:bg-gray-50 p-1 rounded transition-colors",
                                ),
                                class_name="flex items-center justify-between mt-auto",
                            ),
                            class_name="p-5 flex flex-col h-full",
                        ),
                        rx.el.div(
                            rx.el.a(
                                "View Details",
                                href=f"/restaurants/{rest['restaurant_id']}",
                                class_name="text-orange-600 font-medium hover:text-orange-700 text-sm",
                            ),
                            class_name="px-5 py-3 bg-gray-50 border-t border-gray-100 flex justify-end",
                        ),
                        class_name="bg-white rounded-xl border border-gray-200 shadow-sm flex flex-col hover:shadow-md transition-shadow",
                    ),
                ),
                class_name="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6",
            ),
        )
    )


def restaurant_detail_page() -> rx.Component:
    return layout(
        rx.el.div(
            rx.el.a(
                rx.icon("arrow-left", class_name="w-4 h-4 mr-2"),
                "Back to Restaurants",
                href="/restaurants",
                class_name="inline-flex items-center text-sm font-medium text-gray-500 hover:text-gray-700 mb-6",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.h1(
                            RestaurantState.selected_restaurant["name"],
                            class_name="text-3xl font-bold text-gray-900",
                        ),
                        rx.el.button(
                            "Edit Details",
                            on_click=RestaurantState.toggle_edit_modal,
                            class_name="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium text-sm",
                        ),
                        class_name="flex items-center justify-between mb-4",
                    ),
                    rx.el.p(
                        RestaurantState.selected_restaurant["description"],
                        class_name="text-gray-600 mb-6 max-w-3xl",
                    ),
                    class_name="bg-white p-8 rounded-xl border border-gray-200 shadow-sm mb-8",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            rx.el.h2(
                                "Menu Items",
                                class_name="text-xl font-bold text-gray-900",
                            ),
                            rx.el.button(
                                "Add Item",
                                on_click=RestaurantState.toggle_add_menu_modal,
                                class_name="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 font-medium text-sm",
                            ),
                            class_name="flex items-center justify-between mb-6",
                        ),
                        rx.el.div(
                            rx.foreach(
                                RestaurantState.menu_items,
                                lambda item: rx.el.div(
                                    rx.el.div(
                                        rx.el.h4(
                                            item["name"],
                                            class_name="font-bold text-gray-900",
                                        ),
                                        rx.el.p(
                                            item["description"],
                                            class_name="text-sm text-gray-500 mt-1",
                                        ),
                                    ),
                                    rx.el.div(
                                        rx.el.span(
                                            f"${item['price']}",
                                            class_name="font-bold text-gray-900 mr-4",
                                        ),
                                        rx.el.button(
                                            rx.icon("trash-2", class_name="w-4 h-4"),
                                            on_click=lambda: RestaurantState.delete_menu_item(
                                                item["item_id"]
                                            ),
                                            class_name="text-red-500 hover:text-red-700 p-2",
                                        ),
                                        class_name="flex items-center",
                                    ),
                                    class_name="flex items-center justify-between p-4 border border-gray-100 rounded-lg mb-3 hover:border-gray-200 transition-colors",
                                ),
                            ),
                            class_name="flex flex-col",
                        ),
                        class_name="bg-white p-6 rounded-xl border border-gray-200 shadow-sm col-span-2",
                    ),
                    rx.el.div(
                        rx.el.h2(
                            "Recent Reviews",
                            class_name="text-xl font-bold text-gray-900 mb-6",
                        ),
                        rx.el.div(
                            rx.foreach(
                                RestaurantState.reviews,
                                lambda review: rx.el.div(
                                    rx.el.div(
                                        rx.el.span(
                                            review["user_name"],
                                            class_name="font-medium text-gray-900 text-sm",
                                        ),
                                        rx.el.div(
                                            rx.icon(
                                                "star",
                                                class_name="w-3 h-3 text-yellow-400 mr-1",
                                            ),
                                            rx.el.span(
                                                f"{review['rating']}",
                                                class_name="text-xs font-bold text-gray-700",
                                            ),
                                            class_name="flex items-center",
                                        ),
                                        class_name="flex items-center justify-between mb-2",
                                    ),
                                    rx.el.p(
                                        review["comment"],
                                        class_name="text-sm text-gray-600",
                                    ),
                                    class_name="p-4 bg-gray-50 rounded-lg mb-3",
                                ),
                            )
                        ),
                        class_name="bg-white p-6 rounded-xl border border-gray-200 shadow-sm col-span-1",
                    ),
                    class_name="grid grid-cols-1 lg:grid-cols-3 gap-8",
                ),
            ),
        )
    )


def orders_page() -> rx.Component:
    return layout(
        rx.el.div(
            rx.el.div(
                rx.el.h1("Orders", class_name="text-2xl font-bold text-gray-900"),
                class_name="mb-8",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.button(
                        "All",
                        on_click=lambda: OrdersState.set_status_filter("all"),
                        class_name=rx.cond(
                            OrdersState.status_filter == "all",
                            "px-4 py-2 bg-orange-100 text-orange-800 rounded-full text-sm font-medium transition-colors",
                            "px-4 py-2 bg-white border border-gray-200 text-gray-600 hover:bg-gray-50 rounded-full text-sm font-medium transition-colors",
                        ),
                    ),
                    rx.el.button(
                        "Pending",
                        on_click=lambda: OrdersState.set_status_filter("pending"),
                        class_name=rx.cond(
                            OrdersState.status_filter == "pending",
                            "px-4 py-2 bg-orange-100 text-orange-800 rounded-full text-sm font-medium transition-colors",
                            "px-4 py-2 bg-white border border-gray-200 text-gray-600 hover:bg-gray-50 rounded-full text-sm font-medium transition-colors",
                        ),
                    ),
                    rx.el.button(
                        "Delivered",
                        on_click=lambda: OrdersState.set_status_filter("delivered"),
                        class_name=rx.cond(
                            OrdersState.status_filter == "delivered",
                            "px-4 py-2 bg-orange-100 text-orange-800 rounded-full text-sm font-medium transition-colors",
                            "px-4 py-2 bg-white border border-gray-200 text-gray-600 hover:bg-gray-50 rounded-full text-sm font-medium transition-colors",
                        ),
                    ),
                    class_name="flex items-center gap-2 mb-6 overflow-x-auto pb-2",
                ),
                rx.el.div(
                    rx.el.table(
                        rx.el.thead(
                            rx.el.tr(
                                rx.el.th(
                                    "Order ID",
                                    class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                ),
                                rx.el.th(
                                    "Restaurant",
                                    class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                ),
                                rx.el.th(
                                    "Customer",
                                    class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                ),
                                rx.el.th(
                                    "Total",
                                    class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                ),
                                rx.el.th(
                                    "Status",
                                    class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                ),
                                class_name="bg-gray-50",
                            )
                        ),
                        rx.el.tbody(
                            rx.foreach(
                                OrdersState.orders,
                                lambda order: rx.el.tr(
                                    rx.el.td(
                                        order["order_id"].to(str)[:8],
                                        class_name="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900",
                                    ),
                                    rx.el.td(
                                        order["restaurant_name"],
                                        class_name="px-6 py-4 whitespace-nowrap text-sm text-gray-600",
                                    ),
                                    rx.el.td(
                                        order["customer_name"],
                                        class_name="px-6 py-4 whitespace-nowrap text-sm text-gray-600",
                                    ),
                                    rx.el.td(
                                        f"${order['total']}",
                                        class_name="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900",
                                    ),
                                    rx.el.td(
                                        rx.el.span(
                                            order["status"],
                                            class_name=f"{rx.match(order['status'], ('pending', 'bg-yellow-100 text-yellow-800'), ('delivered', 'bg-green-100 text-green-800'), ('cancelled', 'bg-red-100 text-red-800'), 'bg-gray-100 text-gray-800')} px-2.5 py-1 rounded-full text-xs font-medium capitalize",
                                        ),
                                        class_name="px-6 py-4 whitespace-nowrap",
                                    ),
                                    class_name="hover:bg-gray-50 transition-colors border-b border-gray-100 cursor-pointer",
                                    on_click=lambda: OrdersState.load_order_detail(
                                        order["order_id"]
                                    ),
                                ),
                            )
                        ),
                        class_name="min-w-full divide-y divide-gray-200",
                    ),
                    class_name="bg-white border border-gray-200 shadow-sm rounded-xl overflow-x-auto",
                ),
            ),
        )
    )


def user_role_badge(role: rx.Var[str]) -> rx.Component:
    return rx.el.span(
        role,
        class_name=f"{rx.match(role, ('customer', 'bg-gray-100 text-gray-800'), ('owner', 'bg-blue-100 text-blue-800'), ('rider', 'bg-green-100 text-green-800'), ('admin', 'bg-orange-100 text-orange-800'), 'bg-gray-100 text-gray-800')} px-2.5 py-1 rounded-full text-xs font-medium capitalize",
    )


def users_page() -> rx.Component:
    return layout(
        rx.el.div(
            rx.el.div(
                rx.el.h1("Users", class_name="text-2xl font-bold text-gray-900"),
                rx.el.span(
                    f"{UsersState.user_counts['all']} total",
                    class_name="px-2.5 py-0.5 rounded-full bg-orange-100 text-orange-800 text-sm font-medium",
                ),
                class_name="flex items-center gap-4 mb-8",
            ),
            rx.el.div(
                rx.el.div(
                    rx.foreach(
                        ["all", "customer", "owner", "rider", "admin"],
                        lambda r: rx.el.button(
                            r.capitalize(),
                            on_click=lambda: UsersState.set_role_filter(r),
                            class_name=rx.cond(
                                UsersState.role_filter == r,
                                "px-4 py-2 bg-orange-100 text-orange-800 rounded-full text-sm font-medium transition-colors capitalize",
                                "px-4 py-2 bg-white border border-gray-200 text-gray-600 hover:bg-gray-50 rounded-full text-sm font-medium transition-colors capitalize",
                            ),
                        ),
                    ),
                    class_name="flex items-center gap-2 mb-6 overflow-x-auto pb-2",
                ),
                rx.el.div(
                    rx.el.input(
                        placeholder="Search users by name or email...",
                        default_value=UsersState.search_query,
                        on_change=UsersState.set_search_query.debounce(500),
                        class_name="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 max-w-md mb-6",
                    )
                ),
                rx.el.div(
                    rx.el.table(
                        rx.el.thead(
                            rx.el.tr(
                                rx.el.th(
                                    "Name",
                                    class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                ),
                                rx.el.th(
                                    "Email",
                                    class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                ),
                                rx.el.th(
                                    "Phone",
                                    class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                ),
                                rx.el.th(
                                    "Role",
                                    class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                ),
                                rx.el.th(
                                    "Action",
                                    class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                ),
                                class_name="bg-gray-50",
                            )
                        ),
                        rx.el.tbody(
                            rx.foreach(
                                UsersState.users,
                                lambda user: rx.el.tr(
                                    rx.el.td(
                                        user["name"],
                                        class_name="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900",
                                    ),
                                    rx.el.td(
                                        user["email"],
                                        class_name="px-6 py-4 whitespace-nowrap text-sm text-gray-600",
                                    ),
                                    rx.el.td(
                                        rx.cond(
                                            user.get("phone", ""), user["phone"], "—"
                                        ),
                                        class_name="px-6 py-4 whitespace-nowrap text-sm text-gray-600",
                                    ),
                                    rx.el.td(
                                        user_role_badge(user["role"]),
                                        class_name="px-6 py-4 whitespace-nowrap",
                                    ),
                                    rx.el.td(
                                        rx.el.select(
                                            rx.el.option("Customer", value="customer"),
                                            rx.el.option("Owner", value="owner"),
                                            rx.el.option("Rider", value="rider"),
                                            rx.el.option("Admin", value="admin"),
                                            value=user["role"].to(str),
                                            on_change=lambda new_role: UsersState.update_user_role(
                                                user["user_id"].to(str), new_role
                                            ),
                                            class_name="px-3 py-1 bg-white border border-gray-300 rounded text-sm focus:outline-none focus:ring-1 focus:ring-orange-500 appearance-none",
                                        ),
                                        class_name="px-6 py-4 whitespace-nowrap",
                                    ),
                                    class_name="hover:bg-gray-50 transition-colors border-b border-gray-100",
                                ),
                            )
                        ),
                        class_name="min-w-full divide-y divide-gray-200",
                    ),
                    class_name="bg-white border border-gray-200 shadow-sm rounded-xl overflow-x-auto",
                ),
            ),
        )
    )


def riders_page() -> rx.Component:
    return layout(
        rx.el.div(
            rx.el.div(
                rx.el.h1("Riders", class_name="text-2xl font-bold text-gray-900"),
                class_name="mb-8",
            ),
            rx.el.div(
                stat_card("Total Riders", f"{RidersState.total_riders}", "bike"),
                stat_card(
                    "Active Deliveries",
                    f"{RidersState.active_deliveries.length()}",
                    "map-pin",
                ),
                stat_card(
                    "Deliveries Today",
                    f"{RidersState.total_deliveries_today}",
                    "package",
                ),
                stat_card(
                    "Total Earnings",
                    f"${RidersState.total_earnings:.2f}",
                    "dollar-sign",
                ),
                class_name="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6 mb-8",
            ),
            rx.el.div(
                rx.el.h2(
                    "Active Deliveries",
                    class_name="text-lg font-semibold text-gray-800 mb-4",
                ),
                rx.cond(
                    RidersState.active_deliveries.length() > 0,
                    rx.el.div(
                        rx.foreach(
                            RidersState.active_deliveries,
                            lambda d: rx.el.div(
                                rx.el.div(
                                    rx.el.div(
                                        rx.el.h4(
                                            d["rider_name"],
                                            class_name="text-sm font-bold text-gray-900",
                                        ),
                                        rx.el.p(
                                            f"Order: {d['order_id'].to(str)[:8]}",
                                            class_name="text-xs text-gray-500",
                                        ),
                                    ),
                                    rx.el.span(
                                        d["status"],
                                        class_name=f"{rx.match(d['status'], ('accepted', 'bg-blue-100 text-blue-800'), ('picked_up', 'bg-purple-100 text-purple-800'), ('on_the_way', 'bg-indigo-100 text-indigo-800'), 'bg-gray-100 text-gray-800')} px-2.5 py-1 rounded-full text-xs font-medium capitalize",
                                    ),
                                    class_name="flex items-start justify-between mb-3",
                                ),
                                rx.el.div(
                                    rx.icon(
                                        "store", class_name="w-4 h-4 text-gray-400 mr-2"
                                    ),
                                    rx.el.span(
                                        d["restaurant_name"],
                                        class_name="text-sm text-gray-700",
                                    ),
                                    class_name="flex items-center mb-2",
                                ),
                                rx.el.div(
                                    rx.icon(
                                        "map-pin",
                                        class_name="w-4 h-4 text-gray-400 mr-2",
                                    ),
                                    rx.el.span(
                                        d["delivery_address"],
                                        class_name="text-sm text-gray-700 truncate",
                                    ),
                                    class_name="flex items-center mb-3",
                                ),
                                rx.el.div(
                                    rx.icon(
                                        "clock", class_name="w-3 h-3 text-gray-400 mr-1"
                                    ),
                                    rx.el.span(
                                        d["time_since"],
                                        class_name="text-xs text-gray-500",
                                    ),
                                    class_name="flex items-center mt-auto",
                                ),
                                class_name="bg-white p-5 rounded-xl border border-gray-200 shadow-sm flex flex-col",
                            ),
                        ),
                        class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8",
                    ),
                    rx.el.div(
                        rx.icon(
                            "message_circle_check",
                            class_name="w-12 h-12 text-gray-300 mx-auto mb-3",
                        ),
                        rx.el.p(
                            "No active deliveries at the moment",
                            class_name="text-gray-500 font-medium text-center",
                        ),
                        class_name="bg-white py-12 rounded-xl border border-gray-200 shadow-sm flex flex-col items-center justify-center mb-8",
                    ),
                ),
            ),
            rx.el.div(
                rx.el.h2(
                    "All Riders", class_name="text-lg font-semibold text-gray-800 mb-4"
                ),
                rx.el.div(
                    rx.el.table(
                        rx.el.thead(
                            rx.el.tr(
                                rx.el.th(
                                    "Name",
                                    class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                ),
                                rx.el.th(
                                    "Contact",
                                    class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                ),
                                rx.el.th(
                                    "Vehicle",
                                    class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                ),
                                rx.el.th(
                                    "Deliveries",
                                    class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                ),
                                rx.el.th(
                                    "Earnings",
                                    class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                ),
                                rx.el.th(
                                    "Status",
                                    class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                ),
                                class_name="bg-gray-50",
                            )
                        ),
                        rx.el.tbody(
                            rx.foreach(
                                RidersState.riders,
                                lambda rider: rx.el.tr(
                                    rx.el.td(
                                        rider["name"],
                                        class_name="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900",
                                    ),
                                    rx.el.td(
                                        rx.el.div(
                                            rx.el.div(
                                                rider["email"],
                                                class_name="text-sm text-gray-900",
                                            ),
                                            rx.el.div(
                                                rx.cond(
                                                    rider.get("phone", ""),
                                                    rider["phone"],
                                                    "—",
                                                ),
                                                class_name="text-xs text-gray-500",
                                            ),
                                        ),
                                        class_name="px-6 py-4 whitespace-nowrap",
                                    ),
                                    rx.el.td(
                                        rx.cond(
                                            rider.get("vehicle_type", ""),
                                            rider["vehicle_type"],
                                            "Bicycle",
                                        ),
                                        class_name="px-6 py-4 whitespace-nowrap text-sm text-gray-600 capitalize",
                                    ),
                                    rx.el.td(
                                        f"{rider['total_deliveries']}",
                                        class_name="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-medium",
                                    ),
                                    rx.el.td(
                                        f"${rider['total_earnings']:.2f}",
                                        class_name="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-medium",
                                    ),
                                    rx.el.td(
                                        rx.cond(
                                            rider["is_online"],
                                            rx.el.span(
                                                "Active",
                                                class_name="text-xs font-medium text-green-700 bg-green-100 px-2 py-1 rounded-full",
                                            ),
                                            rx.el.span(
                                                "Offline",
                                                class_name="text-xs font-medium text-gray-600 bg-gray-100 px-2 py-1 rounded-full",
                                            ),
                                        ),
                                        class_name="px-6 py-4 whitespace-nowrap",
                                    ),
                                    class_name="hover:bg-gray-50 transition-colors border-b border-gray-100",
                                ),
                            )
                        ),
                        class_name="min-w-full divide-y divide-gray-200",
                    ),
                    class_name="bg-white border border-gray-200 shadow-sm rounded-xl overflow-x-auto",
                ),
            ),
        )
    )


def settings_page() -> rx.Component:
    return layout(
        rx.el.div(
            rx.el.div(
                rx.el.h1(
                    "Platform Settings", class_name="text-2xl font-bold text-gray-900"
                ),
                class_name="mb-8",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.h2(
                            "Configuration",
                            class_name="text-lg font-semibold text-gray-800 mb-4",
                        ),
                        rx.el.form(
                            rx.el.div(
                                rx.el.label(
                                    "Platform Commission Rate (%)",
                                    class_name="block text-sm font-medium text-gray-700 mb-1",
                                ),
                                rx.el.input(
                                    name="platform_commission_rate",
                                    type="number",
                                    step="0.1",
                                    default_value=(
                                        SettingsState.platform_settings.get(
                                            "platform_commission_rate", 0.15
                                        ).to(float)
                                        * 100
                                    ).to_string(),
                                    class_name="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-orange-500 focus:border-orange-500",
                                ),
                                class_name="mb-4",
                            ),
                            rx.el.div(
                                rx.el.label(
                                    "Base Delivery Fee ($)",
                                    class_name="block text-sm font-medium text-gray-700 mb-1",
                                ),
                                rx.el.input(
                                    name="base_delivery_fee",
                                    type="number",
                                    step="0.01",
                                    default_value=SettingsState.platform_settings.get(
                                        "base_delivery_fee", 2.99
                                    ).to_string(),
                                    class_name="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-orange-500 focus:border-orange-500",
                                ),
                                class_name="mb-6",
                            ),
                            rx.el.div(
                                rx.el.label(
                                    rx.el.input(
                                        name="is_platform_active",
                                        type="checkbox",
                                        default_checked=SettingsState.platform_settings.get(
                                            "is_platform_active", True
                                        ).to(bool),
                                        class_name="w-4 h-4 text-orange-600 border-gray-300 rounded focus:ring-orange-500 mr-2",
                                    ),
                                    "Platform Active",
                                    class_name="flex items-center text-sm font-medium text-gray-700",
                                ),
                                class_name="mb-6",
                            ),
                            rx.el.button(
                                rx.cond(
                                    SettingsState.is_saving,
                                    "Saving...",
                                    "Save Settings",
                                ),
                                type="submit",
                                disabled=SettingsState.is_saving,
                                class_name="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 font-medium text-sm transition-colors disabled:opacity-50",
                            ),
                            on_submit=SettingsState.save_settings,
                        ),
                        class_name="bg-white p-6 rounded-xl border border-gray-200 shadow-sm",
                    ),
                    class_name="col-span-1 lg:col-span-2",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.h3(
                            "System Information",
                            class_name="text-md font-semibold text-gray-800 mb-4",
                        ),
                        rx.el.div(
                            rx.el.div(
                                rx.el.span(
                                    "Database Status",
                                    class_name="text-sm text-gray-500",
                                ),
                                rx.el.div(
                                    rx.cond(
                                        SettingsState.db_status == "Connected",
                                        rx.el.span(
                                            "Connected",
                                            class_name="text-sm font-medium text-green-600 flex items-center before:content-[''] before:w-2 before:h-2 before:bg-green-500 before:rounded-full before:mr-2",
                                        ),
                                        rx.el.span(
                                            "Disconnected",
                                            class_name="text-sm font-medium text-red-600 flex items-center before:content-[''] before:w-2 before:h-2 before:bg-red-500 before:rounded-full before:mr-2",
                                        ),
                                    )
                                ),
                                class_name="flex justify-between items-center py-2 border-b border-gray-100",
                            ),
                            rx.el.div(
                                rx.el.span(
                                    "Database Name", class_name="text-sm text-gray-500"
                                ),
                                rx.el.span(
                                    SettingsState.db_name,
                                    class_name="text-sm font-medium text-gray-900",
                                ),
                                class_name="flex justify-between items-center py-2 border-b border-gray-100",
                            ),
                            rx.el.div(
                                rx.el.span(
                                    "API Status", class_name="text-sm text-gray-500"
                                ),
                                rx.el.span(
                                    SettingsState.api_status,
                                    class_name="text-sm font-medium text-green-600 flex items-center before:content-[''] before:w-2 before:h-2 before:bg-green-500 before:rounded-full before:mr-2",
                                ),
                                class_name="flex justify-between items-center py-2 border-b border-gray-100",
                            ),
                            rx.el.div(
                                rx.el.span(
                                    "API Version", class_name="text-sm text-gray-500"
                                ),
                                rx.el.span(
                                    SettingsState.api_version,
                                    class_name="text-sm font-medium text-gray-900",
                                ),
                                class_name="flex justify-between items-center py-2",
                            ),
                            class_name="flex flex-col",
                        ),
                        class_name="bg-white p-6 rounded-xl border border-gray-200 shadow-sm mb-6",
                    ),
                    rx.el.div(
                        rx.el.h3(
                            "Admin Account",
                            class_name="text-md font-semibold text-gray-800 mb-4",
                        ),
                        rx.el.div(
                            rx.el.p(
                                "Current admin info is secured. Password resets can be handled securely through email verification.",
                                class_name="text-sm text-gray-600 mb-4",
                            ),
                            rx.el.button(
                                "Change Password",
                                disabled=True,
                                class_name="px-4 py-2 border border-gray-300 text-gray-500 bg-gray-50 rounded-lg text-sm font-medium cursor-not-allowed",
                            ),
                        ),
                        class_name="bg-white p-6 rounded-xl border border-gray-200 shadow-sm",
                    ),
                    class_name="col-span-1",
                ),
                class_name="grid grid-cols-1 lg:grid-cols-3 gap-6",
            ),
        )
    )


from fastapi import FastAPI
from app.api.routes import api_router

api_app = FastAPI()
api_app.include_router(api_router)
app = rx.App(
    theme=rx.theme(appearance="light"),
    api_transformer=api_app,
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(rel="preconnect", href="https://fonts.gstatic.com", cross_origin=""),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
            rel="stylesheet",
        ),
    ],
)
app.add_page(login_page, route="/", on_load=AuthState.check_auth)
app.add_page(dashboard_page, route="/dashboard", on_load=DashboardState.load_dashboard)
app.add_page(
    restaurants_page, route="/restaurants", on_load=RestaurantState.load_restaurants
)
app.add_page(
    restaurant_detail_page,
    route="/restaurants/[restaurant_id]",
    on_load=RestaurantState.load_restaurant_detail,
)
app.add_page(orders_page, route="/orders", on_load=OrdersState.load_orders)
from app.states.api_docs_state import ApiDocsState


def endpoint_card(endpoint: dict) -> rx.Component:
    is_selected = (ApiDocsState.selected_endpoint.get("path") == endpoint["path"]) & (
        ApiDocsState.selected_endpoint.get("method") == endpoint["method"]
    )
    method_colors = {
        "GET": "bg-green-100 text-green-700 border-green-200",
        "POST": "bg-blue-100 text-blue-700 border-blue-200",
        "PATCH": "bg-amber-100 text-amber-700 border-amber-200",
        "DELETE": "bg-red-100 text-red-700 border-red-200",
    }
    method = endpoint["method"].to(str)
    method_class = rx.match(
        method,
        ("GET", method_colors["GET"]),
        ("POST", method_colors["POST"]),
        ("PATCH", method_colors["PATCH"]),
        ("DELETE", method_colors["DELETE"]),
        "bg-gray-100 text-gray-700 border-gray-200",
    )
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.span(
                    method,
                    class_name=f"{method_class} px-2 py-1 rounded text-xs font-bold border mr-3 w-16 text-center shrink-0",
                ),
                rx.el.span(
                    endpoint["path"],
                    class_name="font-mono text-sm font-semibold text-gray-800 break-all mr-3",
                ),
                rx.el.span(
                    endpoint["description"], class_name="text-sm text-gray-500 truncate"
                ),
                class_name="flex items-center flex-1",
            ),
            rx.el.div(
                rx.cond(
                    endpoint["auth_required"].to(bool),
                    rx.el.div(
                        rx.icon("lock", class_name="h-4 w-4 text-orange-500 mr-1"),
                        rx.cond(
                            endpoint["auth_role"].to(str) != "",
                            rx.el.span(
                                endpoint["auth_role"],
                                class_name="text-xs text-orange-600 font-medium capitalize",
                            ),
                            rx.el.span(
                                "Auth", class_name="text-xs text-gray-500 font-medium"
                            ),
                        ),
                        class_name="flex items-center bg-gray-50 px-2 py-1 rounded",
                    ),
                    rx.el.div(),
                ),
                class_name="flex items-center shrink-0 ml-4",
            ),
            on_click=lambda: ApiDocsState.select_endpoint(endpoint),
            class_name="flex items-center justify-between p-4 cursor-pointer hover:bg-gray-50 transition-colors",
        ),
        rx.cond(
            is_selected,
            rx.el.div(
                rx.el.div(
                    rx.cond(
                        (method == "POST") | (method == "PATCH"),
                        rx.el.div(
                            rx.el.label(
                                "Request Body (JSON)",
                                class_name="block text-xs font-semibold text-gray-700 uppercase tracking-wide mb-2",
                            ),
                            rx.el.textarea(
                                default_value=ApiDocsState.request_body,
                                on_change=ApiDocsState.set_request_body,
                                class_name="w-full h-32 font-mono text-sm p-3 bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500",
                            ),
                            class_name="mb-4",
                        ),
                        rx.el.div(),
                    ),
                    rx.el.button(
                        rx.cond(
                            ApiDocsState.is_testing,
                            rx.el.span("Sending...", class_name="flex items-center"),
                            rx.el.span("Send Request", class_name="flex items-center"),
                        ),
                        on_click=lambda: ApiDocsState.test_endpoint(
                            method, endpoint["path"].to(str), ApiDocsState.request_body
                        ),
                        disabled=ApiDocsState.is_testing,
                        class_name="px-4 py-2 bg-orange-600 hover:bg-orange-700 text-white rounded-lg text-sm font-medium transition-colors shadow-sm disabled:opacity-50",
                    ),
                    class_name="mb-6",
                ),
                rx.cond(
                    ApiDocsState.response_status > 0,
                    rx.el.div(
                        rx.el.div(
                            rx.el.span(
                                "Response",
                                class_name="text-xs font-semibold text-gray-700 uppercase tracking-wide",
                            ),
                            rx.el.span(
                                f"Status: {ApiDocsState.response_status}",
                                class_name=rx.cond(
                                    (ApiDocsState.response_status >= 200)
                                    & (ApiDocsState.response_status < 300),
                                    "text-xs font-medium bg-green-100 text-green-800 px-2 py-1 rounded",
                                    "text-xs font-medium bg-red-100 text-red-800 px-2 py-1 rounded",
                                ),
                            ),
                            class_name="flex items-center justify-between mb-2",
                        ),
                        rx.el.pre(
                            rx.el.code(
                                ApiDocsState.response_data,
                                class_name="text-sm text-gray-200 font-mono break-all whitespace-pre-wrap",
                            ),
                            class_name="bg-gray-900 p-4 rounded-lg overflow-x-auto shadow-inner max-h-96 overflow-y-auto",
                        ),
                    ),
                    rx.el.div(),
                ),
                class_name="p-6 bg-white border-t border-gray-100",
            ),
            rx.el.div(),
        ),
        class_name="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden mb-3",
    )


def api_docs_page() -> rx.Component:
    categories = [
        "Auth",
        "Restaurants",
        "Favorites",
        "Orders",
        "Payments",
        "Reviews",
        "Notifications",
        "Owner",
        "Admin",
        "Rider",
        "Utility",
    ]
    return layout(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.h1(
                        "API Documentation",
                        class_name="text-2xl font-bold text-gray-900",
                    ),
                    rx.el.p(
                        "Complete REST API reference for Qmeal platform",
                        class_name="text-gray-500 mt-1",
                    ),
                    class_name="mb-4 md:mb-0",
                ),
                rx.el.div(
                    rx.el.span(
                        "Base URL:",
                        class_name="text-xs text-gray-500 font-medium uppercase mr-2",
                    ),
                    rx.el.code(
                        rx.State.router.page.host,
                        class_name="px-2 py-1 bg-gray-100 text-gray-800 rounded font-mono text-sm",
                    ),
                    class_name="flex items-center bg-white px-4 py-2 border border-gray-200 rounded-lg shadow-sm",
                ),
                class_name="flex flex-col md:flex-row md:items-center justify-between mb-8",
            ),
            rx.el.div(
                rx.icon("key", class_name="h-5 w-5 text-gray-400 mr-3"),
                rx.el.input(
                    placeholder="Enter Bearer Token for authenticated requests...",
                    on_change=ApiDocsState.set_auth_token,
                    class_name="flex-1 bg-transparent border-none focus:ring-0 text-sm text-gray-900 placeholder-gray-400 outline-none",
                ),
                rx.cond(
                    ApiDocsState.auth_token != "",
                    rx.icon("circle_check", class_name="h-5 w-5 text-green-500 ml-3"),
                    rx.el.div(),
                ),
                class_name="flex items-center bg-white px-4 py-3 border border-gray-200 rounded-xl shadow-sm mb-8",
            ),
            rx.el.div(
                rx.foreach(
                    categories,
                    lambda cat: rx.el.button(
                        cat,
                        on_click=lambda: ApiDocsState.set_category(cat),
                        class_name=rx.cond(
                            ApiDocsState.selected_category == cat,
                            "px-4 py-2 bg-orange-500 text-white rounded-full text-sm font-medium transition-colors whitespace-nowrap shadow-sm",
                            "px-4 py-2 bg-white border border-gray-200 text-gray-600 hover:bg-gray-50 rounded-full text-sm font-medium transition-colors whitespace-nowrap shadow-sm",
                        ),
                    ),
                ),
                class_name="flex items-center gap-3 mb-8 overflow-x-auto pb-2 scrollbar-hide",
            ),
            rx.el.div(
                rx.foreach(ApiDocsState.filtered_endpoints, endpoint_card),
                class_name="flex flex-col",
            ),
            class_name="max-w-6xl mx-auto",
        )
    )


app.add_page(users_page, route="/users", on_load=UsersState.load_users)
app.add_page(riders_page, route="/riders", on_load=RidersState.load_riders)
app.add_page(settings_page, route="/settings", on_load=SettingsState.load_settings)
app.add_page(api_docs_page, route="/docs")