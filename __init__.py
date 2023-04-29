import requests, time, json
from pbf.controller import Cache
from pbf.controller.PBF import PBF
from pbf.utils.RegCmd import RegCmd

_name = "关键词系统"
_version = "1.0.1"
_description = "智能关键词回复。支持“徐氏正则”"
_author = "xzyStudio"
_cost = 0.00

class keyword(PBF):
    @RegCmd(
        name = "关键词审查列表",
        usage = "关键词审查列表",
        permission = "owner",
        description = "查看关键词审查列表",
        mode = "关  键  词"
    )
    def vKw(self):
        uid = self.data.se.get('user_id')
        gid = self.data.se.get('group_id')
        
        vKwList = self.mysql.selectx('SELECT * FROM `botKeyword` WHERE `state`=1 and `uuid`=%s', (self.data.uuid))
        message = '[CQ:face,id=151] {0}-关  键  词审核'.format(self.data.botSettings.get('name'))
        for i in vKwList:
            message += '\n[CQ:face,id=54] 关键词：'+str(i.get('key'))+'\n      回复：'+str(i.get('value'))+'\n      ID：'+str(i.get('id'))
        self.client.msg().raw(message)
    
    @RegCmd(
        name = "关键词垃圾箱",
        usage = "关键词垃圾箱",
        permission = "owner",
        description = "查看未通过审核的关  键  词",
        mode = "关  键  词"
    )
    def bKw(self):
        uid = self.data.se.get('user_id')
        gid = self.data.se.get('group_id')
        
        vKwList = self.mysql.selectx('SELECT * FROM `botKeyword` WHERE `state`=2 and `uuid`=%s', (self.data.uuid))
        message = '[CQ:face,id=151] {0}-关  键  词垃圾箱'.format(self.data.botSettings.get('name'))
        for i in vKwList:
            message += '\n[CQ:face,id=54] 关键词：'+str(i.get('key'))+'\n      回复：'+str(i.get('value'))+'\n      ID：'+str(i.get('id'))
        self.client.msg().raw(message)
    
    @RegCmd(
        name = "关键词审查 ",
        usage = "关键词审查 <ID> <是否通过>",
        permission = "owner",
        description = "审核关  键  词",
        mode = "关  键  词"
    )
    def tKw(self):
        uid = self.data.se.get('user_id')
        gid = self.data.se.get('group_id')
        message = self.data.message
        
        message1 = message.split(' ')
        kwid = message1[0]
        iff = message1[1]
        sql = ", `qn`=0 "
        if iff == '通过':
            state = 0
            message = '[CQ:face,id=54] 已通过！'
        elif iff == "单群":
            state = 0
            message = '[CQ:face,id=54] 已通过！'
            sql = " "
        else:
            state = 2
            message = '[CQ:face,id=54] 已移至回收站！'
        self.mysql.commonx('UPDATE `botKeyword` SET `state`=%s'+sql+'WHERE `id`=%s and `uuid`=%s', (state, kwid, self.data.uuid))
        self.client.msg().raw(message)
        
        cache.refreshFromSql('keywordList')
    
    @RegCmd(
        name = "加回复",
        usage = "加回复",
        permission = "anyone",
        description = "添加关  键  词",
        mode = "关  键  词"
    )
    def addKeyword(self):
        uid = self.data.se.get('user_id')
        gid = self.data.se.get('group_id')
        message = self.data.message
        
        ob = self.commandListener.get()
        if ob == 404:
            self.client.msg().raw('开始添加关  键  词，在此期间，你可以随时发送“退出”来退出加回复\n请发送触发该回复的关键词')
            self.commandListener.set('keyword@addKeyword', {'key':' ','value':' '})
            self.client.msg().raw('提示：加回复规则详见：\n[ https://blog.xzynb.top/archives/21/ ]')
            self.client.msg().raw('[CQ:image,file=https://pbfresources.xzynb.top/images/addKeyword/addKeyword.png]')
            return True
        
        step = int(ob.get('step'))
        args = ob.get('args')
        
        if step == 1:
            self.commandListener.set(args={'key':message,'value':' '})
            self.client.msg().raw('{0}知道了呢，那我该回答啥呢qwq？'.format(self.data.botSettings.get('name')))
        
        if step == 2:
            self.commandListener.set(args={'key':args.get('key'),'value':message})
            self.client.msg().raw('好的呢，你希望用户的好感度至少为几的时候我会回答这条消息呢\n提示：未注册用户好感度-1，也就是说你如果想让该回复适用于所有用户请发送-1')
        
        if step == 3:
            key = args.get('key')
            value = args.get('value')
            self.commandListener.remove()
            
            if uid == self.data.botSettings.get('owner'):
                g_id = 0
        mode = 0
            else:
                g_id = self.data.se.get("group_id")
        mode = 1
            
            self.mysql.commonx('INSERT INTO `botKeyword` (`key`, `value`, `state`, `uid`, `coin`, `uuid`, `qn`) VALUES (%s, %s, %s, %s, %s, %s, %s);', (key, value, mode, uid, message, self.data.uuid, g_id))
            self.client.msg().raw('恭喜你，现在只需要等待我的主人审核通过后就可以啦！')
            
            cache.refreshFromSql('keywordList')
    
    @RegCmd(
        name = "删回复 ",
        usage = "删回复 <关键词>",
        permission = "owner",
        description = "删除对应的关  键  词",
        mode = "关  键  词"
    )
    def delKeyword(self):
        uid = self.data.se.get('user_id')
        gid = self.data.se.get('group_id')
        message = self.data.message
        
        sql = 'DELETE FROM `botKeyword` WHERE `key`=%s and `uuid`=%s', (message, self.data.uuid)
        self.mysql.commonx(sql)
        self.client.msg().raw('[CQ:face,id=54] 删除成功！')
        
        cache.refreshFromSql('keywordList')
        
    def listKeyword(self):
        uid = self.data.se.get('user_id')
        gid = self.data.se.get('group_id')
        
        message1 = '[CQ:face,id=151] {0}-关  键  词列表'.format(self.data.botSettings.get('name'))
        for i in cache.get("keywordList").get(self.data.uuid):
            message1 += '\n[CQ:face,id=54] 关键词：'+str(i.get('key'))+'\n      回复：'+str(i.get('value'))+'\n      ID：'+str(i.get('id'))
        self.client.msg().raw(message1)
    
    @RegCmd(
        name = "关键词替换列表",
        usage = "关键词替换列表",
        permission = "anyone",
        description = "查看关键词替换列表",
        mode = "关  键  词"
    )
    def ListReplace(self):
        uid = self.data.se.get('user_id')
        gid = self.data.se.get('group_id')
        
        message = '[CQ:face,id=189] {0}-关键词替换列表'.format(self.data.botSettings.get('name'))
        for i in cache.get("botReplace"):
            message += '\n[CQ:face,id=54] 字段：'+i.get('key')+'\n     解释：'+i.get('explain')
        self.client.msg().raw(message)