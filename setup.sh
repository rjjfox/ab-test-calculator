mkdir -p ~/.streamlit/
echo "[general]
email = \"ryanfox212@gmail.com\"
" > ~/.streamlit/credentials.toml
echo "[server]
headless = true
port = process.env.PORT
enableCORS = false
" > ~/.streamlit/config.toml