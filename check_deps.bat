@echo off
chcp 65001 >nul
echo Checking hermes-agent dependencies...
echo.
cd /d "%~dp0.."

python -c "import hermes_constants; print('hermes_constants:', hermes_constants.__file__)"
python -c "import run_agent; print('run_agent:', run_agent.__file__); print('AIAgent:', run_agent.AIAgent)"
python -c "from agent.agent_init import init_agent; print('agent_init OK')"
python -c "from agent.conversation_loop import run_conversation; print('conversation_loop OK')"
python -c "import hermes_state; print('hermes_state OK')"
python -c "import toolsets; print('toolsets OK')"
python -c "import providers; print('providers OK')"
echo.
echo Dependencies check:
python -c "import openai; print('openai:', openai.__version__)"
python -c "import httpx; print('httpx:', httpx.__version__)"
python -c "import yaml; print('pyyaml OK')"
python -c "import rich; print('rich OK')"
python -c "import jinja2; print('jinja2 OK')"
python -c "import pydantic; print('pydantic:', pydantic.__version__)"
python -c "import tenacity; print('tenacity OK')"
python -c "import dotenv; print('python-dotenv OK')"
python -c "import certifi; print('certifi OK')"
python -c "import requests; print('requests OK')"
echo.
echo Check complete.
pause
