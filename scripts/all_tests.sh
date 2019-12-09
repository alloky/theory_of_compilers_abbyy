./tests/test_lexer.py
./tests/test_dotlib.py
coverage run --branch --omit 'venv/*' ./tests/test_parser.py && coverage html && coverage report
