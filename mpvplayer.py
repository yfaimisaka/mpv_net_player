#!/usr/bin/env python
#!/etc/profiles/per-user/aimi/bin/python
# coding=utf-8


import os
import sys
import getopt
import re
from typing import Any, final
    
debug = False

"""
MpvBilibili
use you-get to play bilibili vedio by mpv
truly is mpv <vedio_url> <audio_url>
"""
class MpvVedio():
    def __init__(self, kargs):
        # attributes that is a must or choosable one
        self.debug = kargs.get("debug")
        self.is_playlist = kargs.get("is_playlist")
        self.no_cache = kargs.get("no_cache")
        # episode defaults to 1 if not set by hand
        self.episode = kargs.get("episode") or 1
        self.cookie_file = kargs.get("cookie_file")
        self.proxy = kargs.get("proxy")
        self.raw_url = kargs.get("raw_url")
        self.data_file = kargs.get("data_file")

        self.file_exist = kargs.get("file_exist")

        self.use_file = kargs.get("use_file")

    def write_urls(self):
        self.raw_url = self.raw_url.strip('/')
                            
        # if paly failed, then re-generate data_file
        # use cookie and check if type is 'playlist'
        # TODO: remove cookie hardcode(-c xxx), instead, as a parm
        cmd_you_get = './you-get/you-get -u'
        if self.is_playlist:
            cmd_you_get += ' -l '
        if self.debug:
            cmd_you_get += ' --debug '
        if self.cookie_file:
            cmd_you_get += ' -c %s ' % (self.cookie_file)
        if self.proxy:
            # proxy for you-get extractor
            cmd_you_get += ' -y %s ' % (self.proxy)
            # proxy for you-get http download
            # cmd_you_get += ' -x %s ' % (proxy)

        # DEBUG
        # cmd_you_get += self.raw_url
        # print("++++++++++++++++++++++++++START++++++++++++++++++++")
        # os.system(cmd_you_get)
        # print("++++++++++++++++++++++++++END++++++++++++++++++++++")

        cmd_you_get += self.raw_url + ' > ' + self.data_file
        print("[DEBUG]===========get-urls::", cmd_you_get, "==============")
        res = os.system(cmd_you_get)
        if not res:
            raise Exception("[ERROR]: Fail to write vedio and audio url to file [%s]" % (self.data_file))



    # get command string for mpv
    def cmd_str(self, vedio_url: str, audio_url: str) -> str:
        # mpv "{vedio_url}" --audio-file "{audio_url}" --referrer "{referrer}" --no-ytdl
        cmd = 'mpv ' + '"'
        cmd += vedio_url + '"' + ' --audio-file='+ '"' + audio_url + '"' + " --no-ytdl"
        print("[DEBUG]==========cmd::", cmd, "===============")
        return cmd 


    # TODO: download subtitle from video website
    def get_subtile():
        pass

    def get_cmd(self) -> str:
        # get website's address
        with open(self.data_file, 'r', encoding='utf-8') as data:
            url_list = [] # video and audio url
            for x in data.readlines():
                x = x.strip("[]\'")
                if len(x) > 8 and x[:8] == 'https://' or x[:7] == 'http://':
                    url_list.append(x.strip())
        
        if len(url_list) < 1:
            print("[WARN]=========data_file %s is empty or not valid!=================" % (self.data_file))
            return ""

        vedio_url = url_list[2 * self.episode - 2]
        audio_url = url_list[2 * self.episode - 1]
        return self.cmd_str(vedio_url, audio_url)

    # episode defaults is 1, means single vedio
    # if type is 'playlist', then input a episode number
    def play(self):
        # TODO: not use referrer hardcode

        # if urls cache hint and use this cache
        if self.file_exist and not self.no_cache:
            cmd = self.get_cmd()
            # FIXME: if use --use option and failed to play vedio, will cause self.write_urls
            # which need a raw_url arg --use don't have
            # if use -u or --use option to use cache file
            # do not try again?
            if os.system(cmd) != 0 and not self.use_file:
                print("[ERROR]=================FAIL, will try again==============")
                self.write_urls() 
                cmd = self.get_cmd()
                os.system(cmd)
        # no_cache is set to True or file not exist
        else:
            self.write_urls() 
            cmd = self.get_cmd()
            if os.system(cmd) != 0:
                raise Exception("[ERROR]=================MPV Bilibili FAILED=============")

    def run(self):
        self.play()


class MpvBilibili(MpvVedio):
    def __init__(self, kargs: dict[str, Any]):
        super().__init__(kargs)
        self.referrer = "https://www.bilibili.com"

    # get command string for mpv
    def cmd_str(self, vedio_url: str, audio_url: str) -> str:
        # mpv "{vedio_url}" --audio-file "{audio_url}" --referrer "{referrer}" --no-ytdl
        cmd = 'mpv ' 
        if self.proxy:
            cmd += "--http-proxy=" + "http://" + self.proxy + " " 
        cmd += '"' + vedio_url + '"' + ' --audio-file='+ '"' + audio_url + '"' + ' --referrer="{}"'.format(self.referrer) + " --no-ytdl"
        print("[DEBUG]==========cmd::", cmd, "===============")
        return cmd 

    def run(self):
        super().run()

# TODO: use argparse to rewrite parse
def parse(vedio_args: dict[str, Any]):
    argv = sys.argv[1:]
    # read input options
    try:
        opts, args = getopt.getopt(argv, "lfhe:d:o:c:p:u:t:", ["playlist", "episode", "output", "help", "cookie", "proxy", "debug", "use_file", "no_cache", "target"])
    except getopt.GetoptError as error:
        help()
        raise error

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            help()
        elif opt in ("-l", "--playlist"):
            vedio_args["is_playlist"] = True
        elif opt in ("-e", "--episode"):
            vedio_args["episode"] = int(arg)
        elif opt in ("-o", "--output"):
            # FIXME: maybe data_file is not in current diretory
            # so hardcode '.' is not compatible
            vedio_args["data_file"] = os.path.join('.', arg)
        elif opt in ("-c", "--cookie"):
            vedio_args["cookie_file"] = arg
        elif opt in ("-p", "--proxy"):
            vedio_args["proxy"] = arg
        elif opt in ("-d", "--debug"):
            vedio_args["debug"] = True
        elif opt in ("-f", "--no_cache"):
            vedio_args["no_cache"] = True
        elif opt in ("-t", "--target"):
            vedio_args["target"] = arg
        elif opt in ("-u", "--use"):
            vedio_args["use_file"] = file = os.path.join('.', arg)
            if not os.path.exists(file) or not os.stat(file).st_size:
                raise Exception("[ERROR]: File [%s] not exist or is empty" % (file))
            vedio_args["file_exist"] = True
            vedio_args["data_file"] = file

    # some arguments must appear the same time
    if not (type(vedio_args.get("target")) == type(vedio_args.get("use_file"))):
        raise Exception('-t or --target param must use with -u or --use param')

    
    # need raw_url if not directly use file (-u or --use argument)
    if not vedio_args.get("use_file"):
        vedio_args["raw_url"] = args[0]

        # some args can not be empty
        data_file = vedio_args.get("data_file")
        if not data_file:
            raise Exception("output can not be empty, use -o <output_file> to set it")

        # create data_file if not exist
        if not os.path.exists(data_file):
            os.mknod(data_file)
        # check if file is empty
        elif os.stat(data_file).st_size != 0:
            vedio_args["file_exist"] = True

# TODO: complete help message
def help():
    print('''
        Usage:
           ./mpvplayer.py [-l] [-e|--episode] <episode> -o|--output <file> <url>,
           -l, --playlist      if this url has a playlist,
    ''')


# TODO: use a multiplexer to switch vedio
# to specific class
def multiplexer(target: str, args: dict[str, Any]) -> MpvVedio:
    if re.match(r'https?://(www\.)?bilibili\.com/.+', target):
        bilibili = MpvBilibili(args)
        bilibili.referrer = "https://bilibili.com"
        return bilibili
    else:
        print("TO BE COMPLETE!")

    if target == "bilibili":
        bilibili = MpvBilibili(args)
        bilibili.referrer = "https://bilibili.com"
        return bilibili


if __name__ == '__main__':
    vedio_args = {}
    parse(vedio_args)

    vedio_player = multiplexer(vedio_args.get("raw_url") or vedio_args.get("target"), vedio_args)
    vedio_player.run()
