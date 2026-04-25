# Qmeal Food Delivery Admin Dashboard

## Design Direction
- Clean, modern dashboard aesthetic inspired by Linear/Stripe
- Orange-500 accent color (food/delivery branding)
- White sidebar with border-right on gray-50 background
- Bordered white cards with subtle shadows
- Inter font, strong typography, minimal chrome

## Phase 1: Core Layout, Authentication & Dashboard Overview ✅
- [x] Build shared layout with sidebar navigation (Dashboard, Restaurants, Orders, Users, Riders, Settings)
- [x] Build login page with email/password authentication against the API
- [x] Build main dashboard page with platform stats cards (total users, restaurants, orders, revenue)
- [x] Build state management for auth (token storage, API calls, protected routes)
- [x] Seed the database on app load if needed

## Phase 2: Restaurants & Menu Management + Orders ✅
- [x] Build restaurants list page with search, filters, and restaurant cards
- [x] Build restaurant detail page with menu items, reviews, and edit capabilities
- [x] Build orders list page with status filters, order details, and status updates

## Phase 3: Users, Riders & Admin Management ✅
- [x] Build users management page with role filters, user list, and role editing
- [x] Build riders page showing rider stats, active deliveries, and delivery history
- [x] Build admin settings page with platform configuration
- [x] Build notifications panel and profile management

## Phase 4: Expose REST API + Interactive Docs Page ✅
- [x] Mount all FastAPI API routes from server.py onto the Reflex app backend via api_transformer
- [x] Create /docs page with full interactive API documentation UI
- [x] Group endpoints by category (Auth, Restaurants, Orders, Users, Riders, Owner, Admin, Payments)
- [x] Each endpoint card shows method badge, path, description, request/response schema, and a "Try It" section
- [x] Add API docs link to sidebar navigation
