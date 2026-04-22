// Edge Function: submit-contact
// 后端代理表单提交。前端不再持有 Supabase 写入凭证，所有写库操作经此函数 + service_role 完成。
// 安全控制：
//   1. CORS / Origin 白名单（fail-closed：未配置或不在白名单一律 403）
//   2. Cloudflare Turnstile 人机验证（强制真实 siteverify，无任何测试密钥短路）
//   3. 字段强校验（长度、正则、白名单）
//   4. 内容危险标签过滤
//   5. 基于 cf-connecting-ip 的内存级限流（60 秒一次 / IP）
//
// 部署：  supabase functions deploy submit-contact --no-verify-jwt
// 配置：  supabase secrets set TURNSTILE_SECRET=xxx ALLOWED_ORIGINS="https://qinnitest.you,https://www.qinnitest.you"

import { createClient } from 'https://esm.sh/@supabase/supabase-js@2.45.4';

const SUPABASE_URL = Deno.env.get('SUPABASE_URL')!;
const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;
const TURNSTILE_SECRET = Deno.env.get('TURNSTILE_SECRET') ?? '';
const ALLOWED_ORIGINS = (Deno.env.get('ALLOWED_ORIGINS') ?? '')
  .split(',')
  .map(s => s.trim())
  .filter(Boolean);

// 注：原先内置过 Cloudflare 官方测试密钥短路（一律 PASS），已于 2026-04-22
// 安全整改第二轮 H-03 中移除。任何环境都必须配置真实 TURNSTILE_SECRET，
// 否则 verifyTurnstile 直接返回 false。

const COOLDOWN_MS = 60 * 1000;
const ipBuckets = new Map<string, number>();

const ALLOWED_REGIONS_EN = ['asia-pacific', 'europe', 'north-america', 'south-america', 'middle-east-africa'];
const ALLOWED_REGIONS_CN = ['china', 'overseas'];
const ALLOWED_INQUIRY = ['partnership', 'sales', 'technical', 'media', 'careers', 'other'];
const ALLOWED_OVERSEAS_CN = ['asia-pacific', 'europe', 'north-america', 'south-america', 'middle-east-africa'];

const MAX_LEN = {
  name: 100, email: 255, company: 200, details: 2000,
  region: 32, sub_region: 64, sub_region_label: 64,
  inquiry_type: 32, page_source: 200,
};

const EMAIL_RE = /^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$/;
const NAME_RE = /^[\p{L}\p{M}\s.\-·']{2,100}$/u;
const SUB_REGION_RE = /^[a-z]{2,32}$/;
const DANGEROUS_RE = /<\s*\/?\s*(script|iframe|object|embed|link|meta|style|svg|on\w+)/i;

function corsHeaders(origin: string | null): Record<string, string> {
  // M-09 修复：Origin 不在白名单时不发 Access-Control-Allow-Origin 头，
  // 避免回退到 ALLOWED_ORIGINS[0] 造成的非预期跨域行为。
  const isAllowed = !!origin && ALLOWED_ORIGINS.includes(origin);
  if (!isAllowed) {
    return { 'Vary': 'Origin' };
  }
  return {
    'Access-Control-Allow-Origin': origin!,
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Access-Control-Max-Age': '86400',
    'Vary': 'Origin',
  };
}

function jsonResponse(status: number, body: unknown, origin: string | null): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      'Content-Type': 'application/json',
      'X-Content-Type-Options': 'nosniff',
      ...corsHeaders(origin),
    },
  });
}

function clientIp(req: Request): string {
  // H-02 修复：优先使用上游可信头 cf-connecting-ip。
  // X-Forwarded-For 可由客户端伪造（每次换值即可绕过限流），
  // 仅在 cf-connecting-ip 不存在时降级使用。
  const cf = req.headers.get('cf-connecting-ip');
  if (cf) return cf.trim();
  const xff = req.headers.get('x-forwarded-for') ?? '';
  const first = xff.split(',')[0].trim();
  return first || 'unknown';
}

function stripTags(s: unknown): string {
  if (typeof s !== 'string') return '';
  return s.replace(/<[^>]*>/g, '').replace(/[\u0000-\u001F\u007F]/g, '').trim();
}

async function verifyTurnstile(token: string, ip: string): Promise<boolean> {
  // H-03 修复：移除测试密钥短路逻辑。任何环境都必须做真实 siteverify 调用。
  // 本地集成测试请改用 Cloudflare 官方测试 site key + secret 组合，
  // siteverify 端点仍会响应 success:true，无需短路。
  if (!TURNSTILE_SECRET) {
    console.warn('TURNSTILE_SECRET not set; rejecting all requests');
    return false;
  }
  try {
    const form = new FormData();
    form.append('secret', TURNSTILE_SECRET);
    form.append('response', token);
    form.append('remoteip', ip);
    const r = await fetch('https://challenges.cloudflare.com/turnstile/v0/siteverify', {
      method: 'POST',
      body: form,
    });
    const data = await r.json();
    return Boolean(data?.success);
  } catch (err) {
    console.error('Turnstile verify error:', err);
    return false;
  }
}

interface SubmitPayload {
  lang?: 'cn' | 'en';
  name?: string;
  work_email?: string;
  company?: string;
  region?: string;
  sub_region?: string;
  sub_region_label?: string;
  inquiry_type?: string;
  details?: string;
  page_source?: string;
  'cf-turnstile-response'?: string;
}

function validate(p: SubmitPayload): { ok: true; row: Record<string, unknown>; table: string } | { ok: false; error: string } {
  const lang = p.lang === 'cn' ? 'cn' : p.lang === 'en' ? 'en' : null;
  if (!lang) return { ok: false, error: 'invalid_lang' };

  const name = stripTags(p.name);
  const email = stripTags(p.work_email).toLowerCase();
  const company = stripTags(p.company);
  const region = stripTags(p.region);
  const inquiry = stripTags(p.inquiry_type);
  const details = stripTags(p.details);
  const pageSrc = stripTags(p.page_source).slice(0, MAX_LEN.page_source);

  if (!name || !email || !company || !region || !inquiry) return { ok: false, error: 'missing_required' };
  if (name.length > MAX_LEN.name || !NAME_RE.test(name)) return { ok: false, error: 'invalid_name' };
  if (email.length > MAX_LEN.email || !EMAIL_RE.test(email)) return { ok: false, error: 'invalid_email' };
  if (company.length > MAX_LEN.company) return { ok: false, error: 'company_too_long' };
  if (details.length > MAX_LEN.details) return { ok: false, error: 'details_too_long' };
  if (DANGEROUS_RE.test(name) || DANGEROUS_RE.test(company) || DANGEROUS_RE.test(details)) {
    return { ok: false, error: 'forbidden_content' };
  }
  if (ALLOWED_INQUIRY.indexOf(inquiry) === -1) return { ok: false, error: 'invalid_inquiry' };

  if (lang === 'en') {
    if (ALLOWED_REGIONS_EN.indexOf(region) === -1) return { ok: false, error: 'invalid_region' };
    return {
      ok: true,
      table: 'contact_submissions_en',
      row: {
        name, work_email: email, company, region,
        inquiry_type: inquiry, details, page_source: pageSrc,
      },
    };
  }

  // CN
  if (ALLOWED_REGIONS_CN.indexOf(region) === -1) return { ok: false, error: 'invalid_region' };
  const subRegion = stripTags(p.sub_region);
  const subRegionLabel = stripTags(p.sub_region_label);
  if (!subRegion || subRegion.length > MAX_LEN.sub_region || !SUB_REGION_RE.test(subRegion)) {
    return { ok: false, error: 'invalid_sub_region' };
  }
  if (region === 'overseas' && ALLOWED_OVERSEAS_CN.indexOf(subRegion) === -1) {
    return { ok: false, error: 'invalid_overseas' };
  }
  if (subRegionLabel.length > MAX_LEN.sub_region_label) {
    return { ok: false, error: 'sub_region_label_too_long' };
  }
  if (DANGEROUS_RE.test(subRegionLabel)) {
    return { ok: false, error: 'forbidden_content' };
  }

  return {
    ok: true,
    table: 'contact_submissions_cn',
    row: {
      name, work_email: email, company, region,
      sub_region: subRegion, sub_region_label: subRegionLabel,
      inquiry_type: inquiry, details, page_source: pageSrc,
    },
  };
}

Deno.serve(async (req) => {
  const origin = req.headers.get('origin');

  if (req.method === 'OPTIONS') {
    return new Response(null, { status: 204, headers: corsHeaders(origin) });
  }

  if (req.method !== 'POST') {
    return jsonResponse(405, { error: 'method_not_allowed' }, origin);
  }

  // H-01 修复：fail-closed —— 白名单为空或 Origin 不在白名单一律拒绝。
  // 原逻辑在 ALLOWED_ORIGINS 未配置时短路放行，存在 CSRF 风险。
  if (ALLOWED_ORIGINS.length === 0 || !origin || !ALLOWED_ORIGINS.includes(origin)) {
    return jsonResponse(403, { error: 'origin_not_allowed' }, origin);
  }

  if (!req.headers.get('content-type')?.includes('application/json')) {
    return jsonResponse(415, { error: 'unsupported_media_type' }, origin);
  }

  const ip = clientIp(req);
  const last = ipBuckets.get(ip) ?? 0;
  if (Date.now() - last < COOLDOWN_MS) {
    return jsonResponse(429, { error: 'rate_limited', retry_after_sec: Math.ceil((COOLDOWN_MS - (Date.now() - last)) / 1000) }, origin);
  }

  let payload: SubmitPayload;
  try {
    const raw = await req.text();
    if (raw.length > 8192) return jsonResponse(413, { error: 'payload_too_large' }, origin);
    payload = JSON.parse(raw);
  } catch {
    return jsonResponse(400, { error: 'invalid_json' }, origin);
  }

  const ts = String(payload['cf-turnstile-response'] ?? '');
  if (!ts || ts.length > 4096) {
    return jsonResponse(400, { error: 'missing_turnstile' }, origin);
  }
  const tsOk = await verifyTurnstile(ts, ip);
  if (!tsOk) return jsonResponse(403, { error: 'turnstile_failed' }, origin);

  const v = validate(payload);
  if (!v.ok) return jsonResponse(400, { error: v.error }, origin);

  // 通过校验，标记此 IP（即便 DB 写入失败也算一次提交，防止重试爆表）
  ipBuckets.set(ip, Date.now());
  if (ipBuckets.size > 5000) {
    // 简单 LRU：清理 1 小时前的条目
    const cutoff = Date.now() - 60 * 60 * 1000;
    for (const [k, t] of ipBuckets.entries()) if (t < cutoff) ipBuckets.delete(k);
  }

  try {
    const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, {
      auth: { autoRefreshToken: false, persistSession: false },
    });
    const { error } = await supabase.from(v.table).insert(v.row);
    if (error) {
      console.error('Insert error:', error);
      return jsonResponse(500, { error: 'db_insert_failed' }, origin);
    }
    return jsonResponse(200, { ok: true }, origin);
  } catch (err) {
    console.error('Unhandled error:', err);
    return jsonResponse(500, { error: 'internal' }, origin);
  }
});
