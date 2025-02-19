from fabric import Connection
import os
import re
import shutil
import aiohttp  # 导入 aiohttp 用于发送 HTTP 请求
from datetime import datetime
from astrbot.api.event.filter import *
from astrbot.api.event import AstrMessageEvent, MessageEventResult
from astrbot.api.all import *  # 导入所有API
import time

@register("fish_ssh", "案板上的鹹魚", "ssh远程服务器", "1.0")

class SetuPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.all_host=[]
        self.update_host()
        self.now_ssh={}
        self.open=False
        self.conn=None
    @permission_type(PermissionType.ADMIN)  # 仅限管理员使用
    @command("addssh")
    async def add_ssh(self, event: AstrMessageEvent,name: str,host: str ,password: str="Qwer3866373"):
        try:
            conn = Connection(host=host, user="root", connect_kwargs={"password": password})
            result = conn.run("ls", hide=True)  # 运行一个简单命令
            yield event.plain_result("添加并测试成功！")
            self.update_host()
            # 显示命令输出
        except Exception as e:
            yield event.plain_result("SSH 连接失败:", e)
            return
        with open("data.txt","a",encoding="utf-8") as f:
            f.write(f"{name} {host} {password}\n")
            f.close()

    @permission_type(PermissionType.ADMIN)  # 仅限管理员使用
    @command("lsssh")

    async def ls_ssh(self, event: AstrMessageEvent):
        try:
            with open("data.txt", "r", encoding="utf-8") as file:
                yield event.plain_result(file.read().rstrip("\n"))
        except Exception as e:
            yield event.plain_result("读取失败，未检测到文件")

    @permission_type(PermissionType.ADMIN)  # 仅限管理员使用
    @command("delssh")
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
            if i==len(lines)-1:
                yield event.plain_result("删除成功")
                self.update_host()
            else:
                yield event.plain_result("删除失败，无此名称的ssh连接")
        except Exception as e:
            yield event.plain_result("删除失败",e)

    @permission_type(PermissionType.ADMIN)  # 仅限管理员使用
    @command("ssh")
    async  def my_ssh(self, event: AstrMessageEvent,name: str):
        for item in self.all_host:
            if item.get("name") == name:
                try:
                    self.conn = Connection(host=item.get("host"), user="root", connect_kwargs={"password": item.get('password')})
                    yield event.plain_result("成功连接")
                    self.now_ssh["name"] = item.get("name")
                    self.now_ssh["host"] = item.get("host")
                    self.now_ssh["password"] = item.get('password')
                    self.open=True
                    while self.open:
                        time.sleep(10)
                except Exception as e:
                    yield event.plain_result("连接失败",e)
                break
    @permission_type(PermissionType.ADMIN)  # 仅限管理员使用
    @command("cmd")
    async def cmd(self, event: AstrMessageEvent, com: str):
        try:
            com=re.sub(r"^\[|\]$", "", com)
            result = self.conn.run(com, hide=True)
            yield event.plain_result(result.stdout.rstrip("\n"))
        except Exception as e:
            yield event.plain_result("执行命令失败",e)
    def update_host(self):
        new_host=[]
        with open("data.txt", "r", encoding="utf-8") as file:
            for line in file:
                name,host,password = line.strip().split(" ")
                d={"name":name, "host":host, "password":password }
                new_host.append(d)
        self.all_host=new_host