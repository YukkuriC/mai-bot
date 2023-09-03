from src import inject_cmdbot as nonebot

nonebot.inject()
nonebot.load_plugins("src/plugins")

if __name__ == "__main__":
    nonebot.run()