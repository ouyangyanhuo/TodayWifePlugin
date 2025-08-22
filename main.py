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
        # 初始化插件目录路径
        self.plugin_dir = os.path.abspath(os.path.join(os.path.dirname(__file__)))

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

            # 构建cache目录路径
            cache_dir = os.path.abspath(os.path.join(self.plugin_dir, 'cache'))
            # 确保cache目录存在
            if not os.path.exists(cache_dir):
                os.makedirs(cache_dir)
            
            # 保存原始数据到文件
            cache_file = os.path.join(cache_dir, 'group_members.json')
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(group_member_list, f, ensure_ascii=False, indent=2)
            
            # 读取并整理数据
            with open(cache_file, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
            
            # 整理数据，只保留group_id、user_id和nickname，并添加编号
            processed_data = {}
            if "data" in raw_data and isinstance(raw_data["data"], list):
                for index, member in enumerate(raw_data["data"]):
                    group_id = member.get("group_id")
                    user_id = member.get("user_id")
                    nickname = member.get("nickname")
                    
                    # 确保必要字段都存在
                    if group_id is not None and user_id is not None and nickname is not None:
                        # 如果group_id不在processed_data中，初始化它
                        if group_id not in processed_data:
                            processed_data[group_id] = []
                        
                        # 添加用户信息到对应group_id下，包含编号
                        processed_data[group_id].append({
                            "index": index,
                            "user_id": user_id,
                            "nickname": nickname
                        })
            
            # 保存整理后的数据到文件（覆盖原文件）
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(processed_data, f, ensure_ascii=False, indent=2)
            
            # 找到 msg.group_id 群组中 index 最后一项
            group_id_to_find = msg.group_id
            max_index = -1
            last_member = None
            
            # 检查各种可能的键类型
            group_data = None
            if str(group_id_to_find) in processed_data:
                group_data = processed_data[str(group_id_to_find)]
            elif group_id_to_find in processed_data:
                group_data = processed_data[group_id_to_find]
            else:
                # 尝试查找所有键中是否有匹配的
                for key in processed_data.keys():
                    if str(key) == str(group_id_to_find):
                        group_data = processed_data[key]
                        break
            
            # 找到了群组数据且不为空
            if group_data and len(group_data) > 0:
                last_member = group_data[-1]
                max_index = last_member.get("index", -1)

            # 生成随机数，在 0 到 max_index 之间
            if max_index >= 0:
                random_index = random.randint(0, max_index)
                
                # 查找随机数对应的 index 的信息
                random_member = None
                for member in group_data:
                    if member.get("index") == random_index:
                        random_member = member
                        break
                
                # 如果找到了对应的成员
                if random_member:
                    # 可以在这里处理选中的成员，比如发送消息等
                    selected_nickname = random_member.get("nickname", "未知用户")
                    selected_user_id = random_member.get("user_id", "未知ID")
                    message = f"你抽到的老婆是: {selected_nickname} [CQ:image,summary=[图片],url=https://q1.qlogo.cn/g?b=qq&nk={selected_user_id}&s=100]"
                    await msg.reply(text=message)
                else:
                    print("未找到 index 对应的成员")
            else:
                print("无效的 index，无法生成随机数")
            
            # 删除 group_members.json 文件
            if os.path.exists(cache_file):
                os.remove(cache_file)
