# インストールした discord.py を読み込む
from discord.ext import commands
from senpo_kaiseki.ocr.senpo_analyzer import SenpoAnalyzer
import os
import io
import traceback
import urllib.request


class discordbot(commands.Bot):

    def __init__(self, settings, errorcode, **options):
        super().__init__(**options)
        self.analyzer = SenpoAnalyzer()
        self.settings = settings
        self.errorcode = errorcode

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
        # 「/neko」と発言したら「にゃーん」が返る処理
        if message.content == '/neko':
            await message.channel.send('にゃーん')

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
                    await message.channel.send("勝敗：" + result['win_result'] +
                                               "\n味方ユーザ：" + result['user_result'] +
                                               "\n敵ユーザ：" + result['e_user_result'] +
                                               "\n敵同盟：" + result['e_alliance'])
                    await message.channel.send("味方主将Lv：" + result['level1'] +
                                               "\n味方副将1Lv：" + result['level2'] +
                                               "\n味方副将2Lv：" + result['level3'])
                    await message.channel.send("敵主将Lv：" + result['e_level1'] +
                                               "\n敵副将1Lv：" + result['e_level2'] +
                                               "\n敵副将2Lv：" + result['e_level3'])
                    await message.channel.send("味方主将戦法1：" + result['senpo_1_1'] +
                                               "\n味方主将戦法2：：" + result['senpo_1_2'] +
                                               "\n味方主将戦法3：：" + result['senpo_1_3'])
                    await message.channel.send("味方副将1戦法1：" + result['senpo_2_1'] +
                                               "\n味方副将1戦法2：：" + result['senpo_2_2'] +
                                               "\n味方副将1戦法3：：" + result['senpo_2_3'])
                    await message.channel.send("味方副将2戦法1：" + result['senpo_3_1'] +
                                               "\n味方副将2戦法2：：" + result['senpo_3_2'] +
                                               "\n味方副将2戦法3：：" + result['senpo_3_3'])
                    await message.channel.send("敵主将戦法1：" + result['e_senpo_1_1'] +
                                               "\n敵主将戦法2：：" + result['e_senpo_1_2'] +
                                               "\n敵主将戦法3：：" + result['e_senpo_1_3'])
                    await message.channel.send("敵副将1戦法1：" + result['e_senpo_2_1'] +
                                               "\n敵副将1戦法2：：" + result['e_senpo_2_2'] +
                                               "\n敵副将1戦法3：：" + result['e_senpo_2_3'])
                    await message.channel.send("敵副将2戦法1：" + result['e_senpo_3_1'] +
                                               "\n敵副将2戦法2：：" + result['e_senpo_3_2'] +
                                               "\n敵副将2戦法3：：" + result['e_senpo_3_3'])

            except Exception as e:
                print(traceback.format_exc())
                print(e)
