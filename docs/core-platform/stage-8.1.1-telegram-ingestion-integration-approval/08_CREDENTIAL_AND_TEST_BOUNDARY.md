# Credential and Fake-Network Test Boundary

No production Telegram token, network, deployment, database change, or config
change is required or authorized. Tests must use fake Update, Message, Telegram
context/bot, and controlled async file/download doubles. Real Telegram API use
is **NOT AUTHORIZED / NOT REQUIRED**.

Baseline inspection proves module import currently raises when
`TELEGRAM_BOT_TOKEN` is absent. The sole authorized testability adjustment is
within `core/adapters/telegram/main.py`: defer the existing non-empty token
validation from module import to production startup in `main()`, before
`Application.builder().token(...).build()`.

Production startup must still fail explicitly when the token is absent. There
must be no silent/default token, no credential committed, no weakened startup
validation, and no production config edit. Polling behavior after successful
validation is unchanged.
