
from fabric import Connection
from astrbot.api.message_components import *
from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
host = "31.56.123.4"
username = "root"

@register("fish_ssh", "案板上的鹹魚", "ssh远程服务器", "1.0")
class SetuPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    @filter.command("addssh")
    async def add_ssh(self, event: AstrMessageEvent,name: str,host: str ,password: str="Qwer3866373"):
        try:
            conn = Connection(host=host, user="root", connect_kwargs={"password": password})
            result = conn.run("ls", hide=True)  # 运行一个简单命令
            yield event.plain_result("添加并测试成功！")
            # 显示命令输出
        except Exception as e:
            yield event.plain_result("SSH 连接失败:", e)
            return
        with open("data.txt","a",encoding="utf-8") as f:
            f.write(f"{name} {host} {password}\n")
            f.close()
    @filter.command("lsssh")
    async def ls_ssh(self, event: AstrMessageEvent):
        try:
            with open("data.txt", "r", encoding="utf-8") as file:
                yield event.plain_result(file.read().rstrip("\n"))
        except Exception as e:
            yield event.plain_result("读取失败，未检测到文件")
    @filter.command("delssh")
    async def del_ssh(self, event: AstrMessageEvent,name: str):
        try:
            # 读取所有行并删除包含 "host=abc" 的行
            with open("data.txt", "r", encoding="utf-8") as file:
                lines = file.readlines()
            # 过滤掉包含 "host=abc" 的行
            i=0
            with open("data.txt", "w", encoding="utf-8") as file:
                for line in lines:
                    if not line.strip().startswith(f"{name} "):  # 确保去除前后空格再判断
                        file.write(line)
                        i+=1
            if i==len(lines):
                yield event.plain_result("删除成功")
        except Exception as e:
            yield event.plain_result("删除失败",e)
