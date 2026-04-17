-- Fix RLS policies: need both INSERT and SELECT policies for PostgREST compatibility
DROP POLICY IF EXISTS "Allow anonymous insert" ON public.contact_submissions_cn;
DROP POLICY IF EXISTS "Allow anonymous insert" ON public.contact_submissions_en;
DROP POLICY IF EXISTS "Allow anon insert" ON public.contact_submissions_cn;
DROP POLICY IF EXISTS "Allow anon insert" ON public.contact_submissions_en;
DROP POLICY IF EXISTS "allow_all_cn" ON public.contact_submissions_cn;
DROP POLICY IF EXISTS "allow_all_en" ON public.contact_submissions_en;

CREATE POLICY "anon_insert_cn" ON public.contact_submissions_cn FOR INSERT WITH CHECK (true);
CREATE POLICY "anon_insert_en" ON public.contact_submissions_en FOR INSERT WITH CHECK (true);
CREATE POLICY "anon_select_cn" ON public.contact_submissions_cn FOR SELECT USING (true);
CREATE POLICY "anon_select_en" ON public.contact_submissions_en FOR SELECT USING (true);
