# PromoxVE安装笔记

> 原文链接：https://blog.csdn.net/qq_36991535/article/details/163616936
> 发布时间：2026-08-09 23:12:13
> 作者：Anesthesia丶

家里一直有一台之前为了入门AI，搞了一台 e52666v3 + 32G + Tesa P40 24G的主机。

年少无知，倒不是说完全不能用，只是使用起来各种瓶颈，踩了很多坑，还升级了 64g 双通道，最后因为噪音实在是接受不了，所以持巨资入手了 i9 13900 + 3080，近段时间把 P40 显卡也卖了，正愁剩余的古董该怎么办~ 突然想起公司一直用 PromoxVE 在管理虚拟机，如果把这台机器装上 PromoxVE，作为家用的中枢服务器，也方便我做各种实验去折腾，好像也还不错~ 于是有了今天这篇笔记~

## 一、PC环境

- CPU：e5 2666v3
- GPU: GTX 1050TI 4G（作为亮机卡）
- 主板：华南x99 AD3
- 内存：ddr3 1600 64g

## 二、U盘制作

- 工具: rufus
- 镜像: proxmox-ve_9.2-1.iso
- U盘：16g （镜像本身有9g，推荐16g及以上）

### 1、工具下载

https://rufus.ie/zh/

选择便携版即可，免安装版本。

![rufus下载](https://p3-doubao-search-sign.byteimg.com/labis/image/a78a264a102ef593c8095f7b6bf3daa8~tplv-be4g95zd3a-896x896.jpeg?lk3s=0ed4045e&x-expires=1805641984&x-signature=wcNyhftY7UnrOMxPE2sz0vvfiPg%3D)

### 2、镜像下载

https://mirrors.tuna.tsinghua.edu.cn/proxmox/iso/

这里直接给国内镜像源，官方源下载速度感人。

![镜像下载](https://p3-doubao-search-sign.byteimg.com/labis/image/434227a455bb6a851e08c4704a39afb8~tplv-be4g95zd3a-896x896.jpeg?lk3s=0ed4045e&x-expires=1805641984&x-signature=jn2AEcEVv3Fc8hZkulF0dbdEVYI%3D)

### 3、U盘制作

注意点：

- 直接点击【选择】，找到你下载的 promox ve 的 ISO 文件即可，中间会有警告不用管。
- 其它选项保持默认，点击开始即可，会格式化你的U盘，也会有些警告，不用管。
- 确定状态为 100% 即可，不会有完成的提示信息，**U盘会提示无法识别，要求格式化，千万不要点击，直接弹出即可。**

![rufus制作](https://p3-doubao-search-sign.byteimg.com/labis/image/64708e0cc001dfe330bb57b43dd696c9~tplv-be4g95zd3a-896x896.jpeg?lk3s=0ed4045e&x-expires=1805641984&x-signature=DkqUfsCEkaH5PF3xVPUviL0sEQ8%3D)

## 三、安装 Promox VE 系统

准备：

- 制作好的U盘
- 安装系统的电脑
- 网络（网线连接）

这部分只有两个注意事项，其它的不赘述，基本都是无脑下一步：

- **密码设置**：中间会要求你设置 root 密码，尽量设置简单一些，反正我是踩了坑的（两遍）~

如果你不幸也登陆不上，参照以下步骤重置密码，不需要重装：

1. 开机出现 GRUB 菜单，按 `e` 编辑启动项
2. 找到以 `linux` 开头那一行，拖到行尾，空格后加上：

```bash
init=/bin/bash
```

![GRUB编辑](https://p3-doubao-search-sign.byteimg.com/labis/image/d7d76c5bda900468fca877693431150d~tplv-be4g95zd3a-896x896.jpeg?lk3s=0ed4045e&x-expires=1805641984&x-signature=6ZGqn43NDIBmgcT3%2F3TC4RQt4nc%3D)

3. 按下 `Ctrl+X` 直接启动，此时会跳进 root 命令行（免登录）
4. 依次敲下面两行命令，每一行输完回车：

```bash
mount -o remount,rw /
passwd root
```

这时会提示输入新密码、再确认一次。

5. 执行这条命令正常启动系统即可：

```bash
exec /sbin/init
```

## 四、管理员登录

正常来讲，安装完以后，可以通过 `ip:8006` 端口访问管理页面。

- 用户名: root
- 密码: 【你设置的密码】
- Realm 域: Linux PAM standard authentication

正常登录页面参考下图：

![PVE管理界面](https://p26-doubao-search-sign.byteimg.com/labis/image/b283de1039b3d2d44abdfafaa1253e5a~tplv-be4g95zd3a-896x896.jpeg?lk3s=0ed4045e&x-expires=1805641984&x-signature=swsWGBCL4qMPJSMyqLnOtiy5aPc%3D)

## 五、操作镜像预上传

到目前为止，Promox VE 已经被正常安装了，但是发现创建虚拟机时没有可选的镜像。

ubuntu 下载地址（国内镜像源）：
https://mirror.sysu.edu.cn/ubuntu-releases/releases/releases/

OK，到这里你就拥有了一台家用的服务器管理中心~

愿看到的小伙伴不迷路~
