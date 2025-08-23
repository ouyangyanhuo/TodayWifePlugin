from ncatbot.plugin import BasePlugin, CompatibleEnrollment
from ncatbot.core import BaseMessage, GroupMessage
import os,json,random

bot = CompatibleEnrollment  # 兼容回调函数注册器

class TodayWife(BasePlugin):
    name = "TodayWife" # 插件名
    version = "1.0.0" # 插件版本

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.commands = []

    async def on_load(self):
        # 指令列表（本插件内将不会被注册）
        self.commands = [
            {
                "name": "Today's Wife",
                "prefix": "#今日老婆",
                "handler": self.today_wife,
                "description": "为你在群里面找一个老婆",
                "examples": ["#今日老婆"]
            }
        ]

    @bot.group_event()
    async def today_wife(self, msg: GroupMessage):
        if msg.raw_message == "#今日老婆":
            # 获取群成员列表
            group_member_list = await self.api.get_group_member_list(group_id=msg.group_id)
            
            # 直接处理数据，无需文件读写
            members = []
            if "data" in group_member_list and isinstance(group_member_list["data"], list):
                for member in group_member_list["data"]:
                    user_id = member.get("user_id")
                    nickname = member.get("nickname")
                    
                    # 确保必要字段都存在
                    if user_id is not None and nickname is not None:
                        members.append({
                            "user_id": user_id,
                            "nickname": nickname
                        })
            
            # 检查是否有成员数据
            if not members:
                await msg.reply(text="群组中没有成员信息")
                return
            
            # 随机选择一个成员
            selected_member = random.choice(members)
            selected_nickname = selected_member.get("nickname", "未知用户")
            selected_user_id = selected_member.get("user_id", "未知ID")
            
            # 发送结果
            message = f"你抽到的老婆是: {selected_nickname} [CQ:image,summary=[图片],url=https://q1.qlogo.cn/g?b=qq&nk={selected_user_id}&s=100]"
            await msg.reply(text=message)
