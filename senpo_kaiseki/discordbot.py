from discord.ext import commands
from senpo_kaiseki.ocr.senpo_analyzer import SenpoAnalyzer
import os
import io
import traceback
import urllib.request
from senpo_kaiseki.code import ResultCode, SuccessCode
from senpo_kaiseki.db_client import MongoDatabaseClient


INITIAL_EXTENSIONS = [
    'senpo_kaiseki.cogs.readcog'
]


class DiscordBot(commands.Bot):

    def __init__(self, settings, errorcode, errata_list, heroname, command_prefix):
        super().__init__(command_prefix)
        self.analyzer = SenpoAnalyzer()
        self.settings = settings
        self.errorcode = errorcode
        self.errata_list = errata_list
        self.heroname = heroname

        for cog in INITIAL_EXTENSIONS:
            try:
                self.load_extension(cog)
            except Exception:
                print(traceback.format_exc())

    # 起動時に動作する処理
    async def on_ready(self):
        # 起動したらターミナルにログイン通知が表示される
        print('ログインしました')

    # メッセージ受信時に動作する処理
    async def on_message(self, message):
        # 戦法解析チャンネル以外はスルー
        if message.channel.id != 943829651653029939:
            return
        # メッセージ送信者がBotだった場合は無視する
        if message.author.bot:
            return

        if message.attachments:
            # 添付ファイルが複数の時 TODO:あとで複数ファイル対応にする
            if len(message.attachments) > 1:
                await message.channel.send('ファイルは一つずつ送信してください')
                return
            file = message.attachments[0]
            filename = file.filename
            split_name = os.path.splitext(filename)
            # 添付ファイルがpng以外の時
            if split_name[1] not in [".png", ".PNG"]:
                await message.channel.send('対応しているファイル形式はpngファイルのみです')
                return
            await message.channel.send('【戦報解析Bot】PNGファイル解析中・・・【しばらくお待ちください】')

            # ファイルをダウンロードしてメモリ上に保存
            try:
                img_stream = None
                user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'
                headers = {'User-Agent': user_agent}
                req = urllib.request.Request(file.url, None, headers)
                with urllib.request.urlopen(req)as response:
                    img_stream = io.BytesIO(response.read())
                result = self.analyzer.analyze(img_stream, self.settings)
                if 'error_code' in result:
                    await message.channel.send(self.errorcode[result['error_code']]['message'])
                else:

                    for k in result.keys():
                        result[k] = self._correct_name(result[k])

                    # 武将名定義処理
                    result[ResultCode.BUSYO_1] = self._get_hero_name(result[ResultCode.SENPO_1_1.name])
                    result[ResultCode.BUSYO_2] = self._get_hero_name(result[ResultCode.SENPO_2_1.name])
                    result[ResultCode.BUSYO_3] = self._get_hero_name(result[ResultCode.SENPO_3_1.name])
                    result[ResultCode.E_BUSYO_1] = self._get_hero_name(result[ResultCode.E_SENPO_1_1.name])
                    result[ResultCode.E_BUSYO_2] = self._get_hero_name(result[ResultCode.E_SENPO_2_1.name])
                    result[ResultCode.E_BUSYO_3] = self._get_hero_name(result[ResultCode.E_SENPO_3_1.name])

                    db_client = MongoDatabaseClient()
                    success_friend, success_enemy = db_client.insert_data(result)
                    if success_friend == SuccessCode.FAILED:
                        await message.channel.send("★味方ユーザのデータ読み取りが失敗しました。")
                    else:
                        if success_friend == SuccessCode.INSERT:
                            await message.channel.send("★以下の内容でデータベース登録が成功しました")
                        if success_friend == SuccessCode.UPDATE:
                            await message.channel.send("★以下の内容でデータベース更新が成功しました")
                        await message.channel.send("味方ユーザ：" + result[ResultCode.USER_NAME.name])
                        await message.channel.send("味方主将：" + result[ResultCode.BUSYO_1] + " Lv:" + result[ResultCode.LEVEL_1.name] +
                                                   "\n味方副将1：" + result[ResultCode.BUSYO_2] + " Lv:" + result[ResultCode.LEVEL_2.name] +
                                                   "\n味方副将2：" + result[ResultCode.BUSYO_3] + " Lv:" + result[ResultCode.LEVEL_3.name])
                        await message.channel.send("味方主将戦法1：" + result[ResultCode.SENPO_1_2.name] +
                                                   "\n味方主将戦法2：" + result[ResultCode.SENPO_1_3.name])
                        await message.channel.send("味方副将1戦法1：" + result[ResultCode.SENPO_2_2.name] +
                                                   "\n味方副将1戦法2：" + result[ResultCode.SENPO_2_3.name])
                        await message.channel.send("味方副将2戦法1：" + result[ResultCode.SENPO_3_2.name] +
                                                   "\n味方副将2戦法2：" + result[ResultCode.SENPO_3_3.name])
                    if success_enemy == SuccessCode.FAILED:
                        await message.channel.send("★敵ユーザのデータ読み取りが失敗しました。")
                    else:
                        if success_enemy == SuccessCode.INSERT:
                            await message.channel.send("★以下の内容でデータベース登録が成功しました")
                        if success_enemy == SuccessCode.UPDATE:
                            await message.channel.send("★以下の内容でデータベース更新が成功しました")
                        await message.channel.send("敵ユーザ：" + result[ResultCode.E_USER_NAME.name] +
                                                   "\n敵同盟：" + result[ResultCode.E_ALLIANCE_NAME.name])
                        await message.channel.send("敵主将：" + result[ResultCode.E_BUSYO_1] + " Lv:" + result[ResultCode.E_LEVEL_1.name] +
                                                   "\n敵副将1：" + result[ResultCode.E_BUSYO_2] + " Lv:" + result[ResultCode.E_LEVEL_2.name] +
                                                   "\n敵副将2：" + result[ResultCode.E_BUSYO_3] + " Lv:" + result[ResultCode.E_LEVEL_3.name])
                        await message.channel.send("敵主将戦法1：" + result[ResultCode.E_SENPO_1_2.name] +
                                                   "\n敵主将戦法2：" + result[ResultCode.E_SENPO_1_3.name])
                        await message.channel.send("敵副将1戦法1：" + result[ResultCode.E_SENPO_2_2.name] +
                                                   "\n敵副将1戦法2：" + result[ResultCode.E_SENPO_2_3.name])
                        await message.channel.send("敵副将2戦法1：：" + result[ResultCode.E_SENPO_3_2.name] +
                                                   "\n敵副将2戦法2：" + result[ResultCode.E_SENPO_3_3.name])

            except Exception as e:
                await message.channel.send('サーバ内部エラー：しばらくおまちください。')
                print(traceback.format_exc())
                print(e)

        await self.process_commands(message)

    def _correct_name(self, name):
        if name == '※読取失敗※':
            return ""
        elif name not in self.errata_list:
            return name
        else:
            return self.errata_list[name]

    def _get_hero_name(self, senpo):
        if senpo == '':
            return '不明武将'
        elif senpo not in self.heroname:
            return '未定義武将'
        else:
            return self.heroname[senpo]
