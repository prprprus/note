## Git

### Git 的基本概念

- 工作区（本地）：还没 add 的文件待的地方
- 缓存区（本地）：add 后的文件待的地方
- Git 仓库（本地）：commit 后的文件待的地方
- Git 仓库（远端）：push 后的文件待的地方

### Git 常用命令

#### 分支操作

- 查看本地分支：`git branch`
- 查看本地和远端分支：`git branch -a`
- 切换分支：`git checkout <branch>`
- 创建分支并且过去：`git checkout -b <branch>`

#### 推送操作

- 将远端 Git 仓库的代码同步到本地 Git 仓库：`git pull`
- 此时如果有冲突则要解决它
- 将工作区的文件添加到缓存区：`git add <file>/*`
- 将缓存区的文件添加到本地 Git 仓库：`git commit -m <commit_message>`
- 将本地 Git 仓库的文件推送到远端 Git 仓库：`git push -u origin <branch>`

#### 回滚操作

- 回滚工作区（新建文件）：`git rm --cached <file>/*`
- 回滚工作区（修改文件）：`git checkout -- <file>/*`
- 回滚缓存区（修改文件）：` git reset HEAD <file>/* && git checkout -- <file>/*`
- 回滚本地 Git 仓库：`git reset --hard <commit_id>`
- 回滚远端 Git 仓库：`git reset --hard <commit_id> && git push -f`

#### 其他

- clone 项目：`git clone <git_address>/<https_address>`
- 查看本地状态：`git status`

> Git 命令支持部分正则符号

### Git 分支管理策略

Git 作为一个开发团队协作工具，功能并不仅仅是代码版本管理，它本身的一些概念还会影响到整个开发流程和规范的搭建。

分支管理就是这样的概念。不同的开发团队可能有不同的 Git 分支管理策略，一般小公司可能比较随意，大公司可能就相对规范一点。下面记录一下个人感觉还不错的一种

分支种类：

- master 分支：对应生产环境代码
- beta 分支：对应预发布环境代码
- develop 分支：对应测试环境代码（小组内的公共测试环境）
- 个人开发分支

操作流程：

- 在个人开发分支进行开发
- 开发初步完成之后，手动合并个人开发分支到 develop 分支（由于可能需要解决冲突，所以合并这一步还是需要人参与），推送 develop 分支，跑
  CI/CD
- 到测试环境验证没问题后，手动合并个人开发分支到 beta 分支，推送 beta 分支，跑 CI/CD
- 到预发布环境验证没问题后，提交 MR，进行 Code Review，没问题再合并并推送 master 分支，跑 CI/CD
- 完成一次迭代发布

> 可以根据实际情况来做加减法，比如公司提供的资源不是很充足的时候，可以去掉预发布环境等

### GUI 工具

- Sourcetree

### 常见问题

- 解决拉远端分支失败：https://github.com/flutter/flutter/issues/15134
