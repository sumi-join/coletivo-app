-- Painel · administração da operação (Nanda) — 21/11/2026
-- Horário editável, datas fechadas, pausa da loja, aviso no topo do app, lista da equipe e registro de quem mudou.
-- SÓ ADITIVO: tabelas/colunas/funções/policies/triggers novos. Não altera nem apaga nada que já existia.
-- Rodar como postgres (dono). Idempotente. Termina recarregando o schema do PostgREST.

begin;

-- ── 5. lista da equipe (login Google individual) ─────────────────────────────
create table if not exists public.equipe (
  email      text primary key check (email = lower(email)),
  nome       text not null,
  papel      text not null default 'operacao',
  ativo      boolean not null default true,
  criado_em  timestamptz not null default now()
);
insert into public.equipe (email, nome, papel) values
  ('riosandolito@gmail.com', 'Cozinha (login compartilhado)', 'cozinha'),
  ('eduardo.sumi@gmail.com', 'Eduardo', 'socio')
on conflict (email) do nothing;

-- equipe "nova": a allowlist antiga (eh_equipe) OU um e-mail ativo na tabela equipe.
create or replace function public.eh_equipe2() returns boolean
  language sql stable security definer set search_path = public, auth as $$
  select public.eh_equipe()
      or exists (select 1 from public.equipe e
                  where e.email = lower(coalesce(auth.email(), '')) and e.ativo)
$$;
-- o painel pergunta "quem sou eu aqui" logo depois do login Google
create or replace function public.meu_acesso() returns json
  language sql stable security definer set search_path = public, auth as $$
  select json_build_object(
    'email', auth.email(),
    'lista', public.eh_equipe2(),          -- pode entrar no painel (abas de loja/cardápio)
    'completo', public.eh_equipe(),        -- vê pedidos/cupons/etc (allowlist antiga)
    'nome', (select nome from public.equipe where email = lower(coalesce(auth.email(), ''))))
$$;
grant execute on function public.eh_equipe2(), public.meu_acesso() to authenticated;

-- ── registro de quem mudou o quê ─────────────────────────────────────────────
create table if not exists public.admin_log (
  id        bigserial primary key,
  em        timestamptz not null default now(),
  tabela    text not null,
  operacao  text not null,
  chave     text,
  antes     jsonb,
  depois    jsonb,
  por_email text,
  por_nome  text
);
create index if not exists admin_log_em on public.admin_log (em desc);

-- carimbo: quem (e-mail do login, à prova de forja) + quando, antes de gravar
create or replace function public.carimbar_mudanca() returns trigger
  language plpgsql as $$
begin
  new.atualizado_em  := now();
  new.atualizado_por := coalesce(auth.email(), current_user);
  return new;
end $$;

-- log: uma linha por mudança (insert/update/delete) com antes/depois
create or replace function public.registrar_mudanca() returns trigger
  language plpgsql security definer set search_path = public, auth as $$
declare
  a jsonb := case when tg_op <> 'INSERT' then to_jsonb(old) end;
  d jsonb := case when tg_op <> 'DELETE' then to_jsonb(new) end;
  hdr text := nullif(current_setting('request.headers', true), '');
  nome text := coalesce(d->>'atualizado_nome', d->>'criado_nome',
                        case when hdr is not null then hdr::json->>'x-quem' end);
begin
  insert into public.admin_log (tabela, operacao, chave, antes, depois, por_email, por_nome)
  values (tg_table_name, tg_op,
          coalesce(d, a)->>(case tg_table_name when 'loja_horario' then 'dia'
                                               when 'loja_fechada' then 'data'
                                               else 'id' end),
          a, d, coalesce(auth.email(), current_user), nome);
  return coalesce(new, old);
end $$;

-- ── 1. horário por dia da semana (0 = domingo … 6 = sábado, igual JS getDay) ──
create table if not exists public.loja_horario (
  dia             smallint primary key check (dia between 0 and 6),
  aberto          boolean  not null default false,
  abre_min        smallint check (abre_min between 0 and 1439),
  fecha_min       smallint check (fecha_min between 1 and 1440),
  atualizado_em   timestamptz not null default now(),
  atualizado_por  text,
  atualizado_nome text,
  check (not aberto or (abre_min is not null and fecha_min is not null and fecha_min > abre_min))
);
insert into public.loja_horario (dia, aberto, abre_min, fecha_min, atualizado_por, atualizado_nome) values
  (0, false, null, null, 'migracao', 'Eduardo (21/11)'),
  (1, false, null, null, 'migracao', 'Eduardo (21/11)'),
  (2, true, 17*60, 21*60+30, 'migracao', 'Eduardo (21/11)'),
  (3, true, 17*60, 21*60+30, 'migracao', 'Eduardo (21/11)'),
  (4, true, 17*60, 21*60+30, 'migracao', 'Eduardo (21/11)'),
  (5, true, 18*60, 23*60,    'migracao', 'Eduardo (21/11)'),
  (6, true, 18*60, 23*60,    'migracao', 'Eduardo (21/11)')
on conflict (dia) do nothing;

-- ── 2. datas fechadas (feriado, evento, folga) ──────────────────────────────
create table if not exists public.loja_fechada (
  data            date primary key,
  motivo          text,
  atualizado_em   timestamptz not null default now(),
  atualizado_por  text,
  atualizado_nome text
);
insert into public.loja_fechada (data, motivo, atualizado_por, atualizado_nome) values
  ('2026-12-24', 'Véspera de Natal', 'migracao', 'Eduardo (21/11)'),
  ('2026-12-25', 'Natal',            'migracao', 'Eduardo (21/11)'),
  ('2026-12-31', 'Véspera de Ano-Novo', 'migracao', 'Eduardo (21/11)'),
  ('2027-01-01', 'Ano-Novo',         'migracao', 'Eduardo (21/11)')
on conflict (data) do nothing;

-- ── 3 + 4. estado da loja: pausa manual + aviso no topo do app (linha única) ─
create table if not exists public.loja_estado (
  id              smallint primary key default 1 check (id = 1),
  pausada         boolean not null default false,
  pausa_motivo    text check (char_length(pausa_motivo) <= 140),
  pausada_em      timestamptz,
  aviso_ativo     boolean not null default false,
  aviso_texto     text check (char_length(aviso_texto) <= 160),
  atualizado_em   timestamptz not null default now(),
  atualizado_por  text,
  atualizado_nome text
);
insert into public.loja_estado (id, atualizado_por, atualizado_nome) values (1, 'migracao', 'Eduardo (21/11)')
on conflict (id) do nothing;

-- ── 6. cardápio: carimbo de quem mudou preço/disponibilidade (colunas novas) ─
alter table public.produtos add column if not exists atualizado_em   timestamptz;
alter table public.produtos add column if not exists atualizado_por  text;
alter table public.produtos add column if not exists atualizado_nome text;

-- ── triggers ────────────────────────────────────────────────────────────────
drop trigger if exists trg_carimbo on public.loja_horario;
create trigger trg_carimbo before insert or update on public.loja_horario for each row execute function public.carimbar_mudanca();
drop trigger if exists trg_carimbo on public.loja_fechada;
create trigger trg_carimbo before insert or update on public.loja_fechada for each row execute function public.carimbar_mudanca();
drop trigger if exists trg_carimbo on public.loja_estado;
create trigger trg_carimbo before insert or update on public.loja_estado for each row execute function public.carimbar_mudanca();
drop trigger if exists trg_carimbo_admin on public.produtos;
create trigger trg_carimbo_admin before update on public.produtos for each row
  when (old.preco is distinct from new.preco or old.ativo is distinct from new.ativo)
  execute function public.carimbar_mudanca();

drop trigger if exists trg_log on public.loja_horario;
create trigger trg_log after insert or update or delete on public.loja_horario for each row execute function public.registrar_mudanca();
drop trigger if exists trg_log on public.loja_fechada;
create trigger trg_log after insert or update or delete on public.loja_fechada for each row execute function public.registrar_mudanca();
drop trigger if exists trg_log on public.loja_estado;
create trigger trg_log after insert or update or delete on public.loja_estado for each row execute function public.registrar_mudanca();
drop trigger if exists trg_log_admin on public.produtos;
create trigger trg_log_admin after update on public.produtos for each row
  when (old.preco is distinct from new.preco or old.ativo is distinct from new.ativo)
  execute function public.registrar_mudanca();

-- ── segurança: cliente lê horário/datas/estado; só equipe muda ──────────────
alter table public.equipe       enable row level security;
alter table public.admin_log    enable row level security;
alter table public.loja_horario enable row level security;
alter table public.loja_fechada enable row level security;
alter table public.loja_estado  enable row level security;

grant select on public.loja_horario, public.loja_fechada, public.loja_estado to anon, authenticated;
grant update (aberto, abre_min, fecha_min, atualizado_nome) on public.loja_horario to authenticated;
grant insert, update, delete on public.loja_fechada to authenticated;
grant update (pausada, pausa_motivo, pausada_em, aviso_ativo, aviso_texto, atualizado_nome) on public.loja_estado to authenticated;
grant select on public.equipe, public.admin_log to authenticated;
grant all on public.equipe, public.admin_log, public.loja_horario, public.loja_fechada, public.loja_estado to service_role;
grant usage on sequence public.admin_log_id_seq to service_role;

drop policy if exists loja_horario_ler on public.loja_horario;
create policy loja_horario_ler on public.loja_horario for select to anon, authenticated using (true);
drop policy if exists loja_horario_equipe on public.loja_horario;
create policy loja_horario_equipe on public.loja_horario for update to authenticated using (eh_equipe2()) with check (eh_equipe2());

drop policy if exists loja_fechada_ler on public.loja_fechada;
create policy loja_fechada_ler on public.loja_fechada for select to anon, authenticated using (true);
drop policy if exists loja_fechada_equipe on public.loja_fechada;
create policy loja_fechada_equipe on public.loja_fechada for all to authenticated using (eh_equipe2()) with check (eh_equipe2());

drop policy if exists loja_estado_ler on public.loja_estado;
create policy loja_estado_ler on public.loja_estado for select to anon, authenticated using (true);
drop policy if exists loja_estado_equipe on public.loja_estado;
create policy loja_estado_equipe on public.loja_estado for update to authenticated using (eh_equipe2()) with check (eh_equipe2());

drop policy if exists equipe_ler on public.equipe;
create policy equipe_ler on public.equipe for select to authenticated using (eh_equipe2());
drop policy if exists admin_log_ler on public.admin_log;
create policy admin_log_ler on public.admin_log for select to authenticated using (eh_equipe2());

-- cardápio (o SQL de 23/10 nunca tinha rodado: sem ele o botão de preço do painel falha).
-- Mesmo desenho, com eh_equipe2() (superconjunto) e a coluna de nome do carimbo.
drop policy if exists produtos_equipe_edita on public.produtos;
create policy produtos_equipe_edita on public.produtos for update to authenticated using (eh_equipe2()) with check (eh_equipe2());
grant update (ativo, preco, atualizado_nome) on public.produtos to authenticated;

commit;
notify pgrst, 'reload schema';
