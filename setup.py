from cx_Freeze import setup, Executable

setup(
    name="WhiteRabbit",
    version="1.0",
    description="Simple GUI chatbot",
    executables=[Executable("bot.py")]
)
