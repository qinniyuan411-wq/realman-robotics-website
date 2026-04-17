


SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;


COMMENT ON SCHEMA "public" IS 'standard public schema';



CREATE EXTENSION IF NOT EXISTS "pg_graphql" WITH SCHEMA "graphql";






CREATE EXTENSION IF NOT EXISTS "pg_stat_statements" WITH SCHEMA "extensions";






CREATE EXTENSION IF NOT EXISTS "pgcrypto" WITH SCHEMA "extensions";






CREATE EXTENSION IF NOT EXISTS "supabase_vault" WITH SCHEMA "vault";






CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA "extensions";






CREATE OR REPLACE FUNCTION "public"."rls_auto_enable"() RETURNS "event_trigger"
    LANGUAGE "plpgsql" SECURITY DEFINER
    SET "search_path" TO 'pg_catalog'
    AS $$
DECLARE
  cmd record;
BEGIN
  FOR cmd IN
    SELECT *
    FROM pg_event_trigger_ddl_commands()
    WHERE command_tag IN ('CREATE TABLE', 'CREATE TABLE AS', 'SELECT INTO')
      AND object_type IN ('table','partitioned table')
  LOOP
     IF cmd.schema_name IS NOT NULL AND cmd.schema_name IN ('public') AND cmd.schema_name NOT IN ('pg_catalog','information_schema') AND cmd.schema_name NOT LIKE 'pg_toast%' AND cmd.schema_name NOT LIKE 'pg_temp%' THEN
      BEGIN
        EXECUTE format('alter table if exists %s enable row level security', cmd.object_identity);
        RAISE LOG 'rls_auto_enable: enabled RLS on %', cmd.object_identity;
      EXCEPTION
        WHEN OTHERS THEN
          RAISE LOG 'rls_auto_enable: failed to enable RLS on %', cmd.object_identity;
      END;
     ELSE
        RAISE LOG 'rls_auto_enable: skip % (either system schema or not in enforced list: %.)', cmd.object_identity, cmd.schema_name;
     END IF;
  END LOOP;
END;
$$;


ALTER FUNCTION "public"."rls_auto_enable"() OWNER TO "postgres";

SET default_tablespace = '';

SET default_table_access_method = "heap";


CREATE TABLE IF NOT EXISTS "public"."contact_submissions_cn" (
    "id" bigint NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"(),
    "name" "text" NOT NULL,
    "work_email" "text" NOT NULL,
    "company" "text" DEFAULT ''::"text" NOT NULL,
    "region" "text" DEFAULT ''::"text" NOT NULL,
    "sub_region" "text" DEFAULT ''::"text" NOT NULL,
    "sub_region_label" "text" DEFAULT ''::"text" NOT NULL,
    "inquiry_type" "text" DEFAULT ''::"text" NOT NULL,
    "details" "text" DEFAULT ''::"text",
    "page_source" "text" DEFAULT ''::"text"
);


ALTER TABLE "public"."contact_submissions_cn" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."contact_submissions_cn_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE "public"."contact_submissions_cn_id_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."contact_submissions_cn_id_seq" OWNED BY "public"."contact_submissions_cn"."id";



CREATE TABLE IF NOT EXISTS "public"."contact_submissions_en" (
    "id" bigint NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"(),
    "name" "text" NOT NULL,
    "work_email" "text" NOT NULL,
    "company" "text" DEFAULT ''::"text" NOT NULL,
    "region" "text" DEFAULT ''::"text" NOT NULL,
    "inquiry_type" "text" DEFAULT ''::"text" NOT NULL,
    "details" "text" DEFAULT ''::"text",
    "page_source" "text" DEFAULT ''::"text"
);


ALTER TABLE "public"."contact_submissions_en" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."contact_submissions_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE "public"."contact_submissions_id_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."contact_submissions_id_seq" OWNED BY "public"."contact_submissions_en"."id";



ALTER TABLE ONLY "public"."contact_submissions_cn" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."contact_submissions_cn_id_seq"'::"regclass");



ALTER TABLE ONLY "public"."contact_submissions_en" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."contact_submissions_id_seq"'::"regclass");



ALTER TABLE ONLY "public"."contact_submissions_cn"
    ADD CONSTRAINT "contact_submissions_cn_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."contact_submissions_en"
    ADD CONSTRAINT "contact_submissions_pkey" PRIMARY KEY ("id");



CREATE POLICY "Allow anonymous insert" ON "public"."contact_submissions_cn" FOR INSERT WITH CHECK (true);



CREATE POLICY "Allow anonymous insert" ON "public"."contact_submissions_en" FOR INSERT WITH CHECK (true);



ALTER TABLE "public"."contact_submissions_cn" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."contact_submissions_en" ENABLE ROW LEVEL SECURITY;




ALTER PUBLICATION "supabase_realtime" OWNER TO "postgres";


GRANT USAGE ON SCHEMA "public" TO "postgres";
GRANT USAGE ON SCHEMA "public" TO "anon";
GRANT USAGE ON SCHEMA "public" TO "authenticated";
GRANT USAGE ON SCHEMA "public" TO "service_role";

























































































































































GRANT ALL ON FUNCTION "public"."rls_auto_enable"() TO "anon";
GRANT ALL ON FUNCTION "public"."rls_auto_enable"() TO "authenticated";
GRANT ALL ON FUNCTION "public"."rls_auto_enable"() TO "service_role";


















GRANT ALL ON TABLE "public"."contact_submissions_cn" TO "anon";
GRANT ALL ON TABLE "public"."contact_submissions_cn" TO "authenticated";
GRANT ALL ON TABLE "public"."contact_submissions_cn" TO "service_role";



GRANT ALL ON SEQUENCE "public"."contact_submissions_cn_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."contact_submissions_cn_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."contact_submissions_cn_id_seq" TO "service_role";



GRANT ALL ON TABLE "public"."contact_submissions_en" TO "anon";
GRANT ALL ON TABLE "public"."contact_submissions_en" TO "authenticated";
GRANT ALL ON TABLE "public"."contact_submissions_en" TO "service_role";



GRANT ALL ON SEQUENCE "public"."contact_submissions_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."contact_submissions_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."contact_submissions_id_seq" TO "service_role";









ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES TO "postgres";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES TO "anon";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES TO "authenticated";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES TO "service_role";






ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS TO "postgres";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS TO "anon";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS TO "authenticated";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS TO "service_role";






ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES TO "postgres";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES TO "anon";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES TO "authenticated";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES TO "service_role";



































