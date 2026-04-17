# 本地 Supabase 开发环境

## 前置条件

- Docker Desktop（已安装在 D:\DockerDesktop）
- Supabase CLI（已通过 scoop 安装，v2.90.0）

## 日常使用

### 启动本地环境

```bash
# 先启动 Docker Desktop，等引擎就绪
# 然后在项目根目录执行：
supabase start
```

启动后可用的本地服务：

| 服务 | 地址 |
|------|------|
| API | http://127.0.0.1:54321 |
| Studio 管理面板 | http://127.0.0.1:54323 |
| 数据库 | postgresql://postgres:postgres@127.0.0.1:54322/postgres |

### 停止本地环境

```bash
supabase stop
```

### 查看状态

```bash
supabase status
```

## 环境切换

前端 JS（`prop/supabase-cta.js` 和 `prop/supabase-cta-cn.js`）会自动根据 hostname 判断：

- `localhost` / `127.0.0.1` → 连本地 Supabase
- 其他域名 → 连线上 Supabase（dwtfijvpelpavdslvyry.supabase.co）

无需手动切换。

## 数据库变更管理

所有表结构变更统一通过 migration 文件管理：

```bash
# 在本地 Studio 改完表结构后，生成 migration
supabase db diff -f <migration_name>

# 重置本地数据库（按 migrations 重建）
supabase db reset

# 推送变更到线上
supabase db push
```

Migration 文件位于 `supabase/migrations/` 目录。

## 迁移到新服务器

1. 新服务器安装 Docker
2. 复制整个项目（含 `supabase/` 目录）到新服务器
3. `supabase start` 启动
4. 如需迁移线上数据：`supabase db dump` → `psql` 导入

## 线上项目信息

- Project Ref: `dwtfijvpelpavdslvyry`
- Region: West US (Oregon)
- 表：`contact_submissions_cn`、`contact_submissions_en`
