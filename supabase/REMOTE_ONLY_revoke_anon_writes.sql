-- =====================================================================
-- 仅在【远程生产】Supabase 数据库执行一次。本地开发数据库不要执行。
-- 作用：撤销 anon 角色对 contact_submissions_* 表的所有写入权限，
--      生产环境只允许通过 Edge Function（service_role）写入。
-- 操作步骤：
--   1. 打开 https://supabase.com/dashboard/project/dwtfijvpelpavdslvyry/sql/new
--   2. 把本文件全部内容粘贴进去
--   3. 点 Run（右下角绿色按钮）
--   4. 看到 "Success. No rows returned" 即为成功
-- =====================================================================

-- 1) 删除所有允许 anon 角色写入/读取的旧 RLS 策略
DROP POLICY IF EXISTS "Allow anonymous insert" ON public.contact_submissions_cn;
DROP POLICY IF EXISTS "Allow anonymous insert" ON public.contact_submissions_en;
DROP POLICY IF EXISTS "Allow anon insert"      ON public.contact_submissions_cn;
DROP POLICY IF EXISTS "Allow anon insert"      ON public.contact_submissions_en;
DROP POLICY IF EXISTS "allow_all_cn"           ON public.contact_submissions_cn;
DROP POLICY IF EXISTS "allow_all_en"           ON public.contact_submissions_en;
DROP POLICY IF EXISTS "anon_insert_cn"         ON public.contact_submissions_cn;
DROP POLICY IF EXISTS "anon_insert_en"         ON public.contact_submissions_en;
DROP POLICY IF EXISTS "anon_select_cn"         ON public.contact_submissions_cn;
DROP POLICY IF EXISTS "anon_select_en"         ON public.contact_submissions_en;

-- 2) 确保 RLS 仍然开启（开启后没有任何策略 = 默认拒绝一切非 service_role 访问）
ALTER TABLE public.contact_submissions_cn ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.contact_submissions_en ENABLE ROW LEVEL SECURITY;

-- 3) 显式回收 anon / authenticated 角色的表级权限作为双保险
REVOKE ALL ON public.contact_submissions_cn FROM anon, authenticated;
REVOKE ALL ON public.contact_submissions_en FROM anon, authenticated;

-- 4) service_role 必须保留全部权限（Edge Function 用它写库）
GRANT ALL ON public.contact_submissions_cn TO service_role;
GRANT ALL ON public.contact_submissions_en TO service_role;

-- 5) C-03 修复（2026-04-22 安全整改第二轮）：撤销默认权限授予 anon/authenticated。
--    Supabase 项目初始化时默认会给 anon/authenticated 在 public schema 下未来新建的
--    表/序列/函数自动授予 ALL —— 这意味着任何后续新建的表都会自动暴露给匿名用户。
--    这里改为"默认拒绝"：未来若要授权，必须显式 GRANT。
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public REVOKE ALL ON TABLES    FROM anon, authenticated;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public REVOKE ALL ON SEQUENCES FROM anon, authenticated;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public REVOKE ALL ON FUNCTIONS FROM anon, authenticated;
-- service_role 仍然保留完整默认权限（Supabase 平台用它做后台操作）。
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON TABLES    TO service_role;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON SEQUENCES TO service_role;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON FUNCTIONS TO service_role;

-- 7) 验证 1：列出当前表上的所有策略（应该为空）
SELECT schemaname, tablename, policyname, roles
FROM pg_policies
WHERE schemaname = 'public'
  AND tablename IN ('contact_submissions_cn', 'contact_submissions_en');

-- 8) 验证 2：列出表权限授予情况（仅应看到 service_role 与 postgres）
SELECT grantee, table_name, privilege_type
FROM information_schema.role_table_grants
WHERE table_schema = 'public'
  AND table_name IN ('contact_submissions_cn', 'contact_submissions_en')
ORDER BY table_name, grantee;

-- 9) 验证 3：列出 public schema 下的默认权限（anon/authenticated 应该完全消失）
SELECT defaclrole::regrole AS owner, defaclnamespace::regnamespace AS schema,
       defaclobjtype, defaclacl
FROM pg_default_acl
WHERE defaclnamespace = 'public'::regnamespace;
