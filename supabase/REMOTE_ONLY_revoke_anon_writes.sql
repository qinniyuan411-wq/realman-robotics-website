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

-- 5) 验证：列出当前表上的所有策略（应该为空）
SELECT schemaname, tablename, policyname, roles
FROM pg_policies
WHERE schemaname = 'public'
  AND tablename IN ('contact_submissions_cn', 'contact_submissions_en');

-- 6) 验证：列出表权限授予情况
SELECT grantee, table_name, privilege_type
FROM information_schema.role_table_grants
WHERE table_schema = 'public'
  AND table_name IN ('contact_submissions_cn', 'contact_submissions_en')
ORDER BY table_name, grantee;
