from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("create-standalone/", views.create_standalone, name="create-standalone"),
    path(
        "standalone-account/<str:address>/",
        views.standalone_account,
        name="standalone-account",
    ),
    path("initial-funds/<str:receiver>/", views.initial_funds, name="initial-funds"),
    path("transfer-funds/<str:sender>/", views.transfer_funds, name="transfer-funds"),
    path("wallets/", views.wallets, name="wallets"),
    path("create-wallet/", views.create_wallet, name="create-wallet"),
    path("wallet/<str:wallet_id>/", views.wallet, name="wallet"),
    path(
        "create-wallet-account/<str:wallet_id>/",
        views.create_wallet_account,
        name="create-wallet-account",
    ),
    path(
        "wallet-account/<str:wallet_id>/<str:address>/",
        views.wallet_account,
        name="wallet-account",
    ),
    path("assets/", views.assets, name="assets"),
    path("create-asset/", views.create_asset, name="create-asset"),
    path("search/", views.search, name="search"),
]
