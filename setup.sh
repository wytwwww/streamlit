mkdir -p ~/.streamlit2/

echo "\
[general]\n\
email = \"318866428@qq.com\"\n\
" > ~/.streamlit/credentials.toml

echo "\
[server]\n\
headless = true\n\
enableCORS = false\n\
port = 10000\n\
" > ~/.streamlit/config.toml