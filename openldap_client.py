# -*- coding:utf-8 -*-

import crypt

from ldap3 import Server, Connection, SUBTREE, ALL_ATTRIBUTES, MODIFY_REPLACE


class LDAPClient(object):

    def __init__(self, host, port, adminCn, password):
        """ 初始化LDAP客户端参数

        :参数 host: LDAP Server地址
        :参数 port: LDAP Server端口
        :参数 adminCn: LDAP admin管理CN
        :参数 password: LDAP admin密码
        """

        self.host = host
        self.port = port
        self.adminCn = adminCn
        self.password = password


    def get_connetion(self):
        """ 连接LDAP Server

        :返回: 客户端实例
        """

        server = Server(host=self.host, port=self.port)
        client = Connection(server, user=self.adminCn, password=self.password, auto_bind=True)
        
        return client


    def search(self, dn, scope=SUBTREE):
        """ 搜索LDAP指定DN数据

        :参数 dn: LDAP中一条完整的数据记录("uid=user1,dc=test,dc=net")
        :参数 scope: 设定搜索行的范围
        :返回: 操作结果True/False, dn数据
        """

        client = self.get_connetion()
        result = client.search(search_base=dn, search_scope=scope, search_filter="(objectClass=*)", attributes=ALL_ATTRIBUTES)
        
        return result, client.response


    def add(self, dn, entry):
        """ 添加LDAP DN数据
        :参数 dn: LDAP中一条完整的数据记录("uid=user1,dc=test,dc=net")
        :参数 entry: 指定DN记录详细参数配置
        :返回: True/False
        """

        client = self.get_connetion()
        client.add(dn, attributes=entry)

        if client.result["result"] == 0:
            return True
        
        return False


    def modify(self, dn, entry):
        """ 修改LDAP DN数据
        :参数 dn: LDAP中一条完整的数据记录("uid=user1,dc=test,dc=net")
        :参数 entry: 修改dn的数据，例如{"loginShell": "/sbin/nologin"}
        :返回: True/False
        """

        changes = {}

        for k, v in entry.items():
            changes[k] = [(MODIFY_REPLACE, [v])]
        
        client = self.get_connetion()
        client.modify(dn, changes=changes)

        if client.result["result"] == 0:
            return True
        
        return False


    def delete(self, dn):
        """ 删除指定dn的数据

        :参数 dn: LDAP中一条完整的数据记录("uid=user1,dc=test,dc=net")
        :返回: True/False
        """

        client = self.get_connetion()
        client.delete(dn)

        if client.result["result"] == 0:
            return True
        
        return False


    def add_user(self, userId, userDn, groupDn, sudoDn, username, password):
        """ 添加LDAP用户
            已经存在的用户将会重新添加

        :参数 userId: Unix/Linux系统用户id
        :参数 userDn: 用户完整记录
        :参数 groupDn: 用户组完整记录
        :参数 username: 用户名
        :参数 password: 用户密码
        :返回: True/False
        """

        userId = str(userId)
        password = crypt.crypt(password, password)

        userEntry = dict(
            uid = [username],
            cn = [username],
            objectClass = ["account", "posixAccount", "top", "shadowAccount"],
            userPassword = ["{CRYPT}%s" % password],
            shadowLastChange =  ["16384"],
            shadowMin = ["0"],
            shadowMax = ["99999"],
            shadowWarning = ["6"],
            loginShell = ["/bin/bash"],
            uidNumber = [userId],
            gidNumber = [userId],
            homeDirectory = ["/home/" + username]
        )

        groupEntry = dict(
            objectClass = ["posixGroup", "top"],
            cn = [username],
            userPassword = ["{CRYPT}x"],
            gidNumber = [userId]
        )

        exist = self.search(userDn)

        if exist:
            self.delete_user(userDn, groupDn, sudoDn)

        addUserResult = self.add(dn=userDn, entry=userEntry)
        addGroupResult = self.add(dn=groupDn, entry=groupEntry)

        if addUserResult and addGroupResult:
            return True
        
        return False


    def grant_sudo(self, username, sudoDn, sudoHost):
        """ 授权LDAP用户Sudo权限
            已经存在的Sudo权限将会重新授权

        :参数 username: 授权用户名
        :参数 sudoDn: 用户Sudo完整记录
        :参数 sudoHost: 授权Sudo主机列表
        :返回: True/False
        """

        sudoEntry = dict(
            objectClass = ["sudoRole", "top"],
            cn = username,
            sudoUser = ["%" + username],
            sudoHost = sudoHost,
            sudoRunAsUser = ["root"],
            sudoCommand = ["!/bin/bash", "ALL"],
            sudoOption = ["!visiblepw", "!authenticate", "always_set_home", "env_reset", "requiretty"]
        )

        exist = self.search(sudoDn)

        if exist:
            self.revoke_sudo(sudoDn)
            
        return self.add(dn=sudoDn, entry=sudoEntry)


    def revoke_sudo(self, sudoDn):
        """ 撤销LDAP Sudo用户

        :参数 sudoDn: 用户Sudo完整记录
        :返回: True/False
        """

        return self.delete(dn=sudoDn)


    def delete_user(self, userDn, groupDn, sudoDn):
        """ 删除LDAP用户

        :参数 userDn: 用户完整记录
        :参数 groupDn: 用户组完整记录
        :参数 sudoDn: 用户Sudo完整记录
        :返回: True/False
        """

        sudoGranted, _ = self.search(dn=sudoDn)
        
        if sudoGranted:
            self.delete(dn=sudoDn)

        deleteGroupResult = self.delete(dn=groupDn)
        deleteUserResult = self.delete(dn=userDn)

        if deleteUserResult and deleteGroupResult:
            return True
        
        return False


    def modify_user_shell(self, dn, shell):
        """ 修改系统用户登陆的shell环境

        :参数 dn: 用户完整记录
        :参数 shell: shell环境，例如 /bin/bash
        :返回: True/False
        """

        entry = {"loginShell": shell}

        return self.modify(dn=dn, entry=entry)


if __name__ == "__main__":
    ldap = LDAPClient(host="127.0.0.1", port=389, adminCn="cn=admin,dc=test,dc=net", password="admin")
    ldap.search(dn="uid=test1,ou=users,dc=test,dc=net")
    ldap.add_user(userId=2078, userDn="uid=test3,ou=users,dc=test,dc=net", groupDn="cn=test3,ou=groups,dc=test,dc=net", sudoDn="cn=test3,ou=sudoers,dc=test,dc=net", username="test3", password="test")
    ldap.grant_sudo(username="test3", sudoDn="cn=test3,ou=sudoers,dc=test,dc=net", sudoHost=["ALL"])
    ldap.revoke_sudo(sudoDn="cn=test3,ou=sudoers,dc=test,dc=net")
    ldap.modify_user_shell(dn="uid=test3,ou=users,dc=test,dc=net", shell="/sbin/nologin")
    ldap.delete_user(userDn="uid=test3,ou=users,dc=test,dc=net", groupDn="cn=test3,ou=groups,dc=test,dc=net", sudoDn="cn=test3,ou=sudoers,dc=test,dc=net")

