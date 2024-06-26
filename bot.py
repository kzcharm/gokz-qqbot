import nonebot
from nonebot.adapters.onebot.v11 import Adapter as OnebotAdapter  # 避免重复命名

# 初始化 NoneBot
nonebot.init()

# 注册适配器
driver = nonebot.get_driver()
driver.register_adapter(OnebotAdapter)

# 在这里加载插件
nonebot.load_builtin_plugins("echo")
# nonebot.load_plugins("src/plugins")
nonebot.load_from_toml("pyproject.toml")

if __name__ == "__main__":
    nonebot.run()
    