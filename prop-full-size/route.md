# Route.md — 网站上线全流程指南

> 本文档记录 realman-website 从本地静态页面到正式上线的完整流程。  
> 每次上线新网站或修改现有网站时，按此指引操作即可。

---

## 总览

| 步骤 | 内容 | 状态 |
|------|------|------|
| 1 | 绑定 Supabase 后端数据库 | ✅ 完成 |
| 2 | 上传代码到 GitHub | ✅ 完成 |
| 3 | 通过 Vercel 部署上线 | ✅ 完成 |
| 4 | 绑定自定义域名（Porkbun） | ✅ 完成 |

---

## 当前线上信息

| 项目 | 值 |
|------|-----|
| 网站域名 | https://qinnitest.you |
| Vercel URL | https://realman-website.vercel.app |
| GitHub 仓库 | https://github.com/qinniyuan411-wq/realman-robotics-website |
| Supabase 项目 | https://supabase.com/dashboard/project/dwtfijvpelpavdslvyry |
| 数据库表 | `contact_submissions` |

---

## 第一步：绑定 Supabase 后端数据库

### 1.1 Supabase 项目信息

| 项目 | 值 |
|------|-----|
| Project URL | `https://dwtfijvpelpavdslvyry.supabase.co` |
| Publishable Key (anon) | `sb_publishable_p0hMaphSABTlKZiLXtDcBQ_ZU_Nvel0` |
| Database 直连 | `postgresql://postgres:[PASSWORD]@db.dwtfijvpelpavdslvyry.supabase.co:5432/postgres` |

### 1.2 如需重建数据库表

如果 Supabase 项目中有旧表需要清理，在 Supabase Dashboard → SQL Editor 执行：

```sql
-- 删除旧表
DROP TABLE IF EXISTS cta_submissions;
DROP TABLE IF EXISTS contact_submissions;
```

### 1.3 创建新数据库表

在 SQL Editor 中执行：

```sql
CREATE TABLE contact_submissions (
  id           BIGSERIAL PRIMARY KEY,
  created_at   TIMESTAMPTZ DEFAULT NOW(),
  name         TEXT NOT NULL,
  work_email   TEXT NOT NULL,
  company      TEXT NOT NULL DEFAULT '',
  region       TEXT NOT NULL DEFAULT '',
  inquiry_type TEXT NOT NULL DEFAULT '',
  details      TEXT DEFAULT '',
  page_source  TEXT DEFAULT ''
);

-- 启用 Row Level Security
ALTER TABLE contact_submissions ENABLE ROW LEVEL SECURITY;

-- 允许匿名用户 INSERT（网站前端提交表单用）
CREATE POLICY "Allow anonymous insert"
  ON contact_submissions
  FOR INSERT
  WITH CHECK (true);
```

### 1.4 前端连接脚本

网站通过 `prop/supabase-cta.js` 连接 Supabase。该脚本：
- 监听所有页面中 `#contact-form` 表单的提交事件
- 使用 Supabase REST API（PostgREST）直接 POST 数据
- 不依赖任何 npm 包，纯 fetch 调用

**关键配置（在 `prop/supabase-cta.js` 开头）：**
```javascript
var SUPABASE_URL = 'https://dwtfijvpelpavdslvyry.supabase.co';
var SUPABASE_KEY = 'sb_publishable_p0hMaphSABTlKZiLXtDcBQ_ZU_Nvel0';
```

### 1.5 在 HTML 页面中引用脚本

每个包含 CTA 表单的 HTML 页面底部（`</body>` 前）添加：
```html
<script src="../prop/supabase-cta.js"></script>
```
> `main/` 和 `products/` 目录下的页面路径都是 `../prop/`

### 1.6 测试

1. 在浏览器打开任意页面
2. 滚动到底部 "Get in Touch" 表单
3. 填写所有字段并提交
4. 检查 Supabase Dashboard → Table Editor → `contact_submissions`，确认数据已写入

---

## 第二步：上传代码到 GitHub

### 2.1 账户信息

| 项目 | 值 |
|------|-----|
| GitHub 用户名 | `qinniyuan411-wq` |
| 邮箱 | `qinniyuan411@gmail.com` |
| 仓库名 | `realman-robotics-website` |
| 仓库地址 | https://github.com/qinniyuan411-wq/realman-robotics-website |

### 2.2 如需删除旧仓库重建

```bash
# 1. 授权 delete_repo 权限（首次需要）
gh auth refresh -h github.com -s delete_repo

# 2. 删除旧仓库
gh repo delete qinniyuan411-wq/realman-robotics-website --yes
```

### 2.3 初始化并推送新代码

```bash
cd realman-website

# 初始化 git
git init
git config user.name "qinniyuan411-wq"
git config user.email "qinniyuan411@gmail.com"

# 添加所有文件并提交
git add .
git commit -m "Initial commit: realman-website v2"

# 创建 GitHub 仓库并推送
gh repo create qinniyuan411-wq/realman-robotics-website --public --source=. --push
```

### 2.4 后续更新推送

每次修改网站文件后：
```bash
cd realman-website
git add .
git commit -m "描述修改内容"
git push
```

---

## 第三步：通过 Vercel 部署上线

### 3.1 账户信息

| 项目 | 值 |
|------|-----|
| Vercel 用户名 | `qinniyuan411-2758` |
| 邮箱 | `qinniyuan411@gmail.com` |
| 项目名 | `realman-website` |
| 项目 URL | https://realman-website.vercel.app |

### 3.2 如需删除旧项目重建

```bash
# 查看现有项目
vercel ls

# 删除旧项目
vercel rm 旧项目名 --yes
```

### 3.3 首次部署

```bash
cd realman-website

# 部署到 Vercel（会自动创建项目）
vercel --yes --prod
```

### 3.4 vercel.json 配置

项目根目录的 `vercel.json` 控制路由：
```json
{
  "rewrites": [
    { "source": "/", "destination": "/main/home.html" }
  ]
}
```
> 这使得访问根域名 `/` 时自动显示 `main/home.html`

### 3.5 后续重新部署

修改代码后：
```bash
cd realman-website
vercel --prod
```

或者如果已连接 GitHub，推送代码后 Vercel 会自动部署。

---

## 第四步：绑定自定义域名（Porkbun）

### 4.1 域名信息

| 项目 | 值 |
|------|-----|
| 域名 | `qinnitest.you` |
| 域名注册商 | Porkbun |

### 4.2 在 Vercel 添加域名

```bash
vercel domains add qinnitest.you
vercel domains add www.qinnitest.you
```

### 4.3 在 Porkbun 配置 DNS

登录 Porkbun → Domain Management → DNS Records，添加以下记录：

| Type | Host | Answer / Value | TTL |
|------|------|---------------|-----|
| A | `qinnitest.you` | `76.76.21.21` | 600 |
| CNAME | `www.qinnitest.you` | `cname.vercel-dns.com` | 600 |

### 4.4 验证

```bash
# 检查 DNS 解析
nslookup qinnitest.you
nslookup www.qinnitest.you

# 验证域名状态
vercel domains inspect qinnitest.you
```

等待 DNS 生效（通常 5-30 分钟），访问 https://qinnitest.you 确认网站正常。

---

## 日常维护操作

### 修改网站内容后重新部署

```bash
cd realman-website
git add .
git commit -m "描述修改内容"
git push
vercel --prod
```

### 查看表单提交数据

登录 Supabase Dashboard → Table Editor → `contact_submissions`

### 修改表单字段

1. 修改 Supabase 数据库表结构（ALTER TABLE 或在 SQL Editor 中重建）
2. 修改 `prop/supabase-cta.js` 中的字段映射
3. 修改各 HTML 页面中的表单 HTML
4. 重新部署

### 更换域名

1. 在 Vercel 添加新域名：`vercel domains add 新域名`
2. 在域名注册商配置 DNS（A 记录指向 `76.76.21.21`，CNAME 指向 `cname.vercel-dns.com`）
3. 移除旧域名：`vercel domains rm 旧域名`

---

## 项目文件结构

```
realman-website/
├── main/                    # 主页面（7个）
│   ├── home.html            # 首页
│   ├── core-products.html   # 核心产品
│   ├── teleoperation-network.html
│   ├── data-services.html
│   ├── solutions.html
│   ├── developer-center.html
│   └── about-us.html
├── products/                # 产品详情页（13个）
│   ├── rm65.html, rm75.html, rml63.html
│   ├── eco62.html, eco63.html, eco65.html
│   ├── rx75.html
│   ├── whj-joint-modules.html, whj-torque-joint-modules.html, whg-joint-modules.html
│   ├── realbot-humanoid.html, single-arm-lift.html, dual-arm-lift.html
├── prop/                    # 资源文件
│   ├── supabase-cta.js      # Supabase 表单提交脚本
│   ├── three.min.js         # Three.js（Vanta 依赖）
│   ├── vanta.halo.min.js    # Vanta 背景效果
│   ├── *.png / *.jpg        # 图片资源
│   ├── design.md            # 设计规范
│   ├── check.md             # 已知问题
│   └── route.md             # 本文件
├── vercel.json              # Vercel 路由配置
└── .gitignore
```
