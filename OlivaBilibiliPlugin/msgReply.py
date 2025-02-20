'''
 ██████╗ ██╗     ██╗██╗   ██╗ █████╗ ██████╗ ██╗██╗     ██╗
██╔═══██╗██║     ██║██║   ██║██╔══██╗██╔══██╗██║██║     ██║
██║   ██║██║     ██║██║   ██║███████║██████╔╝██║██║     ██║
██║   ██║██║     ██║╚██╗ ██╔╝██╔══██║██╔══██╗██║██║     ██║
╚██████╔╝███████╗██║ ╚████╔╝ ██║  ██║██████╔╝██║███████╗██║
 ╚═════╝ ╚══════╝╚═╝  ╚═══╝  ╚═╝  ╚═╝╚═════╝ ╚═╝╚══════╝╚═╝
@File      :   OlivaBilibiliPlugin/msgReply.py
@Author    :   Fishroud鱼仙
@Contact   :   fishroud@qq.com
@Desc      :   None
'''
import OlivOS
import OlivaBilibiliPlugin

import os
import re
import json
import requests
from xml.dom.minidom import parseString
import datetime

def unity_reply(plugin_event, Proc):


    command_list = deleteBlank(plugin_event.data.message)
    image_path = os.path.abspath(OlivaBilibiliPlugin.data.save_path).replace('\\','\\\\')
    matchJson = re.search(r'\[OP:json,data=(.*)\]', plugin_event.data.message)
    matchXml = re.search(r'&#91;OP:xml,data=(.*)&#93;', plugin_event.data.message)
    if matchJson:
        opjson = json.loads(matchJson.group(1).replace('&#44;',','))
        url = opjson['meta']['detail_1']['qqdocurl']
        if url:
            url = OlivaBilibiliPlugin.bilibili.URL(url)
            if url.netloc == 'b23.tv':
                html = url.getHtml().replace('\n','')
                matchbv = matchBV(html)
                if matchbv:
                    bvid = matchbv.group(1)
                    video = OlivaBilibiliPlugin.bilibili.VIDEO(bvid)
                    video.getVideoDataFromApi()
                    response = video.getVideoInfo()
                    if response != '视频查询失败':
                        plugin_event.reply(response)
            del url
    if matchXml:
        xml = parseString(matchXml.group(1))
        collection = xml.documentElement
        if collection.hasAttribute('url'):
            url = OlivaBilibiliPlugin.bilibili.URL(collection.getAttribute('url'))
            if url.netloc == 'b23.tv':
                html = url.getHtml().replace('\n','')
                matchbv = matchBV(html)
                if matchbv:
                    bvid = matchbv.group(1)
                    video = OlivaBilibiliPlugin.bilibili.VIDEO(bvid)
                    video.getVideoDataFromApi()
                    response = video.getVideoInfo()
                    if response != '视频查询失败':
                        plugin_event.reply(response)
            del url
    if len(command_list) == 1:
        matchbv = matchBV(command_list[0])
        matchurl = matchUrl(command_list[0])
        if command_list[0].lower() == '/bilibili':
            plugin_event.reply('OlivaBilibiliPlugin by Fishroud')
        elif matchbv:
            bvid = matchbv.group(1)
            video = OlivaBilibiliPlugin.bilibili.VIDEO(bvid)
            video.getVideoDataFromApi()
            response = video.getVideoInfo()
            if response != '视频查询失败':
                plugin_event.reply(response)
        elif matchurl:
            url = OlivaBilibiliPlugin.bilibili.URL(matchurl.group(0))
            if url.netloc == 'live.bilibili.com':
                if url.path_list[0].isdigit():
                    biliUser = OlivaBilibiliPlugin.bilibili.BILIUSER()
                    biliUser.getUserDatabyRoomId(int(url.path_list[0]))
                    biliUser.getUserDatafromApi()
                    response = biliUser.getLiveInfo()
                    if response != '用户不存在':
                        #save_path = image_path + '\\' + str(biliUser.mid) + '.PNG'
                        #cqcode = '[OP:image,file=file:///' + save_path + ']'
                        plugin_event.reply('发现了bilibili直播房间链接！\n' + response)
                        del url,biliUser
            elif url.netloc == 'space.bilibili.com':
                if url.path_list[0].isdigit():
                    biliUser = OlivaBilibiliPlugin.bilibili.BILIUSER(int(url.path_list[0]))
                    response = biliUser.getUserInfo()
                    if response != '用户不存在':
                        save_path = image_path + '\\' + str(biliUser.mid) + '.PNG'
                        cqcode = '[OP:image,file=file:///' + save_path + ']'
                        plugin_event.reply(response + cqcode)
                        del url,biliUser
            elif url.netloc == 'b23.tv':
                html = url.getHtml().replace('\n','')
                matchbv = matchBV(html)
                if matchbv:
                    bvid = matchbv.group(1)
                    video = OlivaBilibiliPlugin.bilibili.VIDEO(bvid)
                    video.getVideoDataFromApi()
                    response = video.getVideoInfo()
                    if response != '视频查询失败':
                        plugin_event.reply(response)
    if len(command_list) == 2:
        if command_list[0].lower() == '/search':
            response = OlivaBilibiliPlugin.bilibili.searchUserByName(command_list[1])
            plugin_event.reply(response)
        if command_list[1].lower() == "/today" :
            api='https://bangumi.bilibili.com/web_api/timeline_global'
            response = requests.request("GET", api)
            i = datetime.datetime.now()
            todayjson = json.loads(response.text)
            if todayjson["code"]==0:
                result=todayjson["result"]
                today=str(i.month)+'-'+str(i.day)
                for q in result:
                    if today==q["date"]:
                        seasons=q["seasons"]
                        reply=""
                        for z in seasons:
                            reply=reply+"'{title}'在{time}更新了{pub_index}\n".format(title=z["title"],time=z["pub_time"],pub_index=z["pub_index"])
                        plugin_event.reply(reply)
    if len(command_list) == 3:
        if command_list[0].lower() == '/up':
          #command_list[2].isdigit():
            if command_list[1].lower() == '--uid' or command_list[1].lower() == '-u':
                if command_list[2].isdigit():
                    biliUser = OlivaBilibiliPlugin.bilibili.BILIUSER(int(command_list[2]))
                    save_path = image_path + '\\' + str(biliUser.mid) + '.PNG'
                    cqcode = '[OP:image,file=file:///' + save_path + ']'
                    plugin_event.reply(biliUser.getUserInfo() + cqcode)
                else:
                    plugin_event.reply('[--uid]的参数非法')
            elif command_list[1].lower() == '--roomid' or command_list[1].lower() == '-r':
                if command_list[2].isdigit():
                    biliUser = OlivaBilibiliPlugin.bilibili.BILIUSER()
                    biliUser.getUserDatabyRoomId(int(command_list[2]))
                    biliUser.getUserDatafromApi()
                    save_path = image_path + '\\' + str(biliUser.mid) + '.PNG'
                    cqcode = '[OP:image,file=file:///' + save_path + ']'
                    plugin_event.reply(biliUser.getUserInfo() + cqcode)
                else:
                    plugin_event.reply('[--roomid]的参数非法')
        elif command_list[0].lower() == '/video':
            if len(command_list) == 3:  #command_list[2].isdigit():
                if command_list[1].lower() == '--aid' or command_list[1].lower() == '-a':
                    if command_list[2].isdigit():
                        video = OlivaBilibiliPlugin.bilibili.VIDEO(0 ,int(command_list[2]))
                        video.getVideoDataFromApi('aid')
                        plugin_event.reply(video.getVideoInfo())
                    else:
                        plugin_event.reply('[--aid]的参数非法')
                elif command_list[1].lower() == '--bvid' or command_list[1].lower() == '-b':
                    video = OlivaBilibiliPlugin.bilibili.VIDEO(command_list[2])
                    video.getVideoDataFromApi()
                    plugin_event.reply(video.getVideoInfo())

def deleteBlank(str):
    str_list = list(filter(None,str.split(' ')))
    return str_list

def matchBV(str):
    matchbv = re.match( r'^.*BV(\S{10}).*$', str, re.I)
    return matchbv

def matchUrl(str):
    matchurl = re.match( r'(https?|ftp|file)://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]', str)
    return matchurl